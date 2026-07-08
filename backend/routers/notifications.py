from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from models.notification import Notification
from schemas.schemas import NotificationResponse
from services.auth_service import get_current_customer

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    return (
        db.query(Notification)
        .filter(Notification.customer_id == current.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/unread-count")
async def unread_count(current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(
        Notification.customer_id == current.id,
        Notification.is_read == False,
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
async def mark_read(notification_id: int, current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.customer_id == current.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"status": "ok"}


@router.put("/read-all")
async def mark_all_read(current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.customer_id == current.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok"}
