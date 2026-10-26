from datetime import datetime, timezone
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding, CashTransaction, PortfolioType
from app.models.order import TradeOrder, OrderSide, OrderType, OrderStatus
from app.schemas.order import OrderCreate
from app.services.market_data import market_data_provider
from app.services.audit_service import log_audit_event

class TradingEngine:
    def execute_order(
        self,
        db: Session,
        user_id: str,
        portfolio_id: str,
        order_data: OrderCreate,
        idempotency_key: Optional[str] = None
    ) -> TradeOrder:
        # Check idempotency first (PRD Problem 7)
        if idempotency_key:
            existing_order = db.query(TradeOrder).filter(
                TradeOrder.idempotency_key == idempotency_key
            ).first()
            if existing_order:
                return existing_order

        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).with_for_update().first() if db.bind.dialect.name != "sqlite" else db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()

        if not portfolio or not portfolio.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found, inactive, or access denied"
            )

        if portfolio.type != PortfolioType.VIRTUAL_TRADING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Simulated trading is only permitted on VIRTUAL_TRADING accounts."
            )

        ticker = order_data.ticker.upper()
        quote = market_data_provider.get_quote(ticker, db)
        if not quote or quote.get("price") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to retrieve market quote for ticker {ticker}"
            )
        current_price = float(quote["price"])

        order = TradeOrder(
            portfolio_id=portfolio_id,
            ticker=ticker,
            side=order_data.side,
            type=order_data.type,
            quantity=order_data.quantity,
            limit_price=order_data.limit_price,
            idempotency_key=idempotency_key,
            status=OrderStatus.PENDING
        )
        db.add(order)
        db.flush()

        if order_data.type == OrderType.MARKET:
            self._fill_market_order(db, portfolio, order, current_price)
        elif order_data.type == OrderType.LIMIT:
            self._process_limit_order(db, portfolio, order, current_price)

        log_audit_event(
            db=db,
            user_id=user_id,
            action="TRADE_ORDER_PLACED",
            resource_type="ORDER",
            resource_id=order.id,
            details=f"Placed {order.type} {order.side} order for {order.quantity} {order.ticker} (Status: {order.status})"
        )

        db.commit()
        db.refresh(order)
        return order

    def _fill_market_order(self, db: Session, portfolio: Portfolio, order: TradeOrder, execution_price: float):
        qty = order.quantity
        total_cost = round(qty * execution_price, 2)
        now = datetime.now(timezone.utc)

        if order.side == OrderSide.BUY:
            # Strict cash invariant
            if portfolio.virtual_cash_balance < total_cost:
                order.status = OrderStatus.REJECTED
                order.error_reason = f"Insufficient cash: Required ${total_cost:.2f}, Available ${portfolio.virtual_cash_balance:.2f}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=order.error_reason
                )

            # Deduct cash atomically
            portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance - total_cost, 2)
            tx = CashTransaction(
                portfolio_id=portfolio.id,
                order_id=order.id,
                amount=-total_cost,
                balance_after=portfolio.virtual_cash_balance,
                transaction_type="BUY_ORDER",
                description=f"Market BUY {qty} shares of {order.ticker} @ ${execution_price:.2f}"
            )
            db.add(tx)

            # Update holding position
            holding = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.ticker == order.ticker
            ).first()

            if holding:
                total_shares = holding.quantity + qty
                new_cost_basis = ((holding.quantity * holding.cost_basis) + (qty * execution_price)) / total_shares
                holding.quantity = total_shares
                holding.cost_basis = round(new_cost_basis, 4)
            else:
                holding = Holding(
                    portfolio_id=portfolio.id,
                    ticker=order.ticker,
                    quantity=qty,
                    cost_basis=execution_price
                )
                db.add(holding)

            order.status = OrderStatus.FILLED
            order.execution_price = execution_price
            order.executed_at = now

        elif order.side == OrderSide.SELL:
            holding = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.ticker == order.ticker
            ).first()

            pending_sells = db.query(TradeOrder).filter(
                TradeOrder.portfolio_id == portfolio.id,
                TradeOrder.ticker == order.ticker,
                TradeOrder.status == OrderStatus.PENDING,
                TradeOrder.side == OrderSide.SELL,
                TradeOrder.id != order.id
            ).all()
            committed_limit_sell_qty = sum(o.quantity for o in pending_sells)
            available_qty = (holding.quantity - committed_limit_sell_qty) if holding else 0.0

            if not holding or available_qty < qty:
                order.status = OrderStatus.REJECTED
                order.error_reason = f"Insufficient shares to sell: Requested {qty}, Available {available_qty} (Committed to limit orders: {committed_limit_sell_qty})"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=order.error_reason
                )

            # Increase cash
            portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + total_cost, 2)
            tx = CashTransaction(
                portfolio_id=portfolio.id,
                order_id=order.id,
                amount=total_cost,
                balance_after=portfolio.virtual_cash_balance,
                transaction_type="SELL_ORDER",
                description=f"Market SELL {qty} shares of {order.ticker} @ ${execution_price:.2f}"
            )
            db.add(tx)

            # Deduct or remove holding
            if holding.quantity == qty:
                db.delete(holding)
            else:
                holding.quantity = round(holding.quantity - qty, 4)

            order.status = OrderStatus.FILLED
            order.execution_price = execution_price
            order.executed_at = now

    def _process_limit_order(self, db: Session, portfolio: Portfolio, order: TradeOrder, current_price: float):
        qty = order.quantity
        limit_price = order.limit_price

        if order.side == OrderSide.BUY:
            required_escrow = round(qty * limit_price, 2)
            if portfolio.virtual_cash_balance < required_escrow:
                order.status = OrderStatus.REJECTED
                order.error_reason = f"Insufficient cash for limit escrow: Required ${required_escrow:.2f}, Available ${portfolio.virtual_cash_balance:.2f}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=order.error_reason)

            # Move funds to reserved cash (Escrow pattern - PRD Problem 4)
            portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance - required_escrow, 2)
            portfolio.reserved_cash = round(portfolio.reserved_cash + required_escrow, 2)

            tx = CashTransaction(
                portfolio_id=portfolio.id,
                order_id=order.id,
                amount=-required_escrow,
                balance_after=portfolio.virtual_cash_balance,
                transaction_type="ESCROW_RESERVE",
                description=f"Escrow lock for Limit BUY {qty} {order.ticker} @ ${limit_price:.2f}"
            )
            db.add(tx)

            # Check if immediately fillable
            if current_price <= limit_price:
                actual_cost = round(qty * current_price, 2)
                refund = round(required_escrow - actual_cost, 2)

                portfolio.reserved_cash = round(portfolio.reserved_cash - required_escrow, 2)
                if refund > 0:
                    portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + refund, 2)
                    refund_tx = CashTransaction(
                        portfolio_id=portfolio.id,
                        order_id=order.id,
                        amount=refund,
                        balance_after=portfolio.virtual_cash_balance,
                        transaction_type="ESCROW_REFUND",
                        description=f"Price improvement refund for Limit BUY {order.ticker}: saved ${refund:.2f}"
                    )
                    db.add(refund_tx)

                # Add holding
                holding = db.query(Holding).filter(
                    Holding.portfolio_id == portfolio.id,
                    Holding.ticker == order.ticker
                ).first()

                if holding:
                    total_shares = holding.quantity + qty
                    new_cost_basis = ((holding.quantity * holding.cost_basis) + actual_cost) / total_shares
                    holding.quantity = total_shares
                    holding.cost_basis = round(new_cost_basis, 4)
                else:
                    db.add(Holding(
                        portfolio_id=portfolio.id,
                        ticker=order.ticker,
                        quantity=qty,
                        cost_basis=current_price
                    ))

                order.status = OrderStatus.FILLED
                order.execution_price = current_price
                order.executed_at = datetime.now(timezone.utc)

        elif order.side == OrderSide.SELL:
            holding = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.ticker == order.ticker
            ).first()

            pending_sells = db.query(TradeOrder).filter(
                TradeOrder.portfolio_id == portfolio.id,
                TradeOrder.ticker == order.ticker,
                TradeOrder.status == OrderStatus.PENDING,
                TradeOrder.side == OrderSide.SELL,
                TradeOrder.id != order.id
            ).all()
            committed_qty = sum(o.quantity for o in pending_sells)
            available_qty = (holding.quantity - committed_qty) if holding else 0.0

            if available_qty < qty:
                order.status = OrderStatus.REJECTED
                order.error_reason = f"Insufficient available shares for limit sell: Requested {qty}, Available {available_qty}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=order.error_reason)

            # Check if immediately fillable
            if current_price >= limit_price:
                proceeds = round(qty * current_price, 2)
                portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + proceeds, 2)
                tx = CashTransaction(
                    portfolio_id=portfolio.id,
                    order_id=order.id,
                    amount=proceeds,
                    balance_after=portfolio.virtual_cash_balance,
                    transaction_type="SELL_ORDER",
                    description=f"Limit SELL triggered: {qty} {order.ticker} @ ${current_price:.2f}"
                )
                db.add(tx)

                if holding.quantity == qty:
                    db.delete(holding)
                else:
                    holding.quantity = round(holding.quantity - qty, 4)

                order.status = OrderStatus.FILLED
                order.execution_price = current_price
                order.executed_at = datetime.now(timezone.utc)

    def cancel_order(self, db: Session, user_id: str, portfolio_id: str, order_id: str) -> TradeOrder:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found or access denied")

        order = db.query(TradeOrder).filter(
            TradeOrder.id == order_id,
            TradeOrder.portfolio_id == portfolio_id
        ).first()

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status}"
            )

        # Refund escrow if BUY limit order
        if order.side == OrderSide.BUY and order.type == OrderType.LIMIT:
            refund_amount = round(order.quantity * order.limit_price, 2)
            portfolio.reserved_cash = max(0.0, round(portfolio.reserved_cash - refund_amount, 2))
            portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + refund_amount, 2)

            tx = CashTransaction(
                portfolio_id=portfolio.id,
                order_id=order.id,
                amount=refund_amount,
                balance_after=portfolio.virtual_cash_balance,
                transaction_type="ESCROW_REFUND",
                description=f"Refund from cancelled limit order for {order.ticker}"
            )
            db.add(tx)

        order.status = OrderStatus.CANCELLED
        log_audit_event(
            db=db,
            user_id=user_id,
            action="TRADE_ORDER_CANCELLED",
            resource_type="ORDER",
            resource_id=order.id,
            details=f"Cancelled {order.type} {order.side} order for {order.quantity} {order.ticker}"
        )
        db.commit()
        db.refresh(order)
        return order

    def get_portfolio_orders(self, db: Session, user_id: str, portfolio_id: str) -> List[TradeOrder]:
        # Validate ownership (PRD Multi-Tenancy Isolation)
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or access denied"
            )
        return db.query(TradeOrder).filter(
            TradeOrder.portfolio_id == portfolio_id
        ).order_by(TradeOrder.created_at.desc()).all()

    def get_portfolio_transactions(self, db: Session, user_id: str, portfolio_id: str) -> List[CashTransaction]:
        # Validate ownership (PRD Multi-Tenancy Isolation)
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or access denied"
            )
        return db.query(CashTransaction).filter(
            CashTransaction.portfolio_id == portfolio_id
        ).order_by(CashTransaction.created_at.desc()).all()

    def match_pending_limit_orders(self, db: Session, ticker: str, current_price: float) -> List[TradeOrder]:
        """
        Evaluates pending limit orders for a ticker against new market price tick.
        Resolves PRD Problem 4 (Limit Order Lifecycle Matching Engine).
        """
        ticker = ticker.upper()
        pending_orders = db.query(TradeOrder).filter(
            TradeOrder.ticker == ticker,
            TradeOrder.status == OrderStatus.PENDING,
            TradeOrder.type == OrderType.LIMIT
        ).all()

        filled_orders = []
        modified_orders = []
        now = datetime.now(timezone.utc)

        for order in pending_orders:
            portfolio = db.query(Portfolio).filter(Portfolio.id == order.portfolio_id).first()
            if not portfolio or not portfolio.is_active:
                if portfolio and order.side == OrderSide.BUY and order.limit_price:
                    refund = round(order.quantity * order.limit_price, 2)
                    portfolio.reserved_cash = max(0.0, round(portfolio.reserved_cash - refund, 2))
                    portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + refund, 2)
                    tx = CashTransaction(
                        portfolio_id=portfolio.id,
                        order_id=order.id,
                        amount=refund,
                        balance_after=portfolio.virtual_cash_balance,
                        transaction_type="ESCROW_REFUND",
                        description=f"Escrow release for pending Limit BUY on inactive portfolio ({order.quantity} {order.ticker})"
                    )
                    db.add(tx)
                order.status = OrderStatus.CANCELLED
                order.error_reason = "Portfolio deleted or inactive"
                modified_orders.append(order)
                continue

            if order.side == OrderSide.BUY:
                if current_price <= order.limit_price:
                    qty = order.quantity
                    limit_price = order.limit_price
                    required_escrow = round(qty * limit_price, 2)
                    actual_cost = round(qty * current_price, 2)
                    refund = round(required_escrow - actual_cost, 2)

                    portfolio.reserved_cash = max(0.0, round(portfolio.reserved_cash - required_escrow, 2))
                    if refund > 0:
                        portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + refund, 2)
                        refund_tx = CashTransaction(
                            portfolio_id=portfolio.id,
                            order_id=order.id,
                            amount=refund,
                            balance_after=portfolio.virtual_cash_balance,
                            transaction_type="ESCROW_REFUND",
                            description=f"Price improvement refund for Limit BUY {order.ticker}: saved ${refund:.2f}"
                        )
                        db.add(refund_tx)

                    # Update holding
                    holding = db.query(Holding).filter(
                        Holding.portfolio_id == portfolio.id,
                        Holding.ticker == order.ticker
                    ).first()

                    if holding:
                        total_shares = holding.quantity + qty
                        new_cost_basis = ((holding.quantity * holding.cost_basis) + actual_cost) / total_shares
                        holding.quantity = total_shares
                        holding.cost_basis = round(new_cost_basis, 4)
                    else:
                        db.add(Holding(
                            portfolio_id=portfolio.id,
                            ticker=order.ticker,
                            quantity=qty,
                            cost_basis=current_price
                        ))

                    order.status = OrderStatus.FILLED
                    order.execution_price = current_price
                    order.executed_at = now
                    filled_orders.append(order)
                    modified_orders.append(order)

                    log_audit_event(
                        db=db,
                        user_id=portfolio.user_id,
                        action="TRADE_ORDER_FILLED",
                        resource_type="ORDER",
                        resource_id=order.id,
                        details=f"Limit BUY order filled for {order.quantity} {order.ticker} @ ${current_price:.2f}"
                    )

            elif order.side == OrderSide.SELL:
                if current_price >= order.limit_price:
                    qty = order.quantity
                    holding = db.query(Holding).filter(
                        Holding.portfolio_id == portfolio.id,
                        Holding.ticker == order.ticker
                    ).first()

                    if not holding or holding.quantity < qty:
                        order.status = OrderStatus.REJECTED
                        order.error_reason = "Insufficient shares to fulfill limit sell at execution time"
                        modified_orders.append(order)
                        log_audit_event(
                            db=db,
                            user_id=portfolio.user_id,
                            action="TRADE_ORDER_REJECTED",
                            resource_type="ORDER",
                            resource_id=order.id,
                            details=f"Limit SELL order rejected: insufficient shares at execution time ({order.quantity} {order.ticker})"
                        )
                        continue

                    proceeds = round(qty * current_price, 2)
                    portfolio.virtual_cash_balance = round(portfolio.virtual_cash_balance + proceeds, 2)
                    tx = CashTransaction(
                        portfolio_id=portfolio.id,
                        order_id=order.id,
                        amount=proceeds,
                        balance_after=portfolio.virtual_cash_balance,
                        transaction_type="SELL_ORDER",
                        description=f"Limit SELL triggered: {qty} {order.ticker} @ ${current_price:.2f}"
                    )
                    db.add(tx)

                    if holding.quantity == qty:
                        db.delete(holding)
                    else:
                        holding.quantity = round(holding.quantity - qty, 4)

                    order.status = OrderStatus.FILLED
                    order.execution_price = current_price
                    order.executed_at = now
                    filled_orders.append(order)
                    modified_orders.append(order)

                    log_audit_event(
                        db=db,
                        user_id=portfolio.user_id,
                        action="TRADE_ORDER_FILLED",
                        resource_type="ORDER",
                        resource_id=order.id,
                        details=f"Limit SELL order filled for {order.quantity} {order.ticker} @ ${current_price:.2f}"
                    )

        if modified_orders:
            db.commit()
            for o in modified_orders:
                db.refresh(o)

        return filled_orders

    def match_all_pending_orders(self, db: Session, ticker: Optional[str] = None) -> List[TradeOrder]:
        """Matches pending limit orders across all or specific tickers."""
        if ticker:
            quote = market_data_provider.get_quote(ticker, db)
            if quote and quote.get("price"):
                return self.match_pending_limit_orders(db, ticker, float(quote["price"]))
            return []

        pending_tickers = db.query(TradeOrder.ticker).filter(
            TradeOrder.status == OrderStatus.PENDING,
            TradeOrder.type == OrderType.LIMIT
        ).distinct().all()

        all_filled = []
        for (t,) in pending_tickers:
            quote = market_data_provider.get_quote(t, db)
            if quote and quote.get("price"):
                filled = self.match_pending_limit_orders(db, t, float(quote["price"]))
                all_filled.extend(filled)
        return all_filled

trading_engine = TradingEngine()
