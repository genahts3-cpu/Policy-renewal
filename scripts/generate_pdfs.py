"""
Generate sample PDF policy documents for RAG ingestion.
Run: python scripts/generate_pdfs.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

POLICY_TEXTS = {
    "life_insurance_policy.txt": """
LIFE INSURANCE POLICY DOCUMENT
Policy Type: Term Life Insurance
Issuer: SecureLife Insurance Company

1. COVERAGE OVERVIEW
This Term Life Insurance policy provides a death benefit to your designated beneficiaries
in the event of your death during the policy term. Coverage amounts range from $100,000
to $5,000,000 depending on your selected plan.

2. PREMIUM STRUCTURE
Premiums are calculated based on:
- Age at time of application
- Health status and medical history
- Coverage amount selected
- Policy term (10, 20, or 30 years)
- Lifestyle factors (smoking status, occupation)

Annual premiums typically range from $500 to $5,000 for standard coverage.
Premiums are locked in at the time of policy issuance and do not increase during the term.

3. RENEWAL TERMS
At the end of your policy term, you have the option to:
- Renew for another term (premiums will be recalculated based on current age)
- Convert to a permanent life insurance policy
- Allow the policy to lapse

Renewal applications must be submitted 60 days before policy expiration.
No medical exam is required for renewal if the policy has been in good standing.

4. BENEFICIARY DESIGNATION
You may designate one or more beneficiaries. Primary beneficiaries receive the death benefit.
Contingent beneficiaries receive the benefit if primary beneficiaries predecease you.
Beneficiary changes can be made at any time by submitting a written request.

5. EXCLUSIONS
This policy does not cover death resulting from:
- Suicide within the first two years of the policy
- Death during participation in illegal activities
- War or acts of terrorism (in certain jurisdictions)

6. CLAIMS PROCESS
To file a death benefit claim:
1. Notify the insurance company within 30 days
2. Submit a certified death certificate
3. Complete the beneficiary claim form
4. Provide proof of identity for all beneficiaries
Claims are typically processed within 30 business days.

7. GRACE PERIOD
A 31-day grace period is provided for premium payments. The policy remains in force
during this period. If payment is not received within the grace period, the policy lapses.

8. REINSTATEMENT
A lapsed policy may be reinstated within 3 years by:
- Paying all overdue premiums with interest
- Providing evidence of insurability
- Completing a new application

9. POLICY LOANS
Permanent life policies accumulate cash value that can be borrowed against.
Loan interest rates are typically 5-8% annually.
Outstanding loans reduce the death benefit if not repaid.

10. TAX BENEFITS
Death benefits are generally income-tax-free for beneficiaries.
Cash value growth in permanent policies is tax-deferred.
Consult a tax advisor for your specific situation.
""",

    "health_insurance_policy.txt": """
HEALTH INSURANCE POLICY DOCUMENT
Policy Type: Comprehensive Health Insurance
Issuer: HealthGuard Insurance Company

1. COVERAGE OVERVIEW
This Comprehensive Health Insurance policy covers medical expenses including:
- Hospitalization and surgery
- Emergency room visits
- Prescription medications
- Preventive care and wellness visits
- Mental health services
- Maternity and newborn care

2. DEDUCTIBLES AND COPAYMENTS
Annual Deductible: $1,000 - $5,000 (varies by plan)
Out-of-Pocket Maximum: $7,500 individual / $15,000 family
Copayments:
- Primary Care Visit: $25
- Specialist Visit: $50
- Emergency Room: $250
- Urgent Care: $75
- Generic Prescriptions: $10
- Brand Prescriptions: $40

3. NETWORK PROVIDERS
In-Network: Full coverage after deductible and copayment
Out-of-Network: 60% coverage after higher deductible
Emergency care is covered regardless of network status.

4. PREVENTIVE CARE
The following preventive services are covered at 100% (no deductible):
- Annual physical examinations
- Immunizations and vaccines
- Cancer screenings (mammograms, colonoscopies)
- Blood pressure and cholesterol screenings
- Diabetes screenings

5. PRESCRIPTION DRUG COVERAGE
Tier 1 (Generic): $10 copay
Tier 2 (Preferred Brand): $40 copay
Tier 3 (Non-Preferred Brand): $80 copay
Tier 4 (Specialty): 20% coinsurance up to $250/month

6. MENTAL HEALTH BENEFITS
Mental health services are covered at the same level as medical services:
- Inpatient psychiatric care
- Outpatient therapy sessions
- Substance abuse treatment
- Crisis intervention services

7. RENEWAL PROCESS
Annual renewal occurs on your policy anniversary date.
Premium adjustments are based on:
- Age progression
- Claims history
- Regional healthcare cost changes
- Plan modifications

Renewal notices are sent 90 days before expiration.
Early renewal discounts of up to 5% are available.

8. PRE-AUTHORIZATION REQUIREMENTS
The following services require pre-authorization:
- Elective surgeries
- MRI and CT scans
- Specialist referrals (HMO plans)
- Inpatient admissions (non-emergency)
- Durable medical equipment over $500

9. APPEALS PROCESS
If a claim is denied, you have the right to appeal:
Level 1: Internal appeal within 30 days of denial
Level 2: External review by independent organization
Level 3: State insurance commissioner complaint

10. COBRA CONTINUATION
If you lose coverage due to qualifying events, you may continue coverage
under COBRA for up to 18 months (36 months in some cases).
You will be responsible for the full premium plus a 2% administrative fee.
""",

    "auto_insurance_policy.txt": """
AUTO INSURANCE POLICY DOCUMENT
Policy Type: Comprehensive Auto Insurance
Issuer: DriveSecure Insurance Company

1. COVERAGE TYPES
Liability Coverage:
- Bodily Injury: $100,000 per person / $300,000 per accident
- Property Damage: $100,000 per accident

Collision Coverage:
- Covers damage to your vehicle from collisions
- Deductible: $500 (standard)

Comprehensive Coverage:
- Covers non-collision damage (theft, weather, vandalism)
- Deductible: $250 (standard)

Uninsured/Underinsured Motorist:
- $100,000 per person / $300,000 per accident

2. PREMIUM FACTORS
Your premium is calculated based on:
- Driving record (accidents, violations)
- Vehicle make, model, and year
- Annual mileage
- Geographic location
- Age and driving experience
- Credit score (where permitted)
- Coverage levels selected

3. DISCOUNTS AVAILABLE
- Safe Driver Discount: 10-15% for clean driving record
- Multi-Policy Discount: 5-10% when bundled with home insurance
- Good Student Discount: 8% for students with B average or better
- Anti-Theft Device: 5% discount
- Defensive Driving Course: 5% discount
- Loyalty Discount: 3% per year up to 15%

4. CLAIMS PROCESS
To file an auto claim:
1. Ensure safety and call emergency services if needed
2. Document the scene with photos
3. Exchange information with other parties
4. File a police report if required
5. Contact us within 24 hours
6. Work with our assigned claims adjuster

5. RENTAL CAR COVERAGE
While your vehicle is being repaired, we provide:
- Up to $50/day rental reimbursement
- Maximum 30 days per claim
- Must use approved rental agencies

6. ROADSIDE ASSISTANCE
Included with comprehensive coverage:
- Towing up to 25 miles
- Battery jump-start
- Flat tire change
- Lockout service
- Fuel delivery (up to 2 gallons)

7. RENEWAL TERMS
Auto policies renew every 6 or 12 months.
Premium changes at renewal are based on:
- Updated driving record
- Claims filed during the policy period
- Changes in vehicle value
- Market rate adjustments

Renewal notices sent 30 days before expiration.
Online renewal available through customer portal.

8. POLICY CANCELLATION
You may cancel at any time with written notice.
Refund of unearned premium will be issued within 30 days.
We may cancel for non-payment, fraud, or license suspension.

9. EXCLUSIONS
This policy does not cover:
- Intentional damage
- Racing or speed contests
- Using vehicle for commercial purposes (without endorsement)
- Wear and tear or mechanical breakdown
- Personal belongings in the vehicle

10. ACCIDENT FORGIVENESS
After 5 years of claim-free driving, your first at-fault accident
will not result in a premium increase at renewal.
""",

    "home_insurance_policy.txt": """
HOME INSURANCE POLICY DOCUMENT
Policy Type: Homeowners Insurance (HO-3)
Issuer: HomeShield Insurance Company

1. COVERAGE OVERVIEW
Dwelling Coverage (Coverage A):
- Covers the structure of your home
- Replacement cost value basis
- Coverage amount: Based on rebuild cost estimate

Other Structures (Coverage B):
- Detached garages, fences, sheds
- 10% of dwelling coverage

Personal Property (Coverage C):
- Furniture, electronics, clothing, appliances
- 50-70% of dwelling coverage
- Replacement cost or actual cash value

Loss of Use (Coverage D):
- Additional living expenses if home is uninhabitable
- 20% of dwelling coverage, up to 12 months

2. LIABILITY PROTECTION
Personal Liability (Coverage E):
- $100,000 - $500,000 coverage
- Covers injuries on your property
- Legal defense costs included

Medical Payments (Coverage F):
- $1,000 - $5,000 per person
- Covers minor injuries regardless of fault

3. COVERED PERILS
This policy covers damage from:
- Fire and smoke
- Lightning
- Windstorm and hail
- Explosion
- Riot or civil commotion
- Aircraft and vehicle damage
- Vandalism and malicious mischief
- Theft
- Falling objects
- Weight of ice, snow, or sleet
- Water damage from plumbing failures

4. EXCLUSIONS
This policy does NOT cover:
- Flood damage (requires separate flood insurance)
- Earthquake damage (requires separate earthquake insurance)
- Normal wear and tear
- Pest infestations
- Mold (unless from covered water damage)
- Power failure
- Intentional acts

5. DEDUCTIBLES
Standard Deductible: $1,000 - $2,500
Hurricane/Wind Deductible: 1-5% of dwelling value
Earthquake Deductible (if endorsed): 10-15% of dwelling value

6. PREMIUM FACTORS
- Home age and construction type
- Location and proximity to fire station
- Claims history
- Credit score
- Security systems installed
- Roof age and condition
- Coverage amounts selected

7. RENEWAL PROCESS
Annual renewal with premium adjustments based on:
- Inflation and construction cost changes
- Claims filed during policy period
- Property improvements or changes
- Market conditions

Renewal discounts for claim-free years: 5% per year up to 20%.

8. CLAIMS PROCESS
1. Ensure safety of all occupants
2. Prevent further damage (document mitigation efforts)
3. Document all damage with photos and video
4. File claim within 60 days of loss
5. Work with assigned adjuster
6. Keep receipts for all expenses

9. REPLACEMENT COST VS ACTUAL CASH VALUE
Replacement Cost: Pays to replace item with new equivalent
Actual Cash Value: Replacement cost minus depreciation
We recommend replacement cost coverage for maximum protection.

10. DISCOUNTS
- New Home Discount: 8% for homes under 10 years old
- Security System: 5% discount
- Smoke Detectors: 2% discount
- Multi-Policy Bundle: 10-15% discount
- Claim-Free Discount: 5% per year
- Loyalty Discount: 3% per year up to 12%
"""
}


def generate_text_files():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    for filename, content in POLICY_TEXTS.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(content.strip())
        print(f"Created: {filepath}")


def ingest_to_rag():
    """Ingest the text files into ChromaDB RAG."""
    import asyncio
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))
    sys.path.insert(0, os.getcwd())

    from rag.rag_engine import ingest_text

    for filename, content in POLICY_TEXTS.items():
        policy_name = filename.replace(".txt", "").replace("_", " ").title()
        chunks = ingest_text(content.strip(), metadata={"source": policy_name, "filename": filename})
        print(f"Ingested {chunks} chunks from {filename}")


if __name__ == "__main__":
    generate_text_files()
    print("\nText policy files generated.")
    print("To ingest into RAG, run from backend/: python ../scripts/generate_pdfs.py ingest")

    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        ingest_to_rag()
        print("RAG ingestion complete.")
