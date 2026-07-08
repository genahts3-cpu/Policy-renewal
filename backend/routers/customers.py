from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import CustomerResponse, CustomerUpdate
from services.auth_service import get_current_customer, get_admin_customer

router = APIRouter()


@router.get("/me", response_model=CustomerResponse)
async def get_me(current: Customer = Depends(get_current_customer)):
    return current


@router.put("/me", response_model=CustomerResponse)
async def update_me(data: CustomerUpdate, current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    return db.query(Customer).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db), current: Customer = Depends(get_current_customer)):
    if not current.is_admin and current.id != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
