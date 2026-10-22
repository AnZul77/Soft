from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.journal import InvestmentJournalEntry
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse
)
from app.services.auth_service import get_current_user
from app.services.market_data import market_data_provider
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/journal", tags=["Investment Journal"])

@router.post("/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    entry_in: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if entry_in.portfolio_id:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == entry_in.portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or access denied"
            )

    entry = InvestmentJournalEntry(
        user_id=current_user.id,
        portfolio_id=entry_in.portfolio_id,
        ticker=entry_in.ticker.upper(),
        thesis_title=entry_in.thesis_title,
        thesis_content=entry_in.thesis_content,
        rationale=entry_in.rationale,
        target_price=entry_in.target_price,
        confidence_rating=entry_in.confidence_rating,
        review_date=entry_in.review_date
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/", response_model=List[JournalEntryResponse])
def get_user_journal_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(InvestmentJournalEntry).filter(
        InvestmentJournalEntry.user_id == current_user.id
    ).order_by(InvestmentJournalEntry.created_at.desc()).all()

@router.get("/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(InvestmentJournalEntry).filter(
        InvestmentJournalEntry.id == entry_id,
        InvestmentJournalEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    return entry

@router.put("/{entry_id}", response_model=JournalEntryResponse)
def update_journal_entry(
    entry_id: str,
    entry_in: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(InvestmentJournalEntry).filter(
        InvestmentJournalEntry.id == entry_id,
        InvestmentJournalEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")

    if entry_in.thesis_title is not None:
        entry.thesis_title = entry_in.thesis_title
    if entry_in.thesis_content is not None:
        entry.thesis_content = entry_in.thesis_content
    if entry_in.rationale is not None:
        entry.rationale = entry_in.rationale
    if entry_in.target_price is not None:
        entry.target_price = entry_in.target_price
    if entry_in.confidence_rating is not None:
        entry.confidence_rating = entry_in.confidence_rating
    if entry_in.review_date is not None:
        entry.review_date = entry_in.review_date

    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(InvestmentJournalEntry).filter(
        InvestmentJournalEntry.id == entry_id,
        InvestmentJournalEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    db.delete(entry)
    db.commit()
    return None

@router.post("/{entry_id}/reflect", response_model=JournalEntryResponse)
def reflect_on_thesis(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Thesis Reflection (PRD Phase 6):
    Compares past user thesis and target price against current market reality,
    highlighting divergences without issuing buy/sell instructions.
    """
    entry = db.query(InvestmentJournalEntry).filter(
        InvestmentJournalEntry.id == entry_id,
        InvestmentJournalEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")

    quote = market_data_provider.get_quote(entry.ticker, db)
    curr_price = quote["price"] if quote else 0.0

    citations = rag_engine.retrieve_context(db, f"{entry.ticker} earnings supply demand", ticker=entry.ticker, limit=2)
    news_snippet = citations[0].snippet if citations else "No recent breaking news logged."

    price_diff_text = ""
    if entry.target_price and curr_price > 0:
        gap = round(((entry.target_price - curr_price) / curr_price) * 100, 2)
        price_diff_text = f"Target price was ${entry.target_price:.2f} vs current market price ${curr_price:.2f} ({gap:+}% gap)."

    reflection = (
        f"**Thesis Review for {entry.ticker} (Recorded on {entry.created_at.strftime('%Y-%m-%d')}):**\n"
        f"- *Original Premise*: \"{entry.thesis_content}\"\n"
        f"- *Market Status*: Current price is ${curr_price:.2f}. {price_diff_text}\n"
        f"- *Recent Context*: \"{news_snippet.strip()}\"\n"
        f"- *Objective Reflection*: Consider whether your original timeline and valuation assumptions "
        f"accounted for recent sector volatility and supply constraints. "
        f"Note: This reflection is purely analytical and does not advise adding or trimming positions."
    )

    entry.ai_reflection = reflection
    db.commit()
    db.refresh(entry)
    return entry
