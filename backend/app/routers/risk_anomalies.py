from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import AlertNotification, AlertStatus
from app.schemas.alert import RiskMetricsResponse, AlertNotificationResponse
from app.services.auth_service import get_current_user
from app.services.portfolio_service import portfolio_service
from app.services.risk_engine import risk_engine
from app.services.anomaly_scanner import anomaly_scanner

router = APIRouter(prefix="/risk-anomalies", tags=["Risk & Anomaly Engine"])

@router.get("/portfolios/{portfolio_id}/risk", response_model=RiskMetricsResponse)
def get_portfolio_risk(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    portfolio_service.get_portfolio(db, current_user.id, portfolio_id)
    return risk_engine.calculate_risk_metrics(db, portfolio_id)

@router.post("/anomalies/scan", response_model=List[AlertNotificationResponse])
def run_anomaly_scan(db: Session = Depends(get_db)):
    """Triggers the background anomaly scan over consolidated asset watcher queue."""
    alerts = anomaly_scanner.scan_for_anomalies(db, threshold_pct=0.08)
    return alerts

@router.get("/alerts", response_model=List[AlertNotificationResponse])
def get_user_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alerts = db.query(AlertNotification).filter(
        AlertNotification.user_id == current_user.id
    ).order_by(AlertNotification.created_at.desc()).all()
    return alerts

@router.put("/alerts/{alert_id}/read", response_model=AlertNotificationResponse)
def mark_alert_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(AlertNotification).filter(
        AlertNotification.id == alert_id,
        AlertNotification.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.status = AlertStatus.READ
    db.commit()
    db.refresh(alert)
    return alert
