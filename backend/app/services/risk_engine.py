import math
from datetime import datetime, timezone
from typing import Dict
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding
from app.schemas.alert import RiskMetricsResponse
from app.services.market_data import market_data_provider

ASSET_BETAS: Dict[str, float] = {
    "NVDA": 1.75,
    "TSMC": 1.25,
    "AAPL": 1.10,
    "TSLA": 2.10,
    "MSFT": 1.15,
    "AMD": 1.65,
    "SPY": 1.00,
    "INTC": 1.05,
}

ASSET_VOLATILITIES: Dict[str, float] = {
    "NVDA": 0.48, # 48% annualized
    "TSMC": 0.35,
    "AAPL": 0.22,
    "TSLA": 0.55,
    "MSFT": 0.24,
    "AMD": 0.45,
    "SPY": 0.15,
    "INTC": 0.38,
}

class RiskEngine:
    def calculate_risk_metrics(self, db: Session, portfolio_id: str) -> RiskMetricsResponse:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        holding_values = []
        total_holding_value = 0.0

        for h in holdings:
            quote = market_data_provider.get_quote(h.ticker, db)
            price = quote["price"] if quote else h.cost_basis
            val = h.quantity * price
            holding_values.append({"ticker": h.ticker, "value": val})
            total_holding_value += val

        total_equity = total_holding_value + portfolio.virtual_cash_balance + portfolio.reserved_cash
        if total_equity <= 0:
            total_equity = 1.0

        # Weights relative to total equity
        weights = [item["value"] / total_equity for item in holding_values]
        
        # 1. Concentration: Herfindahl-Hirschman Index (HHI)
        # HHI on scale 0 to 1
        hhi = sum(w ** 2 for w in weights) if weights else 0.0

        # Top 3 concentration
        sorted_weights = sorted(weights, reverse=True)
        top_3_pct = round(sum(sorted_weights[:3]) * 100, 2)
        is_high_concentration = (hhi > 0.25) or (top_3_pct > 50.0)

        # 2. Portfolio Beta
        # Weighted beta of holdings; cash beta is 0.0
        portfolio_beta = 0.0
        for item, w in zip(holding_values, weights):
            asset_beta = ASSET_BETAS.get(item["ticker"], 1.0)
            portfolio_beta += w * asset_beta

        # 3. Portfolio Annualized Volatility
        # Approximated via asset-weighted volatility
        portfolio_vol = 0.0
        for item, w in zip(holding_values, weights):
            asset_vol = ASSET_VOLATILITIES.get(item["ticker"], 0.25)
            portfolio_vol += w * asset_vol

        # 4. Parametric Value at Risk (VaR 95% 1-day)
        # 1.645 * daily_std * portfolio_value
        daily_vol = portfolio_vol / math.sqrt(252)
        var_95_1d = round(1.645 * daily_vol * total_equity, 2)

        return RiskMetricsResponse(
            portfolio_id=portfolio.id,
            concentration_hhi=round(hhi, 4),
            top_3_concentration_pct=top_3_pct,
            is_high_concentration=is_high_concentration,
            annualized_volatility=round(portfolio_vol * 100, 2), # In percentage
            portfolio_beta=round(portfolio_beta, 2),
            value_at_risk_95_1d=var_95_1d,
            benchmark_ticker="SPY",
            calculated_at=datetime.now(timezone.utc)
        )

risk_engine = RiskEngine()
