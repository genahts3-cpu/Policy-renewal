"""
Full production-like data seeder.
Run from backend folder: python scripts/seed_full_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta, datetime
from db.database import SessionLocal
from models.customer import Customer
from models.policy import Policy
from models.claim import Claim
from models.renewal import Renewal
from models.notification import Notification
from services.auth_service import hash_password

CUSTOMERS = [
    {"email": "admin@insurance.com",       "password": "admin123",    "full_name": "Admin User",       "phone": "+1-555-0100", "age": 35, "occupation": "Insurance Manager",  "risk_profile": "low",    "is_admin": True},
    {"email": "john.smith@email.com",       "password": "password123", "full_name": "John Smith",        "phone": "+1-555-0101", "age": 39, "occupation": "Software Engineer",  "risk_profile": "low",    "address": "123 Main St, New York, NY",      "date_of_birth": "1985-03-15"},
    {"email": "sarah.johnson@email.com",    "password": "password123", "full_name": "Sarah Johnson",     "phone": "+1-555-0102", "age": 34, "occupation": "Teacher",            "risk_profile": "low",    "address": "456 Oak Ave, Los Angeles, CA",   "date_of_birth": "1990-07-22"},
    {"email": "mike.davis@email.com",       "password": "password123", "full_name": "Mike Davis",        "phone": "+1-555-0103", "age": 49, "occupation": "Business Owner",     "risk_profile": "medium", "address": "789 Pine Rd, Chicago, IL",       "date_of_birth": "1975-11-08"},
    {"email": "emily.chen@email.com",       "password": "password123", "full_name": "Emily Chen",        "phone": "+1-555-0104", "age": 29, "occupation": "Nurse",              "risk_profile": "low",    "address": "321 Elm St, Houston, TX",        "date_of_birth": "1995-01-30"},
    {"email": "robert.wilson@email.com",    "password": "password123", "full_name": "Robert Wilson",     "phone": "+1-555-0105", "age": 55, "occupation": "Retired",            "risk_profile": "high",   "address": "654 Maple Dr, Phoenix, AZ",      "date_of_birth": "1969-05-12"},
    {"email": "lisa.martinez@email.com",    "password": "password123", "full_name": "Lisa Martinez",     "phone": "+1-555-0106", "age": 42, "occupation": "Doctor",             "risk_profile": "low",    "address": "987 Cedar Ln, Philadelphia, PA", "date_of_birth": "1982-09-18"},
    {"email": "david.brown@email.com",      "password": "password123", "full_name": "David Brown",       "phone": "+1-555-0107", "age": 31, "occupation": "Freelancer",         "risk_profile": "medium", "address": "147 Birch St, San Antonio, TX",  "date_of_birth": "1993-12-05"},
    {"email": "jennifer.taylor@email.com",  "password": "password123", "full_name": "Jennifer Taylor",   "phone": "+1-555-0108", "age": 46, "occupation": "Lawyer",             "risk_profile": "low",    "address": "258 Walnut Ave, San Diego, CA",  "date_of_birth": "1978-04-25"},
    {"email": "james.anderson@email.com",   "password": "password123", "full_name": "James Anderson",    "phone": "+1-555-0109", "age": 62, "occupation": "Consultant",         "risk_profile": "high",   "address": "369 Spruce Blvd, Dallas, TX",    "date_of_birth": "1962-08-14"},
]

POLICIES = [
    # John Smith
    {"email": "john.smith@email.com",      "type": "life",   "coverage": 500000,  "premium": 1200, "deductible": 0,    "offset": -300, "status": "active",   "beneficiary": "Spouse",   "desc": "Term life insurance providing financial protection for your family."},
    {"email": "john.smith@email.com",      "type": "health", "coverage": 100000,  "premium": 3600, "deductible": 1000, "offset": -200, "status": "active",   "beneficiary": "Self",     "desc": "Comprehensive health insurance covering medical expenses."},
    {"email": "john.smith@email.com",      "type": "auto",   "coverage": 50000,   "premium": 1800, "deductible": 500,  "offset": -350, "status": "active",   "beneficiary": "Self",     "desc": "Full coverage auto insurance for your vehicle."},
    # Sarah Johnson
    {"email": "sarah.johnson@email.com",   "type": "health", "coverage": 80000,   "premium": 2800, "deductible": 500,  "offset": -355, "status": "active",   "beneficiary": "Self",     "desc": "Individual health insurance plan with comprehensive coverage."},
    {"email": "sarah.johnson@email.com",   "type": "home",   "coverage": 250000,  "premium": 1500, "deductible": 2000, "offset": -60,  "status": "active",   "beneficiary": "Self",     "desc": "Homeowners insurance protecting your property and belongings."},
    # Mike Davis
    {"email": "mike.davis@email.com",      "type": "life",   "coverage": 1000000, "premium": 3500, "deductible": 0,    "offset": -180, "status": "active",   "beneficiary": "Family",   "desc": "Whole life insurance with investment component for business owner."},
    {"email": "mike.davis@email.com",      "type": "health", "coverage": 200000,  "premium": 6000, "deductible": 2000, "offset": -90,  "status": "active",   "beneficiary": "Family",   "desc": "Family health insurance plan with premium coverage."},
    {"email": "mike.davis@email.com",      "type": "auto",   "coverage": 75000,   "premium": 2400, "deductible": 1000, "offset": -340, "status": "active",   "beneficiary": "Self",     "desc": "Commercial auto insurance for business vehicle."},
    {"email": "mike.davis@email.com",      "type": "home",   "coverage": 500000,  "premium": 3200, "deductible": 5000, "offset": -270, "status": "active",   "beneficiary": "Self",     "desc": "High-value homeowners insurance for luxury property."},
    # Emily Chen
    {"email": "emily.chen@email.com",      "type": "health", "coverage": 90000,   "premium": 2400, "deductible": 750,  "offset": -120, "status": "active",   "beneficiary": "Self",     "desc": "Health insurance for healthcare professional."},
    {"email": "emily.chen@email.com",      "type": "auto",   "coverage": 35000,   "premium": 1200, "deductible": 500,  "offset": -30,  "status": "active",   "beneficiary": "Self",     "desc": "Standard auto insurance coverage."},
    # Robert Wilson
    {"email": "robert.wilson@email.com",   "type": "life",   "coverage": 300000,  "premium": 4800, "deductible": 0,    "offset": -400, "status": "expired",  "beneficiary": "Children", "desc": "Senior life insurance policy."},
    {"email": "robert.wilson@email.com",   "type": "health", "coverage": 150000,  "premium": 8400, "deductible": 3000, "offset": -10,  "status": "active",   "beneficiary": "Self",     "desc": "Senior health insurance with extensive coverage."},
    {"email": "robert.wilson@email.com",   "type": "home",   "coverage": 400000,  "premium": 2800, "deductible": 3000, "offset": -360, "status": "active",   "beneficiary": "Self",     "desc": "Homeowners insurance for retirement property."},
    # Lisa Martinez
    {"email": "lisa.martinez@email.com",   "type": "life",   "coverage": 750000,  "premium": 2100, "deductible": 0,    "offset": -150, "status": "active",   "beneficiary": "Spouse",   "desc": "Premium life insurance for medical professional."},
    {"email": "lisa.martinez@email.com",   "type": "health", "coverage": 200000,  "premium": 4800, "deductible": 500,  "offset": -220, "status": "active",   "beneficiary": "Family",   "desc": "Family health insurance with specialist coverage."},
    {"email": "lisa.martinez@email.com",   "type": "auto",   "coverage": 60000,   "premium": 1600, "deductible": 500,  "offset": -310, "status": "renewed",  "beneficiary": "Self",     "desc": "Auto insurance for luxury vehicle."},
    # David Brown
    {"email": "david.brown@email.com",     "type": "health", "coverage": 60000,   "premium": 1800, "deductible": 1500, "offset": -45,  "status": "active",   "beneficiary": "Self",     "desc": "Basic health insurance for freelancer."},
    {"email": "david.brown@email.com",     "type": "auto",   "coverage": 25000,   "premium": 900,  "deductible": 1000, "offset": -200, "status": "active",   "beneficiary": "Self",     "desc": "Economy auto insurance coverage."},
    # Jennifer Taylor
    {"email": "jennifer.taylor@email.com", "type": "life",   "coverage": 600000,  "premium": 1800, "deductible": 0,    "offset": -240, "status": "active",   "beneficiary": "Children", "desc": "Term life insurance for legal professional."},
    {"email": "jennifer.taylor@email.com", "type": "health", "coverage": 120000,  "premium": 3200, "deductible": 1000, "offset": -330, "status": "active",   "beneficiary": "Family",   "desc": "Comprehensive family health insurance."},
    {"email": "jennifer.taylor@email.com", "type": "home",   "coverage": 350000,  "premium": 2200, "deductible": 2500, "offset": -15,  "status": "active",   "beneficiary": "Self",     "desc": "Homeowners insurance for suburban property."},
    # James Anderson
    {"email": "james.anderson@email.com",  "type": "life",   "coverage": 200000,  "premium": 6000, "deductible": 0,    "offset": -380, "status": "expired",  "beneficiary": "Spouse",   "desc": "Senior life insurance policy."},
    {"email": "james.anderson@email.com",  "type": "health", "coverage": 180000,  "premium": 9600, "deductible": 4000, "offset": -20,  "status": "active",   "beneficiary": "Self",     "desc": "Senior comprehensive health insurance."},
    {"email": "james.anderson@email.com",  "type": "auto",   "coverage": 40000,   "premium": 2800, "deductible": 1500, "offset": -290, "status": "active",   "beneficiary": "Self",     "desc": "Senior auto insurance with roadside assistance."},
]

CLAIMS = [
    {"email": "john.smith@email.com",      "pidx": 1,  "type": "medical",         "amount": 2500,  "status": "approved", "desc": "Emergency room visit and treatment",        "filed": "2025-06-15"},
    {"email": "john.smith@email.com",      "pidx": 2,  "type": "auto_accident",   "amount": 4200,  "status": "approved", "desc": "Minor collision repair",                    "filed": "2025-08-20"},
    {"email": "sarah.johnson@email.com",   "pidx": 3,  "type": "medical",         "amount": 1800,  "status": "approved", "desc": "Specialist consultation and tests",         "filed": "2025-09-10"},
    {"email": "mike.davis@email.com",      "pidx": 6,  "type": "medical",         "amount": 8500,  "status": "approved", "desc": "Surgery and hospitalization",               "filed": "2025-07-05"},
    {"email": "mike.davis@email.com",      "pidx": 7,  "type": "auto_accident",   "amount": 12000, "status": "approved", "desc": "Major collision - vehicle totaled",         "filed": "2025-05-18"},
    {"email": "mike.davis@email.com",      "pidx": 8,  "type": "property_damage", "amount": 15000, "status": "approved", "desc": "Fire damage to home office",                "filed": "2025-10-22"},
    {"email": "robert.wilson@email.com",   "pidx": 12, "type": "medical",         "amount": 22000, "status": "approved", "desc": "Cardiac procedure and recovery",            "filed": "2025-04-12"},
    {"email": "robert.wilson@email.com",   "pidx": 12, "type": "medical",         "amount": 5500,  "status": "approved", "desc": "Follow-up treatments and medication",       "filed": "2025-08-30"},
    {"email": "robert.wilson@email.com",   "pidx": 13, "type": "property_damage", "amount": 8000,  "status": "pending",  "desc": "Storm damage to roof and windows",          "filed": "2025-11-01"},
    {"email": "emily.chen@email.com",      "pidx": 9,  "type": "medical",         "amount": 3200,  "status": "approved", "desc": "Dental surgery and treatment",              "filed": "2025-07-20"},
    {"email": "lisa.martinez@email.com",   "pidx": 15, "type": "medical",         "amount": 1200,  "status": "approved", "desc": "Annual health checkup and tests",           "filed": "2025-06-01"},
    {"email": "james.anderson@email.com",  "pidx": 23, "type": "medical",         "amount": 35000, "status": "approved", "desc": "Hip replacement surgery",                   "filed": "2025-03-15"},
    {"email": "james.anderson@email.com",  "pidx": 23, "type": "medical",         "amount": 9000,  "status": "approved", "desc": "Physical therapy and rehabilitation",       "filed": "2025-06-20"},
    {"email": "james.anderson@email.com",  "pidx": 24, "type": "auto_accident",   "amount": 6500,  "status": "pending",  "desc": "Rear-end collision damage",                 "filed": "2025-11-10"},
    {"email": "david.brown@email.com",     "pidx": 17, "type": "medical",         "amount": 900,   "status": "approved", "desc": "Urgent care visit",                         "filed": "2025-09-05"},
    {"email": "jennifer.taylor@email.com", "pidx": 20, "type": "medical",         "amount": 4500,  "status": "approved", "desc": "Maternity care and delivery",               "filed": "2025-08-14"},
]

RENEWALS = [
    {"email": "john.smith@email.com",      "pidx": 0,  "score": 0.95, "premium": 1200,  "status": "completed", "reason": "Low risk profile, No claims on life policy, Affordable premium",                    "msg": "Your life insurance policy is an excellent value. We recommend renewing to keep your family protected."},
    {"email": "sarah.johnson@email.com",   "pidx": 3,  "score": 0.88, "premium": 2900,  "status": "pending",   "reason": "Policy expiring in 10 days, Good claims history, Competitive premium",              "msg": "Your health insurance is expiring very soon. Renewing now ensures no gap in your medical coverage."},
    {"email": "mike.davis@email.com",      "pidx": 5,  "score": 0.72, "premium": 3800,  "status": "pending",   "reason": "Multiple claims history, High coverage value, Business continuity",                  "msg": "Despite recent claims, your life insurance remains important for your family's financial security."},
    {"email": "robert.wilson@email.com",   "pidx": 11, "score": 0.60, "premium": 5200,  "status": "declined",  "reason": "High risk profile, Multiple large claims, Premium increase required",                "msg": "Due to your claims history, we recommend reviewing your coverage options with an advisor."},
    {"email": "lisa.martinez@email.com",   "pidx": 16, "score": 0.98, "premium": 1600,  "status": "completed", "reason": "Excellent risk profile, No claims, Professional discount applied",                   "msg": "As a healthcare professional with an excellent record, you qualify for our preferred rate of Rs.1,600/year."},
    {"email": "james.anderson@email.com",  "pidx": 23, "score": 0.55, "premium": 10200, "status": "pending",   "reason": "Senior age bracket, High claims amount, Comprehensive coverage needed",              "msg": "Your health coverage is critical given your medical history. We strongly recommend renewal."},
    {"email": "jennifer.taylor@email.com", "pidx": 19, "score": 0.91, "premium": 1850,  "status": "pending",   "reason": "Low risk profile, Family coverage, Competitive rate",                               "msg": "Your life insurance provides excellent protection for your family at a competitive rate."},
    {"email": "emily.chen@email.com",      "pidx": 9,  "score": 0.85, "premium": 2500,  "status": "pending",   "reason": "Healthcare professional discount, Good health record, Comprehensive coverage",       "msg": "As a nurse, you qualify for our healthcare professional discount on your health insurance."},
]

NOTIFICATIONS = [
    {"email": "john.smith@email.com",      "channel": "in_app", "subject": "Policy Renewal Confirmed",        "message": "Your Life Insurance policy has been successfully renewed for another year.",                          "type": "renewal_confirmed", "read": True},
    {"email": "john.smith@email.com",      "channel": "in_app", "subject": "Claim Approved - Rs.2,500",       "message": "Your medical claim has been approved and will be processed within 3-5 business days.",                "type": "claim_update",      "read": True},
    {"email": "sarah.johnson@email.com",   "channel": "in_app", "subject": "Policy Expiring in 10 Days",     "message": "Your Health Insurance policy is expiring soon. Please renew to avoid a coverage gap.",               "type": "expiry_warning",    "read": False},
    {"email": "sarah.johnson@email.com",   "channel": "email",  "subject": "Action Required: Policy Renewal", "message": "Your health insurance policy expires soon. Renew now to maintain your coverage.",                   "type": "renewal_reminder",  "read": False},
    {"email": "mike.davis@email.com",      "channel": "in_app", "subject": "Claim Approved - Rs.12,000",      "message": "Your auto insurance claim for vehicle collision has been approved. Payment will be issued.",         "type": "claim_update",      "read": True},
    {"email": "mike.davis@email.com",      "channel": "in_app", "subject": "AI Renewal Recommendation Ready", "message": "Your life insurance renewal recommendation is ready. Review your personalized AI analysis.",         "type": "renewal_reminder",  "read": False},
    {"email": "emily.chen@email.com",      "channel": "in_app", "subject": "Welcome to Policy Renewal Agent", "message": "Welcome Emily! Your policies are set up. Use the AI assistant for any questions.",                  "type": "welcome",           "read": False},
    {"email": "robert.wilson@email.com",   "channel": "in_app", "subject": "Life Policy Expired",             "message": "Your life insurance policy has expired. Please contact us to discuss renewal options.",              "type": "expiry_warning",    "read": False},
    {"email": "robert.wilson@email.com",   "channel": "in_app", "subject": "Claim Under Review - Rs.8,000",   "message": "Your property damage claim is currently under review. Expected decision within 5 business days.",   "type": "claim_update",      "read": False},
    {"email": "lisa.martinez@email.com",   "channel": "in_app", "subject": "Policy Renewed - Preferred Rate", "message": "Your auto insurance has been renewed at our preferred professional rate of Rs.1,600/year.",          "type": "renewal_confirmed", "read": True},
    {"email": "james.anderson@email.com",  "channel": "in_app", "subject": "Life Policy Expired",             "message": "Your life insurance policy has expired. Immediate action required to restore coverage.",             "type": "expiry_warning",    "read": False},
    {"email": "james.anderson@email.com",  "channel": "in_app", "subject": "Claim Approved - Rs.35,000",      "message": "Your hip replacement surgery claim has been approved. Full reimbursement will be processed.",        "type": "claim_update",      "read": True},
    {"email": "jennifer.taylor@email.com", "channel": "in_app", "subject": "Claim Approved - Maternity",      "message": "Your maternity care claim of Rs.4,500 has been approved. Payment processing in 3 business days.",   "type": "claim_update",      "read": True},
    {"email": "david.brown@email.com",     "channel": "in_app", "subject": "Welcome to Policy Renewal Agent", "message": "Welcome David! Your policies are active. Chat with our AI assistant for any questions.",            "type": "welcome",           "read": False},
    {"email": "jennifer.taylor@email.com", "channel": "in_app", "subject": "AI Renewal Recommendation Ready", "message": "Your life insurance renewal recommendation is ready. Click to review and confirm.",                  "type": "renewal_reminder",  "read": False},
    {"email": "emily.chen@email.com",      "channel": "in_app", "subject": "AI Renewal Recommendation Ready", "message": "Your health insurance renewal recommendation is ready with a special professional discount.",         "type": "renewal_reminder",  "read": False},
]


def seed():
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Notification).delete()
        db.query(Renewal).delete()
        db.query(Claim).delete()
        db.query(Policy).delete()
        db.query(Customer).delete()
        db.commit()
        print("Cleared existing data")

        # Create customers
        customer_map = {}
        for cdata in CUSTOMERS:
            c = Customer(
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
            db.add(c)
            db.flush()
            customer_map[cdata["email"]] = c
        db.commit()
        print(f"Created {len(CUSTOMERS)} customers")

        # Create policies
        policy_list = []
        for i, pdata in enumerate(POLICIES):
            customer = customer_map[pdata["email"]]
            start = date.today() + timedelta(days=pdata["offset"])
            end = start + timedelta(days=365)
            p = Policy(
                policy_number=f"POL-{2000 + i:05d}",
                customer_id=customer.id,
                policy_type=pdata["type"],
                coverage_amount=float(pdata["coverage"]),
                premium_amount=float(pdata["premium"]),
                deductible=float(pdata["deductible"]),
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                status=pdata["status"],
                description=pdata["desc"],
                beneficiary=pdata["beneficiary"],
            )
            db.add(p)
            db.flush()
            policy_list.append(p)
        db.commit()
        print(f"Created {len(POLICIES)} policies")

        # Create claims
        for i, cdata in enumerate(CLAIMS):
            customer = customer_map[cdata["email"]]
            policy = policy_list[cdata["pidx"]]
            cl = Claim(
                claim_number=f"CLM-{3000 + i:05d}",
                customer_id=customer.id,
                policy_id=policy.id,
                claim_type=cdata["type"],
                amount=float(cdata["amount"]),
                status=cdata["status"],
                description=cdata["desc"],
                filed_date=cdata["filed"],
            )
            db.add(cl)
        db.commit()
        print(f"Created {len(CLAIMS)} claims")

        # Create renewals
        for rdata in RENEWALS:
            customer = customer_map[rdata["email"]]
            policy = policy_list[rdata["pidx"]]
            completed_at = datetime.utcnow() if rdata["status"] == "completed" else None
            r = Renewal(
                policy_id=policy.id,
                customer_id=customer.id,
                renewal_date=date.today().isoformat(),
                new_premium=float(rdata["premium"]),
                new_end_date=(date.today() + timedelta(days=365)).isoformat(),
                status=rdata["status"],
                recommendation_score=rdata["score"],
                recommendation_reason=rdata["reason"],
                ai_recommendation=rdata["msg"],
                completed_at=completed_at,
            )
            db.add(r)
            if rdata["status"] == "completed":
                policy.status = "renewed"
                policy.premium_amount = float(rdata["premium"])
                policy.end_date = (date.today() + timedelta(days=365)).isoformat()
        db.commit()
        print(f"Created {len(RENEWALS)} renewals")

        # Create notifications
        for ndata in NOTIFICATIONS:
            customer = customer_map[ndata["email"]]
            n = Notification(
                customer_id=customer.id,
                channel=ndata["channel"],
                subject=ndata["subject"],
                message=ndata["message"],
                status="sent",
                notification_type=ndata["type"],
                is_read=ndata["read"],
            )
            db.add(n)
        db.commit()
        print(f"Created {len(NOTIFICATIONS)} notifications")

        print("\n🎉 Database seeded successfully with production-like data!")
        print("\nDemo Accounts:")
        print("  admin@insurance.com       / admin123")
        print("  john.smith@email.com      / password123")
        print("  sarah.johnson@email.com   / password123  (policy expiring soon!)")
        print("  mike.davis@email.com      / password123  (multiple claims)")
        print("  emily.chen@email.com      / password123")
        print("  robert.wilson@email.com   / password123  (expired policies)")
        print("  lisa.martinez@email.com   / password123  (renewed policy)")
        print("  david.brown@email.com     / password123")
        print("  jennifer.taylor@email.com / password123")
        print("  james.anderson@email.com  / password123  (high risk, large claims)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
