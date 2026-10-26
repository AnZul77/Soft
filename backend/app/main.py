import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import * # Load all models
from app.routers import auth, portfolios, trading, market, risk_anomalies, ai_research, journal, watchlists, alerts
from app.services.market_data import market_data_provider
from app.services.rag_engine import rag_engine

logger = logging.getLogger("investment_platform")

async def run_periodic_background_tasks(interval_seconds: int = 60):
    """
    Automated periodic background task running in FastAPI lifespan.
    Evaluates anomaly scans and limit order matching every 60 seconds.
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            db = SessionLocal()
            try:
                from app.services.anomaly_scanner import anomaly_scanner
                from app.services.trading_engine import trading_engine
                anomaly_scanner.scan_for_anomalies(db, threshold_pct=0.08)
                trading_engine.match_all_pending_orders(db)
            except Exception as e:
                logger.error(f"Error in periodic background tasks: {e}")
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic loop error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        market_data_provider.sync_to_db(db)
        rag_engine.sync_knowledge_graph_and_news(db)
    finally:
        db.close()

    bg_task = asyncio.create_task(run_periodic_background_tasks(interval_seconds=60))
    yield
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for AI-Powered Investment Intelligence Platform with RAG, Ledger & Anomaly Detection",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(portfolios.router, prefix=settings.API_V1_STR)
app.include_router(trading.router, prefix=settings.API_V1_STR)
app.include_router(market.router, prefix=settings.API_V1_STR)
app.include_router(risk_anomalies.router, prefix=settings.API_V1_STR)
app.include_router(ai_research.router, prefix=settings.API_V1_STR)
app.include_router(journal.router, prefix=settings.API_V1_STR)
app.include_router(watchlists.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "market_cache": "warm",
        "version": settings.VERSION
    }
