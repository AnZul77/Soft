from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit_event(
    db: Session,
    user_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Records an immutable audit log entry for user authentication and operational actions."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    db.add(entry)
    db.flush()
    return entry
