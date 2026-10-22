from typing import List, Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, CashTransactionResponse
from app.services.auth_service import get_current_user
from app.services.trading_engine import trading_engine

router = APIRouter(prefix="/trading", tags=["Simulated Trading"])

@router.post("/{portfolio_id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    portfolio_id: str,
    order_in: OrderCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return trading_engine.execute_order(
        db=db,
        user_id=current_user.id,
        portfolio_id=portfolio_id,
        order_data=order_in,
        idempotency_key=idempotency_key
    )

@router.get("/{portfolio_id}/orders", response_model=List[OrderResponse])
def get_orders(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return trading_engine.get_portfolio_orders(db, current_user.id, portfolio_id)

@router.post("/{portfolio_id}/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    portfolio_id: str,
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return trading_engine.cancel_order(db, current_user.id, portfolio_id, order_id)

@router.get("/{portfolio_id}/transactions", response_model=List[CashTransactionResponse])
def get_cash_transactions(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return trading_engine.get_portfolio_transactions(db, current_user.id, portfolio_id)

@router.post("/match-orders", response_model=List[OrderResponse])
def match_orders(
    ticker: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Triggers limit order matching against current market quotes."""
    return trading_engine.match_all_pending_orders(db, ticker=ticker)
