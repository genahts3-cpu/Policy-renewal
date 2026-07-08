"""
Seeds the RAG knowledge base with policy documents.
Run from backend/ directory: python scripts/seed_policies.py
"""
import os
import sys

# Must run from backend directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

POLICIES = {
    "Life Insurance Policy": """
LIFE INSURANCE POLICY - TERM LIFE COVERAGE

1. COVERAGE OVERVIEW
Term life insurance provides a death benefit to your designated beneficiaries in the event of your death during the policy term.
Coverage amounts range from $100,000 to $5,000,000.

2. PREMIUM STRUCTURE
Premiums are calculated based on age, health status, coverage amount, and policy term (10, 20, or 30 years).
Annual premiums range from $500 to $5,000 for standard coverage.
Premiums are locked in at the time of policy issuance.

3. RENEWAL TERMS
At the end of your policy term, you may renew for another term (premiums recalculated based on current age),
convert to a permanent life insurance policy, or allow the policy to lapse.
Renewal applications must be submitted 60 days before policy expiration.
No medical exam is required for renewal if the policy has been in good standing.

4. BENEFICIARY DESIGNATION
You may designate one or more beneficiaries. Changes can be made at any time by submitting a written request.

5. EXCLUSIONS
This policy does not cover death resulting from suicide within the first two years,
death during participation in illegal activities, or war/acts of terrorism.

6. CLAIMS PROCESS
Notify the insurance company within 30 days. Submit a certified death certificate and complete the beneficiary claim form.
Claims are typically processed within 30 business days.

7. GRACE PERIOD
A 31-day grace period is provided for premium payments. The policy remains in force during this period.

8. TAX BENEFITS
Death benefits are generally income-tax-free for beneficiaries.
Cash value growth in permanent policies is tax-deferred.
""",

    "Health Insurance Policy": """
HEALTH INSURANCE POLICY - COMPREHENSIVE COVERAGE

1. COVERAGE OVERVIEW
This policy covers hospitalization and surgery, emergency room visits, prescription medications,
preventive care and wellness visits, mental health services, and maternity and newborn care.

2. DEDUCTIBLES AND COPAYMENTS
Annual Deductible: $1,000 - $5,000 (varies by plan)
Out-of-Pocket Maximum: $7,500 individual / $15,000 family
Copayments: Primary Care $25, Specialist $50, Emergency Room $250, Urgent Care $75
Generic Prescriptions: $10, Brand Prescriptions: $40

3. NETWORK PROVIDERS
In-Network: Full coverage after deductible and copayment.
Out-of-Network: 60% coverage after higher deductible.
Emergency care is covered regardless of network status.

4. PREVENTIVE CARE
The following preventive services are covered at 100% with no deductible:
Annual physical examinations, immunizations, cancer screenings, blood pressure and cholesterol screenings.

5. PRESCRIPTION DRUG COVERAGE
Tier 1 Generic: $10 copay. Tier 2 Preferred Brand: $40 copay.
Tier 3 Non-Preferred Brand: $80 copay. Tier 4 Specialty: 20% coinsurance up to $250/month.

6. RENEWAL PROCESS
Annual renewal occurs on your policy anniversary date.
Premium adjustments are based on age progression, claims history, and regional healthcare cost changes.
Renewal notices are sent 90 days before expiration. Early renewal discounts of up to 5% are available.

7. MENTAL HEALTH BENEFITS
Mental health services are covered at the same level as medical services including
inpatient psychiatric care, outpatient therapy, substance abuse treatment, and crisis intervention.

8. APPEALS PROCESS
Level 1: Internal appeal within 30 days of denial.
Level 2: External review by independent organization.
Level 3: State insurance commissioner complaint.
""",

    "Auto Insurance Policy": """
AUTO INSURANCE POLICY - COMPREHENSIVE COVERAGE

1. COVERAGE TYPES
Liability: Bodily Injury $100,000 per person / $300,000 per accident. Property Damage $100,000 per accident.
Collision: Covers damage to your vehicle from collisions. Deductible: $500 standard.
Comprehensive: Covers non-collision damage (theft, weather, vandalism). Deductible: $250 standard.
Uninsured/Underinsured Motorist: $100,000 per person / $300,000 per accident.

2. PREMIUM FACTORS
Your premium is calculated based on driving record, vehicle make/model/year, annual mileage,
geographic location, age and driving experience, and credit score.

3. DISCOUNTS AVAILABLE
Safe Driver Discount: 10-15% for clean driving record.
Multi-Policy Discount: 5-10% when bundled with home insurance.
Good Student Discount: 8% for students with B average or better.
Anti-Theft Device: 5% discount. Defensive Driving Course: 5% discount.
Loyalty Discount: 3% per year up to 15%.

4. CLAIMS PROCESS
Ensure safety and call emergency services if needed. Document the scene with photos.
Exchange information with other parties. File a police report if required.
Contact us within 24 hours. Work with our assigned claims adjuster.

5. RENTAL CAR COVERAGE
Up to $50/day rental reimbursement while your vehicle is being repaired. Maximum 30 days per claim.

6. ROADSIDE ASSISTANCE
Included with comprehensive coverage: towing up to 25 miles, battery jump-start,
flat tire change, lockout service, and fuel delivery up to 2 gallons.

7. RENEWAL TERMS
Auto policies renew every 6 or 12 months. Premium changes at renewal are based on
updated driving record, claims filed, changes in vehicle value, and market rate adjustments.
Renewal notices sent 30 days before expiration.

8. ACCIDENT FORGIVENESS
After 5 years of claim-free driving, your first at-fault accident will not result in a premium increase.
""",

    "Home Insurance Policy": """
HOME INSURANCE POLICY - HOMEOWNERS COVERAGE (HO-3)

1. COVERAGE OVERVIEW
Dwelling Coverage (A): Covers the structure of your home at replacement cost value.
Other Structures (B): Detached garages, fences, sheds - 10% of dwelling coverage.
Personal Property (C): Furniture, electronics, clothing, appliances - 50-70% of dwelling coverage.
Loss of Use (D): Additional living expenses if home is uninhabitable - 20% of dwelling coverage up to 12 months.

2. LIABILITY PROTECTION
Personal Liability (E): $100,000 - $500,000 coverage. Covers injuries on your property. Legal defense included.
Medical Payments (F): $1,000 - $5,000 per person. Covers minor injuries regardless of fault.

3. COVERED PERILS
Fire and smoke, lightning, windstorm and hail, explosion, riot, aircraft and vehicle damage,
vandalism, theft, falling objects, weight of ice/snow/sleet, water damage from plumbing failures.

4. EXCLUSIONS
This policy does NOT cover flood damage (requires separate flood insurance),
earthquake damage (requires separate earthquake insurance), normal wear and tear,
pest infestations, mold (unless from covered water damage), or intentional acts.

5. DEDUCTIBLES
Standard Deductible: $1,000 - $2,500. Hurricane/Wind Deductible: 1-5% of dwelling value.

6. PREMIUM FACTORS
Home age and construction type, location and proximity to fire station, claims history,
credit score, security systems installed, roof age and condition, and coverage amounts selected.

7. RENEWAL PROCESS
Annual renewal with premium adjustments based on inflation, construction cost changes,
claims filed, property improvements, and market conditions.
Renewal discounts for claim-free years: 5% per year up to 20%.

8. DISCOUNTS
New Home Discount: 8% for homes under 10 years old. Security System: 5%.
Smoke Detectors: 2%. Multi-Policy Bundle: 10-15%. Claim-Free: 5% per year.
"""
}


def main():
    print("Seeding RAG knowledge base with policy documents...")
    try:
        from rag.rag_engine import ingest_text, get_vectorstore
        # Check if already seeded
        vs = get_vectorstore()
        existing = vs._collection.count()
        if existing > 0:
            print(f"Knowledge base already has {existing} chunks. Skipping.")
            return
        total = 0
        for name, content in POLICIES.items():
            chunks = ingest_text(content.strip(), metadata={"source": name})
            total += chunks
            print(f"  Ingested {chunks} chunks from: {name}")
        print(f"RAG knowledge base ready with {total} total chunks.")
    except Exception as e:
        print(f"Warning: RAG seeding failed: {e}")
        print("The app will still work - RAG answers may be limited.")


if __name__ == "__main__":
    main()
