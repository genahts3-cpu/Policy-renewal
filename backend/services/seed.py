import logging
from datetime import date, timedelta
from db.database import SessionLocal
from models.customer import Customer
from models.policy import Policy
from models.claim import Claim
from models.notification import Notification
from models.support_user import SupportUser
from services.auth_service import hash_password

logger = logging.getLogger(__name__)

CUSTOMERS = [
    {
        "email": "admin@insurance.com",
        "password": "admin123",
        "full_name": "Admin User",
        "phone": "+1-555-0100",
        "age": 35,
        "occupation": "Insurance Manager",
        "risk_profile": "low",
        "is_admin": True,
    },
    {
        "email": "john.smith@email.com",
        "password": "password123",
        "full_name": "John Smith",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001",
        "date_of_birth": "1985-03-15",
        "age": 39,
        "occupation": "Software Engineer",
        "risk_profile": "low",
    },
    {
        "email": "sarah.johnson@email.com",
        "password": "password123",
        "full_name": "Sarah Johnson",
        "phone": "+1-555-0102",
        "address": "456 Oak Ave, Los Angeles, CA 90001",
        "date_of_birth": "1990-07-22",
        "age": 34,
        "occupation": "Teacher",
        "risk_profile": "low",
    },
    {
        "email": "mike.davis@email.com",
        "password": "password123",
        "full_name": "Mike Davis",
        "phone": "+1-555-0103",
        "address": "789 Pine Rd, Chicago, IL 60601",
        "date_of_birth": "1975-11-08",
        "age": 49,
        "occupation": "Business Owner",
        "risk_profile": "medium",
    },
    {
        "email": "emily.chen@email.com",
        "password": "password123",
        "full_name": "Emily Chen",
        "phone": "+1-555-0104",
        "address": "321 Elm St, Houston, TX 77001",
        "date_of_birth": "1995-01-30",
        "age": 29,
        "occupation": "Nurse",
        "risk_profile": "low",
    },
]

POLICIES_TEMPLATE = [
    {
        "policy_type": "life",
        "coverage_amount": 500000.0,
        "premium_amount": 1200.0,
        "deductible": 0.0,
        "description": "Term life insurance providing financial protection for your family.",
        "beneficiary": "Spouse",
        "days_offset": -300,
        "duration_days": 365,
        "status": "active",
    },
    {
        "policy_type": "health",
        "coverage_amount": 100000.0,
        "premium_amount": 3600.0,
        "deductible": 1000.0,
        "description": "Comprehensive health insurance covering medical expenses.",
        "beneficiary": "Self",
        "days_offset": -200,
        "duration_days": 365,
        "status": "active",
    },
    {
        "policy_type": "auto",
        "coverage_amount": 50000.0,
        "premium_amount": 1800.0,
        "deductible": 500.0,
        "description": "Full coverage auto insurance for your vehicle.",
        "beneficiary": "Self",
        "days_offset": -350,
        "duration_days": 365,
        "status": "active",
    },
    {
        "policy_type": "home",
        "coverage_amount": 300000.0,
        "premium_amount": 2400.0,
        "deductible": 2000.0,
        "description": "Homeowners insurance protecting your property.",
        "beneficiary": "Self",
        "days_offset": -60,
        "duration_days": 365,
        "status": "active",
    },
]

CLAIMS_TEMPLATE = [
    {
        "claim_type": "medical",
        "amount": 2500.0,
        "status": "approved",
        "description": "Emergency room visit and treatment",
        "filed_date": "2024-06-15",
    },
    {
        "claim_type": "auto_accident",
        "amount": 4200.0,
        "status": "approved",
        "description": "Minor collision repair",
        "filed_date": "2024-08-20",
    },
    {
        "claim_type": "property_damage",
        "amount": 1800.0,
        "status": "pending",
        "description": "Storm damage to roof",
        "filed_date": "2024-11-01",
    },
]


async def _seed_support_users(db):
    try:
        if db.query(SupportUser).count() > 0:
            return
        support_team = [
            {"name": "Priya Sharma", "email": "priya.sharma@insurance.com", "department": "Policy Support", "calendar_email": "priya.sharma@insurance.com"},
            {"name": "Rahul Mehta", "email": "rahul.mehta@insurance.com", "department": "Claims Support", "calendar_email": "rahul.mehta@insurance.com"},
            {"name": "Anita Desai", "email": "anita.desai@insurance.com", "department": "Renewal Support", "calendar_email": "anita.desai@insurance.com"},
        ]
        for s in support_team:
            db.add(SupportUser(**s, status="available"))
        db.commit()
        logger.info("Support users seeded.")
    except Exception as e:
        logger.warning(f"Support user seeding failed: {e}")
        db.rollback()


async def seed_database():
    db = SessionLocal()
    try:
        if db.query(Customer).count() > 0:
            logger.info("Database already seeded, skipping.")
            # Still seed support users if missing
            await _seed_support_users(db)
            return

        logger.info("Seeding database with sample data...")
        policy_counter = 1000

        for i, cdata in enumerate(CUSTOMERS):
            customer = Customer(
                email=cdata["email"],
                hashed_password=hash_password(cdata["password"]),
                full_name=cdata["full_name"],
                phone=cdata.get("phone"),
                address=cdata.get("address"),
                date_of_birth=cdata.get("date_of_birth"),
                age=cdata.get("age"),
                occupation=cdata.get("occupation"),
                risk_profile=cdata.get("risk_profile", "medium"),
                is_admin=cdata.get("is_admin", False),
            )
            db.add(customer)
            db.flush()

            if not cdata.get("is_admin"):
                for j, ptemplate in enumerate(POLICIES_TEMPLATE[:2 + (i % 3)]):
                    policy_counter += 1
                    start = date.today() + timedelta(days=ptemplate["days_offset"])
                    end = start + timedelta(days=ptemplate["duration_days"])
                    policy = Policy(
                        policy_number=f"POL-{policy_counter:05d}",
                        customer_id=customer.id,
                        policy_type=ptemplate["policy_type"],
                        coverage_amount=ptemplate["coverage_amount"],
                        premium_amount=ptemplate["premium_amount"],
                        deductible=ptemplate["deductible"],
                        start_date=start.isoformat(),
                        end_date=end.isoformat(),
                        status=ptemplate["status"],
                        description=ptemplate["description"],
                        beneficiary=ptemplate["beneficiary"],
                    )
                    db.add(policy)
                    db.flush()

                    if j < len(CLAIMS_TEMPLATE) and i % 2 == 0:
                        claim_data = CLAIMS_TEMPLATE[j % len(CLAIMS_TEMPLATE)]
                        claim = Claim(
                            claim_number=f"CLM-{policy_counter:05d}",
                            customer_id=customer.id,
                            policy_id=policy.id,
                            claim_type=claim_data["claim_type"],
                            amount=claim_data["amount"],
                            status=claim_data["status"],
                            description=claim_data["description"],
                            filed_date=claim_data["filed_date"],
                        )
                        db.add(claim)

                notif = Notification(
                    customer_id=customer.id,
                    channel="in_app",
                    subject="Welcome to Policy Renewal Agent",
                    message=f"Welcome {customer.full_name}! Your policies are set up and ready to manage.",
                    status="sent",
                    notification_type="welcome",
                    is_read=False,
                )
                db.add(notif)

        db.commit()
        logger.info("Database seeded successfully.")
        await _seed_support_users(db)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
