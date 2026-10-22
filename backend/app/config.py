import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Investment Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-dev-jwt-key-investment-platform-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # SQLite default for out-of-the-box local execution, or PostgreSQL if configured
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./investment_intelligence.db")
    
    # Market Data
    DEFAULT_BENCHMARK_TICKER: str = "SPY"
    ANOMALY_PRICE_CHANGE_THRESHOLD: float = 0.08  # 8% price change
    ANOMALY_WINDOW_MINUTES: int = 15
    
    # LLM Settings (can be mocked or live)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
