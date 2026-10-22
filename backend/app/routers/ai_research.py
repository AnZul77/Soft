from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.ai import (
    ExplainImpactRequest, ExplainImpactResponse, AIResearchQuery, AIResearchResponse
)
from app.services.auth_service import get_current_user
from app.services.explain_impact_agent import explain_impact_agent, sanitize_input
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/ai", tags=["AI & Explainable RAG"])

@router.post("/explain-impact", response_model=ExplainImpactResponse)
def explain_portfolio_impact(
    req: ExplainImpactRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return explain_impact_agent.explain_impact(db, current_user.id, req)

@router.get("/explain-impact/stream")
async def stream_explain_portfolio_impact(
    portfolio_id: str = Query(...),
    ticker: str = Query(...),
    event_description: str = Query(None),
    price_change_pct: float = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = ExplainImpactRequest(
        portfolio_id=portfolio_id,
        ticker=ticker,
        event_description=event_description,
        price_change_pct=price_change_pct
    )
    generator = explain_impact_agent.stream_explain_impact(db, current_user.id, req)
    return StreamingResponse(generator, media_type="text/event-stream")

@router.post("/research", response_model=AIResearchResponse)
def semantic_research(
    query_in: AIResearchQuery,
    db: Session = Depends(get_db)
):
    clean_q = sanitize_input(query_in.query)
    citations = rag_engine.retrieve_context(
        db=db,
        query=clean_q,
        ticker=query_in.ticker,
        limit=query_in.limit
    )

    if not citations:
        return AIResearchResponse(
            query=clean_q,
            ticker=query_in.ticker,
            answer="No relevant financial news or filings were retrieved matching this query. Insufficient grounded evidence to synthesize an answer.",
            citations=[],
            abstention=True
        )

    top_c = citations[0]
    answer = (
        f"Based on recent reporting from {top_c.source} (\"{top_c.title}\"): "
        f"{top_c.snippet} "
        f"Market participants are evaluating ongoing capacity utilization and capital expenditure plans."
    )

    return AIResearchResponse(
        query=clean_q,
        ticker=query_in.ticker,
        answer=answer,
        citations=citations,
        abstention=False
    )
