from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding, PortfolioType, CashTransaction
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioValuation, ValuationHolding, HoldingCreate, HoldingUpdate
)
from app.services.market_data import market_data_provider

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

        db.commit()
        db.refresh(portfolio)
        return portfolio

    def get_user_portfolios(self, db: Session, user_id: str) -> List[Portfolio]:
        return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

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

    def delete_portfolio(self, db: Session, user_id: str, portfolio_id: str) -> bool:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        db.delete(portfolio)
        db.commit()
        return True

    def add_holding_manual(self, db: Session, user_id: str, portfolio_id: str, data: HoldingCreate) -> Holding:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
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
