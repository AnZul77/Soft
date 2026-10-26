from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistCreate, WatchlistUpdate, WatchlistResponse,
    WatchlistItemCreate, WatchlistItemResponse
)
from app.services.auth_service import get_current_user
from app.services.market_data import market_data_provider
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])

def _enrich_item(item: WatchlistItem, db: Session) -> WatchlistItemResponse:
    quote = market_data_provider.get_quote(item.ticker, db)
    return WatchlistItemResponse(
        id=item.id,
        watchlist_id=item.watchlist_id,
        ticker=item.ticker,
        notes=item.notes,
        target_price=item.target_price,
        added_at=item.added_at,
        current_price=quote.get("price") if quote else None,
        change_percent=quote.get("change_percent") if quote else None
    )

def _enrich_watchlist(w: Watchlist, db: Session) -> WatchlistResponse:
    items = [_enrich_item(item, db) for item in w.items]
    return WatchlistResponse(
        id=w.id,
        user_id=w.user_id,
        name=w.name,
        description=w.description,
        items=items,
        created_at=w.created_at,
        updated_at=w.updated_at
    )

@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = Watchlist(
        user_id=current_user.id,
        name=data.name,
        description=data.description
    )
    db.add(wl)
    db.flush()

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="WATCHLIST_CREATED",
        resource_type="WATCHLIST",
        resource_id=wl.id,
        details=f"Created watchlist '{wl.name}'"
    )

    db.commit()
    db.refresh(wl)
    return _enrich_watchlist(wl, db)

@router.get("/", response_model=List[WatchlistResponse])
def get_watchlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wls = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).order_by(Watchlist.created_at.desc()).all()
    return [_enrich_watchlist(w, db) for w in wls]

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(
    watchlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")
    return _enrich_watchlist(wl, db)

@router.put("/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist(
    watchlist_id: str,
    data: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    if data.name is not None:
        wl.name = data.name
    if data.description is not None:
        wl.description = data.description

    db.commit()
    db.refresh(wl)
    return _enrich_watchlist(wl, db)

@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    watchlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    db.delete(wl)
    db.commit()
    return None

@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_watchlist_item(
    watchlist_id: str,
    item_in: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    ticker = item_in.ticker.upper().strip()
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.watchlist_id == watchlist_id,
        WatchlistItem.ticker == ticker
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ticker {ticker} already in watchlist")

    from sqlalchemy.exc import IntegrityError
    item = WatchlistItem(
        watchlist_id=watchlist_id,
        ticker=ticker,
        notes=item_in.notes,
        target_price=item_in.target_price
    )
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ticker {ticker} already in watchlist")
    return _enrich_item(item, db)

@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_item(
    watchlist_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wl = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.watchlist_id == watchlist_id
    ).first()
    if not item:
        # Also try searching by ticker if item_id matches ticker
        item = db.query(WatchlistItem).filter(
            WatchlistItem.ticker == item_id.upper(),
            WatchlistItem.watchlist_id == watchlist_id
        ).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found")

    db.delete(item)
    db.commit()
    return None
