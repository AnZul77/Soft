from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import random
import hashlib
from sqlalchemy.orm import Session
from app.models.market import Security, QuoteCache, NewsArticle
from app.schemas.market import AnomalyInjectionRequest

try:
    import yfinance as yf
except ImportError:
    yf = None

INITIAL_SECURITIES = [
    {"ticker": "NVDA", "company_name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "price": 128.50, "prev_close": 127.00},
    {"ticker": "TSMC", "company_name": "Taiwan Semiconductor Manufacturing Co.", "sector": "Technology", "industry": "Semiconductors", "price": 172.00, "prev_close": 170.50},
    {"ticker": "AAPL", "company_name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "price": 230.00, "prev_close": 228.80},
    {"ticker": "TSLA", "company_name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "price": 215.00, "prev_close": 218.00},
    {"ticker": "MSFT", "company_name": "Microsoft Corporation", "sector": "Technology", "industry": "Software - Infrastructure", "price": 445.00, "prev_close": 442.00},
    {"ticker": "AMD", "company_name": "Advanced Micro Devices, Inc.", "sector": "Technology", "industry": "Semiconductors", "price": 155.00, "prev_close": 153.20},
    {"ticker": "SPY", "company_name": "SPDR S&P 500 ETF Trust", "sector": "Financial", "industry": "Exchange Traded Fund", "price": 580.00, "prev_close": 578.50},
    {"ticker": "INTC", "company_name": "Intel Corporation", "sector": "Technology", "industry": "Semiconductors", "price": 23.50, "prev_close": 24.10},
    {"ticker": "GOOGL", "company_name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Content & Information", "price": 182.50, "prev_close": 180.20},
    {"ticker": "AMZN", "company_name": "Amazon.com, Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail", "price": 195.00, "prev_close": 193.40},
    {"ticker": "META", "company_name": "Meta Platforms, Inc.", "sector": "Technology", "industry": "Internet Content & Information", "price": 590.00, "prev_close": 585.00},
    {"ticker": "QQQ", "company_name": "Invesco QQQ Trust", "sector": "Financial", "industry": "Exchange Traded Fund", "price": 490.00, "prev_close": 487.50},
    {"ticker": "JPM", "company_name": "JPMorgan Chase & Co.", "sector": "Financial", "industry": "Diversified Banking", "price": 225.00, "prev_close": 223.80},
]

class MarketDataProvider:
    def __init__(self):
        self._quote_cache: Dict[str, dict] = {}
        self._cache_ttl_seconds = 60
        self._initialize_defaults()

    def _initialize_defaults(self):
        now = datetime.now(timezone.utc)
        for item in INITIAL_SECURITIES:
            ticker = item["ticker"]
            price = item["price"]
            prev = item["prev_close"]
            change = price - prev
            change_pct = (change / prev) * 100
            self._quote_cache[ticker] = {
                "ticker": ticker,
                "price": price,
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "high_24h": round(price * 1.02, 2),
                "low_24h": round(price * 0.98, 2),
                "volume": 25000000.0,
                "previous_close": prev,
                "last_updated": now,
                "is_stale": False,
                "source": "MOCK_LIVE"
            }

    def sync_to_db(self, db: Session):
        """Ensures default securities and quotes are present in the database."""
        for sec in INITIAL_SECURITIES:
            existing_sec = db.query(Security).filter(Security.ticker == sec["ticker"]).first()
            if not existing_sec:
                db_sec = Security(
                    ticker=sec["ticker"],
                    company_name=sec["company_name"],
                    sector=sec["sector"],
                    industry=sec["industry"]
                )
                db.add(db_sec)

            quote_data = self._quote_cache.get(sec["ticker"])
            if quote_data:
                db_quote = db.query(QuoteCache).filter(QuoteCache.ticker == sec["ticker"]).first()
                if not db_quote:
                    db_quote = QuoteCache(
                        ticker=sec["ticker"],
                        price=quote_data["price"],
                        change=quote_data["change"],
                        change_percent=quote_data["change_percent"],
                        high_24h=quote_data["high_24h"],
                        low_24h=quote_data["low_24h"],
                        volume=quote_data["volume"],
                        previous_close=quote_data["previous_close"],
                        last_updated=quote_data["last_updated"]
                    )
                    db.add(db_quote)
                else:
                    db_quote.price = quote_data["price"]
                    db_quote.change = quote_data["change"]
                    db_quote.change_percent = quote_data["change_percent"]
                    db_quote.last_updated = quote_data["last_updated"]
        db.commit()

    def get_quote(self, ticker: str, db: Optional[Session] = None) -> Optional[dict]:
        ticker = ticker.upper()
        now = datetime.now(timezone.utc)
        if ticker in self._quote_cache:
            data = self._quote_cache[ticker]
            # Check TTL
            if (now - data["last_updated"]).total_seconds() > self._cache_ttl_seconds:
                # Add minor realistic jitter
                jitter = random.uniform(-0.002, 0.002)
                data["price"] = round(data["price"] * (1 + jitter), 2)
                data["change"] = round(data["price"] - data["previous_close"], 2)
                data["change_percent"] = round((data["change"] / data["previous_close"]) * 100, 2)
                data["last_updated"] = now
            return data

        # Check DB fallback
        if db:
            db_quote = db.query(QuoteCache).filter(QuoteCache.ticker == ticker).first()
            if db_quote:
                quote_dict = {
                    "ticker": db_quote.ticker,
                    "price": db_quote.price,
                    "change": db_quote.change,
                    "change_percent": db_quote.change_percent,
                    "high_24h": db_quote.high_24h,
                    "low_24h": db_quote.low_24h,
                    "volume": db_quote.volume,
                    "previous_close": db_quote.previous_close,
                    "last_updated": db_quote.last_updated,
                    "is_stale": True,
                    "source": "DB_CACHE"
                }
                self._quote_cache[ticker] = quote_dict
                return quote_dict

        # Resolve extended market symbol via yfinance or realistic synthesis
        resolved = self._resolve_extended_symbol(ticker, db)
        if resolved:
            return resolved

        return None

    def get_all_quotes(self, db: Optional[Session] = None) -> List[dict]:
        results = []
        for ticker in list(self._quote_cache.keys()):
            q = self.get_quote(ticker, db)
            if q:
                results.append(q)
        return results

    def inject_anomaly(self, req: AnomalyInjectionRequest, db: Session) -> dict:
        """Injects a sharp market drop or spike for testing anomaly alerts & RAG."""
        ticker = req.ticker.upper()
        current = self.get_quote(ticker, db)
        prev_close = current["previous_close"] if current and current.get("previous_close") else (current["price"] if current else 100.0)
        old_price = current["price"] if current else prev_close
        
        new_price = round(prev_close * (1 + req.price_change_pct), 2)
        change = round(new_price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2)
        now = datetime.now(timezone.utc)

        updated_quote = {
            "ticker": ticker,
            "price": new_price,
            "change": change,
            "change_percent": change_pct,
            "high_24h": max(old_price, new_price),
            "low_24h": min(old_price, new_price),
            "volume": 75000000.0,
            "previous_close": prev_close,
            "last_updated": now,
            "is_stale": False,
            "source": "ANOMALY_INJECTED"
        }
        self._quote_cache[ticker] = updated_quote

        # Also update DB quote
        db_quote = db.query(QuoteCache).filter(QuoteCache.ticker == ticker).first()
        if db_quote:
            db_quote.price = new_price
            db_quote.change = change
            db_quote.change_percent = change_pct
            db_quote.last_updated = now
        else:
            db_quote = QuoteCache(
                ticker=ticker,
                price=new_price,
                change=change,
                change_percent=change_pct,
                last_updated=now
            )
            db.add(db_quote)

        # Ingest breaking news article if provided
        headline = req.headline or f"Breaking: {ticker} experiences sudden {change_pct}% price volatility"
        content = req.content or (
            f"Shares of {ticker} plunged/surged sharply during intraday trading. "
            f"Supply chain reports and sudden macroeconomic demand adjustments triggered extensive trading volume."
        )
        url = f"https://finance-news.wire/{ticker.lower()}-anomaly-{int(now.timestamp())}"
        
        news_art = NewsArticle(
            title=headline,
            source="MarketPulse Terminal",
            url=url,
            published_at=now,
            content_raw=content,
            ai_summary=headline,
            sentiment_label="BEARISH" if req.price_change_pct < 0 else "BULLISH",
            sentiment_score=float(req.price_change_pct),
            ticker_tags=ticker
        )
        db.add(news_art)
        db.commit()

        return updated_quote

    def _resolve_extended_symbol(self, ticker: str, db: Optional[Session] = None) -> Optional[dict]:
        ticker = ticker.upper().strip()
        now = datetime.now(timezone.utc)

        # 1. Check if yfinance is available
        if yf:
            try:
                t = yf.Ticker(ticker)
                fast_info = getattr(t, "fast_info", None)
                if fast_info and getattr(fast_info, "last_price", None):
                    price = round(float(fast_info.last_price), 2)
                    prev = round(float(getattr(fast_info, "previous_close", price)), 2)
                    change = round(price - prev, 2)
                    pct = round((change / prev) * 100, 2) if prev else 0.0
                    quote = {
                        "ticker": ticker,
                        "price": price,
                        "change": change,
                        "change_percent": pct,
                        "high_24h": round(float(getattr(fast_info, "day_high", price * 1.02)), 2),
                        "low_24h": round(float(getattr(fast_info, "day_low", price * 0.98)), 2),
                        "volume": float(getattr(fast_info, "last_volume", 1000000.0)),
                        "previous_close": prev,
                        "last_updated": now,
                        "is_stale": False,
                        "source": "YFINANCE_LIVE"
                    }
                    self._quote_cache[ticker] = quote
                    self._persist_symbol(ticker, f"{ticker} Corp", price, prev, db)
                    return quote
            except Exception:
                pass

        # 2. Check valid ticker pattern (1-5 letters)
        if not ticker.isalpha() or len(ticker) > 5:
            return None

        # 3. Deterministic realistic synthetic generation for lookup beyond seed stocks
        seed_val = int(hashlib.md5(ticker.encode()).hexdigest(), 16)
        base_price = round(20.0 + (seed_val % 380) + ((seed_val % 99) / 100.0), 2)
        daily_move_pct = round(((seed_val % 40) - 20) / 10.0, 2) # between -2.0% and +2.0%
        prev_close = round(base_price / (1 + (daily_move_pct / 100.0)), 2)
        change = round(base_price - prev_close, 2)

        quote = {
            "ticker": ticker,
            "price": base_price,
            "change": change,
            "change_percent": daily_move_pct,
            "high_24h": round(base_price * 1.02, 2),
            "low_24h": round(base_price * 0.98, 2),
            "volume": float(1000000 + (seed_val % 10000000)),
            "previous_close": prev_close,
            "last_updated": now,
            "is_stale": False,
            "source": "SYNTHETIC_MARKET_LOOKUP"
        }
        self._quote_cache[ticker] = quote
        self._persist_symbol(ticker, f"{ticker} Technologies Corp", base_price, prev_close, db)
        return quote

    def _persist_symbol(self, ticker: str, company_name: str, price: float, prev_close: float, db: Optional[Session]):
        if not db:
            return
        try:
            sec = db.query(Security).filter(Security.ticker == ticker).first()
            if not sec:
                db.add(Security(ticker=ticker, company_name=company_name, sector="Technology", industry="General"))
            q = db.query(QuoteCache).filter(QuoteCache.ticker == ticker).first()
            if not q:
                db.add(QuoteCache(
                    ticker=ticker,
                    price=price,
                    change=round(price - prev_close, 2),
                    change_percent=round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0.0,
                    previous_close=prev_close,
                    last_updated=datetime.now(timezone.utc)
                ))
            db.commit()
        except Exception:
            db.rollback()

    def get_history(self, ticker: str, period: str = "30d", db: Optional[Session] = None) -> dict:
        ticker = ticker.upper().strip()
        quote = self.get_quote(ticker, db)
        if not quote:
            raise ValueError(f"Ticker '{ticker}' not found")

        current_price = float(quote["price"])
        company_name = ticker

        if db:
            sec = db.query(Security).filter(Security.ticker == ticker.upper()).first()
            if sec:
                company_name = sec.company_name

        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 252}
        num_days = days_map.get(period.lower(), 30)

        # Attempt yfinance if available
        if yf:
            try:
                hist = yf.Ticker(ticker).history(period=period)
                if not hist.empty:
                    candles = []
                    for idx, row in hist.iterrows():
                        candles.append({
                            "timestamp": idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else idx,
                            "open": round(float(row["Open"]), 2),
                            "high": round(float(row["High"]), 2),
                            "low": round(float(row["Low"]), 2),
                            "close": round(float(row["Close"]), 2),
                            "volume": round(float(row["Volume"]), 2),
                        })
                    if candles:
                        return {
                            "ticker": ticker.upper(),
                            "company_name": company_name,
                            "period": period,
                            "current_price": current_price,
                            "candles": candles
                        }
            except Exception:
                pass

        # Realistic synthetic candle generation
        candles = []
        now = datetime.now(timezone.utc)
        running_price = current_price

        daily_prices = [running_price]
        random_gen = random.Random(int(hashlib.md5(f"{ticker.upper()}-{period}".encode()).hexdigest(), 16))
        for _ in range(num_days - 1):
            daily_pct = random_gen.uniform(-0.025, 0.025)
            running_price = max(1.0, running_price / (1.0 + daily_pct))
            daily_prices.append(round(running_price, 2))

        daily_prices.reverse()

        for i, close_p in enumerate(daily_prices):
            c_date = now - timedelta(days=(num_days - 1 - i))
            open_p = daily_prices[i - 1] if i > 0 else round(close_p * (1 + random_gen.uniform(-0.01, 0.01)), 2)
            high_p = round(max(open_p, close_p) * (1 + random_gen.uniform(0.002, 0.015)), 2)
            low_p = round(min(open_p, close_p) * (1 - random_gen.uniform(0.002, 0.015)), 2)
            vol = round(random_gen.uniform(5000000, 35000000), 0)
            candles.append({
                "timestamp": c_date,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "volume": vol
            })

        return {
            "ticker": ticker.upper(),
            "company_name": company_name,
            "period": period,
            "current_price": current_price,
            "candles": candles
        }

market_data_provider = MarketDataProvider()
