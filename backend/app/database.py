from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30.0}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def ensure_sqlite_migrations(target_engine):
    """
    Lightweight auto-migration for SQLite development databases.
    Adds any missing columns to existing tables without data loss.
    """
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(target_engine)
        tables = inspector.get_table_names()
        
        with target_engine.begin() as conn:
            # Check 'portfolios'
            if "portfolios" in tables:
                cols = [c["name"] for c in inspector.get_columns("portfolios")]
                if "is_active" not in cols:
                    conn.execute(text("ALTER TABLE portfolios ADD COLUMN is_active BOOLEAN DEFAULT 1"))
            
            # Check 'users'
            if "users" in tables:
                cols = [c["name"] for c in inspector.get_columns("users")]
                if "risk_tolerance" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN risk_tolerance VARCHAR(30) DEFAULT 'MODERATE'"))
                if "investment_horizon" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN investment_horizon VARCHAR(30) DEFAULT 'MEDIUM_TERM'"))
                if "bio" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))
                if "updated_at" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP"))

            # Check 'investment_journal_entries'
            if "investment_journal_entries" in tables:
                cols = [c["name"] for c in inspector.get_columns("investment_journal_entries")]
                if "is_archived" not in cols:
                    conn.execute(text("ALTER TABLE investment_journal_entries ADD COLUMN is_archived BOOLEAN DEFAULT 0"))
    except Exception as e:
        import logging
        logging.getLogger("investment_platform").warning(f"Auto-migration check note: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
