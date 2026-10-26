from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.market import NewsArticle
from app.schemas.market import (
    QuoteResponse, NewsArticleResponse, AnomalyInjectionRequest, PriceHistoryResponse
)
from app.services.market_data import market_data_provider

router = APIRouter(prefix="/market", tags=["Market Data & Ingestion"])

@router.get("/quotes", response_model=List[QuoteResponse])
def get_quotes(db: Session = Depends(get_db)):
    return market_data_provider.get_all_quotes(db)

@router.get("/quotes/{ticker}", response_model=QuoteResponse)
def get_single_quote(ticker: str, db: Session = Depends(get_db)):
    quote = market_data_provider.get_quote(ticker, db)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote for ticker '{ticker}' not found"
        )
    return quote

@router.get("/history/{ticker}", response_model=PriceHistoryResponse)
def get_price_history(ticker: str, period: str = "30d", db: Session = Depends(get_db)):
    """FR-06: Historical price / candle series for charting and technical analysis."""
    try:
        return market_data_provider.get_history(ticker=ticker, period=period, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/anomalies/inject", response_model=QuoteResponse)
def inject_market_anomaly(req: AnomalyInjectionRequest, db: Session = Depends(get_db)):
    quote = market_data_provider.inject_anomaly(req, db)
    from app.services.trading_engine import trading_engine
    trading_engine.match_pending_limit_orders(db, req.ticker.upper(), quote["price"])
    return quote

@router.get("/news", response_model=List[NewsArticleResponse])
def get_news_articles(db: Session = Depends(get_db)):
    articles = db.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(20).all()
    return articles
