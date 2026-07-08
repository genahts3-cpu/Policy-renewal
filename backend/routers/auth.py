from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import Token, LoginRequest, CustomerCreate, CustomerResponse
from services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.email == request.email).first()
    if not customer or not verify_password(request.password, customer.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(customer.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        customer_id=customer.id,
        is_admin=customer.is_admin,
        full_name=customer.full_name,
    )


@router.post("/register", response_model=CustomerResponse)
async def register(data: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    customer = Customer(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        address=data.address,
        date_of_birth=data.date_of_birth,
        age=data.age,
        occupation=data.occupation,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
