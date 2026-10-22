from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio, Holding
from app.models.alert import AlertNotification, AlertStatus
from app.services.market_data import market_data_provider

class AnomalyScanner:
    def scan_for_anomalies(self, db: Session, threshold_pct: float = 0.08) -> List[AlertNotification]:
        quotes = market_data_provider.get_all_quotes(db)
        created_alerts: List[AlertNotification] = []

        for q in quotes:
            ticker = q["ticker"]
            change_percent = abs(q["change_percent"] / 100.0)

            if change_percent >= threshold_pct:
                direction = "PRICE_DROP" if q["change_percent"] < 0 else "PRICE_SPIKE"
                current_price = q["price"]

                # Find all portfolios that hold this ticker
                affected_holdings = db.query(Holding).filter(Holding.ticker == ticker).all()

                for h in affected_holdings:
                    portfolio = db.query(Portfolio).filter(Portfolio.id == h.portfolio_id).first()
                    if not portfolio:
                        continue

                    # Calculate exposure
                    all_holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                    total_equity = portfolio.virtual_cash_balance + portfolio.reserved_cash
                    holding_val = h.quantity * current_price

                    for other_h in all_holdings:
                        other_q = market_data_provider.get_quote(other_h.ticker, db)
                        p = other_q["price"] if other_q else other_h.cost_basis
                        total_equity += other_h.quantity * p

                    exposure_pct = round((holding_val / total_equity) * 100, 2) if total_equity > 0 else 0.0

                    # Check if an alert was already issued in the last 15 minutes to avoid duplicates
                    existing = db.query(AlertNotification).filter(
                        AlertNotification.user_id == portfolio.user_id,
                        AlertNotification.portfolio_id == portfolio.id,
                        AlertNotification.ticker == ticker,
                        AlertNotification.event_type == direction
                    ).order_by(AlertNotification.created_at.desc()).first()

                    now = datetime.now(timezone.utc)
                    # Deduplicate if created within last 10 minutes (handling aware/naive comparisons)
                    if existing:
                        created = existing.created_at
                        if created.tzinfo is None:
                            created = created.replace(tzinfo=timezone.utc)
                        if (now - created).total_seconds() < 600:
                            continue

                    sign = "+" if q["change_percent"] > 0 else ""
                    msg = (
                        f"Market Alert: {ticker} moved {sign}{q['change_percent']:.2f}% to ${current_price:.2f}. "
                        f"Your portfolio '{portfolio.name}' has {exposure_pct}% exposure."
                    )

                    alert = AlertNotification(
                        user_id=portfolio.user_id,
                        portfolio_id=portfolio.id,
                        ticker=ticker,
                        event_type=direction,
                        price_change_pct=round(q["change_percent"], 2),
                        current_price=current_price,
                        portfolio_exposure_pct=exposure_pct,
                        status=AlertStatus.DELIVERED,
                        message=msg,
                        created_at=now
                    )
                    db.add(alert)
                    created_alerts.append(alert)

        if created_alerts:
            db.commit()
            for a in created_alerts:
                db.refresh(a)

        return created_alerts

anomaly_scanner = AnomalyScanner()
