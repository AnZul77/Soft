from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding, PortfolioType, CashTransaction
from app.models.order import TradeOrder, OrderStatus, OrderSide
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioValuation, ValuationHolding, HoldingCreate, HoldingUpdate
)
from app.services.market_data import market_data_provider
from app.services.audit_service import log_audit_event

class PortfolioService:
    def create_portfolio(self, db: Session, user_id: str, data: PortfolioCreate) -> Portfolio:
        initial_cash = data.initial_cash if data.type == PortfolioType.VIRTUAL_TRADING else 0.0
        portfolio = Portfolio(
            user_id=user_id,
            name=data.name,
            type=data.type,
            virtual_cash_balance=initial_cash,
            reserved_cash=0.0
        )
        db.add(portfolio)
        db.flush()

        if data.type == PortfolioType.VIRTUAL_TRADING and initial_cash > 0:
            tx = CashTransaction(
                portfolio_id=portfolio.id,
                amount=initial_cash,
                balance_after=initial_cash,
                transaction_type="INITIAL_DEPOSIT",
                description="Initial funding deposit for simulated paper trading"
            )
            db.add(tx)

        log_audit_event(
            db=db,
            user_id=user_id,
            action="PORTFOLIO_CREATED",
            resource_type="PORTFOLIO",
            resource_id=portfolio.id,
            details=f"Created {data.type} portfolio '{data.name}' with initial cash ${initial_cash:,.2f}"
        )

        db.commit()
        db.refresh(portfolio)
        return portfolio

    def get_user_portfolios(self, db: Session, user_id: str, include_inactive: bool = False) -> List[Portfolio]:
        query = db.query(Portfolio).filter(Portfolio.user_id == user_id)
        if not include_inactive:
            query = query.filter(Portfolio.is_active == True)
        return query.all()

    def get_portfolio(self, db: Session, user_id: str, portfolio_id: str) -> Portfolio:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or access denied"
            )
        return portfolio

    def update_portfolio(self, db: Session, user_id: str, portfolio_id: str, data: PortfolioUpdate) -> Portfolio:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        if data.name is not None:
            portfolio.name = data.name
        if data.is_active is not None:
            portfolio.is_active = data.is_active
        db.commit()
        db.refresh(portfolio)

        log_audit_event(
            db=db,
            user_id=user_id,
            action="PORTFOLIO_UPDATED",
            resource_type="PORTFOLIO",
            resource_id=portfolio.id,
            details=f"Updated portfolio: name={portfolio.name}, is_active={portfolio.is_active}"
        )
        return portfolio

    def delete_portfolio(self, db: Session, user_id: str, portfolio_id: str) -> bool:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        portfolio.is_active = False

        # Cancel any pending limit orders to release escrow and maintain ledger invariants
        pending_orders = db.query(TradeOrder).filter(
            TradeOrder.portfolio_id == portfolio.id,
            TradeOrder.status == OrderStatus.PENDING
        ).all()

        for order in pending_orders:
            if order.side == OrderSide.BUY and order.limit_price:
                refund = round(order.quantity * order.limit_price, 2)
                portfolio.reserved_cash = max(0.0, round(portfolio.reserved_cash - refund, 2))
                portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + refund, 2)
                tx = CashTransaction(
                    portfolio_id=portfolio.id,
                    order_id=order.id,
                    amount=refund,
                    balance_after=portfolio.virtual_cash_balance,
                    transaction_type="ESCROW_REFUND",
                    description=f"Escrow refund upon portfolio deletion for Limit BUY {order.quantity} {order.ticker}"
                )
                db.add(tx)
            order.status = OrderStatus.CANCELLED
            order.error_reason = "Cancelled due to portfolio deletion"
            log_audit_event(
                db=db,
                user_id=user_id,
                action="TRADE_ORDER_CANCELLED",
                resource_type="ORDER",
                resource_id=order.id,
                details=f"Auto-cancelled pending order {order.id} upon portfolio deletion"
            )

        db.commit()

        log_audit_event(
            db=db,
            user_id=user_id,
            action="PORTFOLIO_DELETED",
            resource_type="PORTFOLIO",
            resource_id=portfolio_id,
            details=f"Soft deleted portfolio {portfolio.name} (preserved ledger orders and cash transactions)"
        )
        return True

    def add_holding_manual(self, db: Session, user_id: str, portfolio_id: str, data: HoldingCreate) -> Holding:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        if not portfolio.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify holdings of an inactive/deleted portfolio"
            )
        if portfolio.type != PortfolioType.MANUAL_TRACKING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual holding modification is only permitted on MANUAL_TRACKING portfolios. "
                       "Virtual trading portfolios modify holdings exclusively via Trade Orders."
            )

        ticker = data.ticker.upper()
        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.ticker == ticker
        ).first()

        if existing:
            # Update weighted average cost basis
            total_cost = (existing.quantity * existing.cost_basis) + (data.quantity * data.cost_basis)
            total_qty = existing.quantity + data.quantity
            existing.quantity = total_qty
            existing.cost_basis = round(total_cost / total_qty, 4)
            db.commit()
            db.refresh(existing)
            return existing

        holding = Holding(
            portfolio_id=portfolio_id,
            ticker=ticker,
            quantity=data.quantity,
            cost_basis=data.cost_basis
        )
        db.add(holding)
        db.commit()
        db.refresh(holding)
        return holding

    def update_holding_manual(self, db: Session, user_id: str, portfolio_id: str, holding_id: str, data: HoldingUpdate) -> Holding:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        if not portfolio.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify holdings of an inactive/deleted portfolio"
            )
        if portfolio.type != PortfolioType.MANUAL_TRACKING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual holding modification is forbidden on VIRTUAL_TRADING portfolios."
            )

        holding = db.query(Holding).filter(
            Holding.id == holding_id,
            Holding.portfolio_id == portfolio_id
        ).first()
        if not holding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

        if data.quantity is not None:
            holding.quantity = data.quantity
        if data.cost_basis is not None:
            holding.cost_basis = data.cost_basis

        db.commit()
        db.refresh(holding)
        return holding

    def delete_holding_manual(self, db: Session, user_id: str, portfolio_id: str, holding_id: str) -> bool:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        if not portfolio.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify holdings of an inactive/deleted portfolio"
            )
        if portfolio.type != PortfolioType.MANUAL_TRACKING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual holding deletion is forbidden on VIRTUAL_TRADING portfolios."
            )

        holding = db.query(Holding).filter(
            Holding.id == holding_id,
            Holding.portfolio_id == portfolio_id
        ).first()
        if not holding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

        db.delete(holding)
        db.commit()
        return True

    def calculate_valuation(self, db: Session, user_id: str, portfolio_id: str) -> PortfolioValuation:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        valuation_holdings: List[ValuationHolding] = []
        total_holdings_value = 0.0
        total_cost = 0.0

        raw_calc = []
        for h in holdings:
            quote = market_data_provider.get_quote(h.ticker, db)
            price_source = "LIVE"
            is_stale = False

            if quote and quote.get("price"):
                current_price = float(quote["price"])
                is_stale = quote.get("is_stale", False)
                price_source = quote.get("source", "LIVE")
            elif quote and quote.get("previous_close"):
                current_price = float(quote["previous_close"])
                is_stale = True
                price_source = "PREV_CLOSE_FALLBACK"
            else:
                # PRD Problem 6: fallback to cost_basis with is_stale: True
                current_price = float(h.cost_basis)
                is_stale = True
                price_source = "COST_BASIS_FALLBACK"

            market_val = round(h.quantity * current_price, 2)
            cost_val = round(h.quantity * h.cost_basis, 2)
            unrealized_pl = round(market_val - cost_val, 2)
            unrealized_pl_pct = round((unrealized_pl / cost_val) * 100, 2) if cost_val > 0 else 0.0

            total_holdings_value += market_val
            total_cost += cost_val

            raw_calc.append({
                "holding_id": h.id,
                "ticker": h.ticker,
                "quantity": h.quantity,
                "cost_basis": h.cost_basis,
                "current_price": current_price,
                "market_value": market_val,
                "unrealized_pl": unrealized_pl,
                "unrealized_pl_pct": unrealized_pl_pct,
                "is_stale": is_stale,
                "price_source": price_source
            })

        # Calculate weighting relative to total holdings value (or total equity)
        total_equity = round(total_holdings_value + portfolio.virtual_cash_balance + portfolio.reserved_cash, 2)
        base_divisor = total_holdings_value if total_holdings_value > 0 else 1.0

        for r in raw_calc:
            weight_pct = round((r["market_value"] / base_divisor) * 100, 2) if total_holdings_value > 0 else 0.0
            valuation_holdings.append(ValuationHolding(
                holding_id=r["holding_id"],
                ticker=r["ticker"],
                quantity=r["quantity"],
                cost_basis=r["cost_basis"],
                current_price=r["current_price"],
                market_value=r["market_value"],
                unrealized_pl=r["unrealized_pl"],
                unrealized_pl_pct=r["unrealized_pl_pct"],
                weight_pct=weight_pct,
                is_stale=r["is_stale"],
                price_source=r["price_source"]
            ))

        total_unrealized_pl = round(total_holdings_value - total_cost, 2)
        total_unrealized_pl_pct = round((total_unrealized_pl / total_cost) * 100, 2) if total_cost > 0 else 0.0

        return PortfolioValuation(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            portfolio_type=portfolio.type,
            base_currency=portfolio.base_currency,
            total_equity=total_equity,
            holdings_value=round(total_holdings_value, 2),
            virtual_cash_balance=round(portfolio.virtual_cash_balance, 2),
            reserved_cash=round(portfolio.reserved_cash, 2),
            total_unrealized_pl=total_unrealized_pl,
            total_unrealized_pl_pct=total_unrealized_pl_pct,
            holdings=valuation_holdings,
            valuation_time=datetime.now(timezone.utc)
        )

portfolio_service = PortfolioService()
