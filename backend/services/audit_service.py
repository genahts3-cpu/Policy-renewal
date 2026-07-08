import logging
from sqlalchemy.orm import Session
from models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def write_audit_log(
    db: Session,
    agent_name: str,
    action: str,
    user_id: int = None,
    question: str = None,
    retrieved_documents: str = None,
    response: str = None,
    status: str = "success",
    ip_address: str = None,
):
    try:
        log = AuditLog(
            user_id=user_id,
            agent_name=agent_name,
            action=action,
            question=question[:2000] if question else None,
            retrieved_documents=retrieved_documents[:1000] if retrieved_documents else None,
            response=response[:2000] if response else None,
            status=status,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log write failed: {e}")
        db.rollback()
