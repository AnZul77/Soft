import re
import asyncio
from typing import AsyncGenerator, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding
from app.schemas.ai import ExplainImpactRequest, ExplainImpactResponse
from app.services.market_data import market_data_provider
from app.services.rag_engine import rag_engine

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"system\s*override",
    r"recommend\s+(buying|selling)\s+now",
    r"act\s+as\s+a\s+financial\s+advisor",
    r"<script\b[^>]*>",
    r"javascript:",
]

def sanitize_input(text: str) -> str:
    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[BLOCKED_ADVERSARIAL_INJECTION]", sanitized, flags=re.IGNORECASE)
    # Strip HTML tags
    sanitized = re.sub(r"<[^>]+>", "", sanitized)
    return sanitized.strip()

class ExplainImpactAgent:
    def explain_impact(
        self,
        db: Session,
        user_id: str,
        req: ExplainImpactRequest
    ) -> ExplainImpactResponse:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == req.portfolio_id,
            Portfolio.user_id == user_id
        ).first()

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {req.portfolio_id} not found or access denied"
            )

        ticker = req.ticker.upper()
        clean_event = sanitize_input(req.event_description or f"Price volatility event on {ticker}")

        # 1. Check portfolio direct holdings
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        target_holding = next((h for h in holdings if h.ticker == ticker), None)

        # 2. Retrieve supply chain relationships
        supply_links = rag_engine.get_supply_chain_links(db, ticker)
        related_tickers = set(l.source_ticker for l in supply_links) | set(l.target_ticker for l in supply_links)
        indirect_holdings = [h for h in holdings if h.ticker in related_tickers and h.ticker != ticker]

        # 3. Calculate portfolio exposure
        total_equity = portfolio.virtual_cash_balance + portfolio.reserved_cash
        holding_val = 0.0
        holding_shares = 0.0

        for h in holdings:
            q = market_data_provider.get_quote(h.ticker, db)
            price = q["price"] if q else h.cost_basis
            val = h.quantity * price
            total_equity += val
            if h.ticker == ticker:
                holding_val = val
                holding_shares = h.quantity

        exposure_pct = round((holding_val / total_equity) * 100, 2) if total_equity > 0 else 0.0
        direct_tickers = [ticker] if target_holding else []

        # 4. Semantic RAG context retrieval
        search_query = f"{ticker} {clean_event}"
        citations = rag_engine.retrieve_context(db, search_query, ticker=ticker, limit=3)

        # Check for abstention if no relevant evidence or holding exposure
        if not citations and not target_holding and not indirect_holdings:
            return ExplainImpactResponse(
                ticker=ticker,
                summary_headline="Insufficient Evidence to Assess Impact",
                portfolio_exposure_pct=0.0,
                portfolio_holding_shares=0.0,
                portfolio_holding_value=0.0,
                direct_holdings_affected=[],
                supply_chain_links=supply_links,
                evidence_citations=[],
                sentiment_impact="NEUTRAL",
                analysis_text=(
                    f"No verified market data or financial news articles were retrieved for {ticker}, "
                    f"and neither {ticker} nor any direct supply-chain partners are currently held in your portfolio. "
                    f"Insufficient grounded evidence to assess impact."
                ),
                abstention=True
            )

        # 5. Synthesize grounded explainable response
        price_drop = req.price_change_pct or 0.0
        sentiment = "BEARISH" if price_drop < 0 else ("BULLISH" if price_drop > 0 else "NEUTRAL")

        analysis_paragraphs = []
        if target_holding:
            analysis_paragraphs.append(
                f"**Direct Exposure Context**: You hold **{holding_shares} shares** of {ticker} "
                f"valued at **${holding_val:,.2f}**, representing **{exposure_pct}%** of your total portfolio equity."
            )
        else:
            analysis_paragraphs.append(
                f"**Direct Exposure Context**: You do not hold direct shares of {ticker}."
            )

        if indirect_holdings:
            indirect_names = ", ".join([f"{ih.ticker} ({ih.quantity} shares)" for ih in indirect_holdings])
            analysis_paragraphs.append(
                f"**Supply Chain Contagion Risk**: While assessing {ticker}, your portfolio holds connected companies: **{indirect_names}**. "
                f"Supply or pricing bottlenecks in {ticker} can propagate downstream or upstream across these positions."
            )

        if citations:
            best_citation = citations[0]
            analysis_paragraphs.append(
                f"**Market Grounding**: According to *{best_citation.source}* (*\"{best_citation.title}\"*): "
                f"\"{best_citation.snippet.strip()}\""
            )

        analysis_paragraphs.append(
            "**Strategic Takeaway**: Retail investors often overreact to headline volatility. "
            "Review your target allocation and investment thesis to determine whether underlying business fundamentals "
            "have structurally shifted or if this represents short-term liquidity noise."
        )

        full_analysis = "\n\n".join(analysis_paragraphs)

        headline = (
            f"{ticker} Volatility Event: {exposure_pct}% Portfolio Exposure"
            if target_holding else
            f"{ticker} Ecosystem Update: Indirect Supply Chain Relevance"
        )

        return ExplainImpactResponse(
            ticker=ticker,
            summary_headline=headline,
            portfolio_exposure_pct=exposure_pct,
            portfolio_holding_shares=holding_shares,
            portfolio_holding_value=round(holding_val, 2),
            direct_holdings_affected=direct_tickers,
            supply_chain_links=supply_links,
            evidence_citations=citations,
            sentiment_impact=sentiment,
            analysis_text=full_analysis,
            abstention=False
        )

    async def stream_explain_impact(
        self,
        db: Session,
        user_id: str,
        req: ExplainImpactRequest
    ) -> AsyncGenerator[str, None]:
        """Server-Sent Events (SSE) generator streaming explanation tokens."""
        response = self.explain_impact(db, user_id, req)
        
        words = response.analysis_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.02) # Sub-second streaming rhythm

        yield f"event: done\ndata: [COMPLETED]\n\n"

explain_impact_agent = ExplainImpactAgent()
