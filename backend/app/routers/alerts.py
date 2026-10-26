from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import AlertRule, AlertNotification, AlertStatus
from app.schemas.alert import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertNotificationResponse
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts & User Alert Rules"])

@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule_in: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = AlertRule(
        user_id=current_user.id,
        ticker=rule_in.ticker.upper().strip() if rule_in.ticker else None,
        threshold_pct=rule_in.threshold_pct,
        window_minutes=rule_in.window_minutes,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/rules", response_model=List[AlertRuleResponse])
def get_alert_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rules = db.query(AlertRule).filter(
        AlertRule.user_id == current_user.id
    ).order_by(AlertRule.created_at.desc()).all()
    return rules

@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def get_alert_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: str,
    rule_in: AlertRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")

    if rule_in.ticker is not None:
        rule.ticker = rule_in.ticker.upper().strip() if rule_in.ticker else None
    if rule_in.threshold_pct is not None:
        rule.threshold_pct = rule_in.threshold_pct
    if rule_in.window_minutes is not None:
        rule.window_minutes = rule_in.window_minutes
    if rule_in.is_active is not None:
        rule.is_active = rule_in.is_active

    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")

    db.delete(rule)
    db.commit()
    return None

@router.get("", response_model=List[AlertNotificationResponse])
@router.get("/", response_model=List[AlertNotificationResponse])
def get_user_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alerts = db.query(AlertNotification).filter(
        AlertNotification.user_id == current_user.id
    ).order_by(AlertNotification.created_at.desc()).all()
    return alerts

@router.put("/{alert_id}/read", response_model=AlertNotificationResponse)
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
