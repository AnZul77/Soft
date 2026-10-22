import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Security(Base):
    __tablename__ = "securities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class QuoteCache(Base):
    __tablename__ = "quote_cache"

    ticker = Column(String(10), primary_key=True, index=True)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=False, default=0.0)
    change_percent = Column(Float, nullable=False, default=0.0)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(Text, unique=True, nullable=False)
    published_at = Column(DateTime, nullable=False)
    content_raw = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    sentiment_label = Column(String(20), nullable=True) # BULLISH, BEARISH, NEUTRAL
    sentiment_score = Column(Float, nullable=True) # -1.0 to 1.0
    ticker_tags = Column(String(255), nullable=True) # comma-separated tickers, e.g. "NVDA,TSMC,AAPL"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    embeddings = relationship("NewsEmbedding", back_populates="article", cascade="all, delete-orphan")

class NewsEmbedding(Base):
    __tablename__ = "news_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False) # JSON array of floats for cross-db cosine similarity
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    article = relationship("NewsArticle", back_populates="embeddings")
