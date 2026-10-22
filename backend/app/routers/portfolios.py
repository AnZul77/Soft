from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioResponse, PortfolioValuation,
    HoldingCreate, HoldingUpdate, HoldingResponse
)
from app.services.auth_service import get_current_user
from app.services.portfolio_service import portfolio_service

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.create_portfolio(db, current_user.id, portfolio_in)

@router.get("/", response_model=List[PortfolioResponse])
def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.get_user_portfolios(db, current_user.id)

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.get_portfolio(db, current_user.id, portfolio_id)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio_service.delete_portfolio(db, current_user.id, portfolio_id)
    return None

@router.get("/{portfolio_id}/valuation", response_model=PortfolioValuation)
def get_portfolio_valuation(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.calculate_valuation(db, current_user.id, portfolio_id)

@router.post("/{portfolio_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def add_manual_holding(
    portfolio_id: str,
    holding_in: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.add_holding_manual(db, current_user.id, portfolio_id, holding_in)

@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingResponse)
def update_manual_holding(
    portfolio_id: str,
    holding_id: str,
    holding_in: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return portfolio_service.update_holding_manual(db, current_user.id, portfolio_id, holding_id, holding_in)

@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manual_holding(
    portfolio_id: str,
    holding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio_service.delete_holding_manual(db, current_user.id, portfolio_id, holding_id)
    return None
