"""
src/data_generator.py
─────────────────────
Generates realistic randomized invoice data:
  - Law firm names, attorney names, client names
  - Randomized hourly rates, hours, amounts
  - Case types, legal task descriptions
  - Dates, addresses, emails, IRS numbers
"""

import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker("en_US")

# ─────────────────────────────────────────────────────────────
# STATIC POOLS
# ─────────────────────────────────────────────────────────────

LAW_FIRMS = [
    ("RICHARD & MATTHEWS LLP",    "PO BOX 657778", "Dallas"),
    ("BLACKSTONE HART COUNSEL LLP","PO BOX 556677", "Philadelphia"),
    ("SULLIVAN & CROMWELL LLP",   "PO BOX 112233", "New York"),
    ("MORRISON & FOERSTER LLP",   "PO BOX 998877", "San Francisco"),
    ("DAVIS POLK & WARDWELL LLP", "PO BOX 445566", "New York"),
    ("LATHAM & WATKINS LLP",      "PO BOX 334455", "Los Angeles"),
    ("SKADDEN ARPS LLP",          "PO BOX 667788", "Chicago"),
    ("KIRKLAND & ELLIS LLP",      "PO BOX 223344", "Chicago"),
    ("WEIL GOTSHAL & MANGES LLP", "PO BOX 889900", "Houston"),
    ("CLEARY GOTTLIEB LLP",       "PO BOX 778899", "Washington DC"),
]

CASE_TYPES = [
    "Robotex Investment", "Merger & Acquisition Advisory",
    "FDA Regulatory Compliance", "IP Licensing Agreement",
    "Securities Litigation Defense", "Employment Contract Dispute",
    "Real Estate Transaction", "Tax Restructuring Advisory",
    "Corporate Governance Review", "Patent Infringement Defense",
    "Data Privacy Compliance", "Cross-Border Investment",
    "Joint Venture Formation", "Debt Restructuring",
    "Environmental Compliance", "Antitrust Investigation",
]

ATTORNEY_FIRSTS  = [
    "Matthew", "Joey", "Monica", "Rachel", "Ross", "Chandler",
    "Nathaniel", "Sophia", "Franklin", "Jennifer", "Michael",
    "Sarah", "David", "Emily", "Robert", "Jessica", "James",
    "Kapil", "Priya", "Arjun", "Neha", "Vikram", "Anita",
    "William", "Elizabeth", "Charles", "Margaret", "Thomas",
]
ATTORNEY_MIDDLES = ["T.", "J.", "C.", "A.", "R.", "P.", "K.", "M.", "B.", "L.", "H.", "D."]
ATTORNEY_LASTS   = [
    "Perry", "Tribiani", "Geller", "Green", "Buffay", "Bing",
    "Blackstone", "Hart", "Abara", "Patel", "Cohen", "Watson",
    "Reynolds", "Torres", "Martinez", "Chen", "Williams",
    "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore",
    "Taylor", "Anderson", "Jackson", "White", "Harris", "Martin",
]

HOURLY_RATES = [325, 350, 390, 420, 450, 480, 510, 530, 560, 580,
                600, 620, 650, 680, 720, 750, 800, 850, 875, 950]

LEGAL_TASKS = [
    "Conducted a detailed review of the proposed {case} structure and held an initial strategic discussion with the client to align on objectives and legal considerations.",
    "Drafted the preliminary {case} agreement, including key commercial terms, and prepared internal notes for further legal review and partner feedback.",
    "Conducted comprehensive legal research on applicable regulatory frameworks governing {case} and summarized findings for the team.",
    "Reviewed and revised the {case} agreement to incorporate client feedback and ensure alignment with legal and business requirements.",
    "Participated in a conference call with the client and external advisors to discuss {case} transaction progress and next steps.",
    "Prepared supporting documentation and developed a compliance checklist to ensure all regulatory obligations are met prior to execution.",
    "Drafted detailed contractual clauses addressing liability, indemnification, and risk allocation between the involved parties.",
    "Conducted a final review of all {case} transaction documents and advised on negotiation points prior to execution.",
    "Held a follow-up meeting with the client to provide final advisory input and confirm readiness for execution of the {case} agreement.",
    "Analyzed proposed {case} terms and prepared detailed recommendations for risk minimization strategy.",
    "Prepared and filed regulatory submissions related to {case} with the appropriate authorities.",
    "Coordinated with external counsel to review cross-jurisdictional compliance requirements for the {case} matter.",
    "Reviewed due diligence materials and prepared summary memorandum for senior partner review.",
    "Drafted and negotiated non-disclosure agreement with counterparties involved in the {case}.",
    "Attended client meeting to present legal analysis and strategic recommendations regarding {case}.",
    "Reviewed financing documents and advised on security arrangements related to {case}.",
    "Prepared board resolutions and corporate authorizations required for the {case} transaction.",
    "Advised on employment and benefit plan implications arising from the proposed {case}.",
    "Analyzed tax implications and prepared memorandum on structuring alternatives for {case}.",
    "Reviewed and commented on disclosure schedules in connection with {case} documentation.",
]

HOURS_POOL = [0.25, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.90,
              1.00, 1.10, 1.20, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50]


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def random_attorney():
    first    = random.choice(ATTORNEY_FIRSTS)
    middle   = random.choice(ATTORNEY_MIDDLES)
    last     = random.choice(ATTORNEY_LASTS)
    name     = f"{first} {middle} {last}"
    initials = f"{first[0]}{middle[0]}{last[0]}"   # e.g. MTP
    rate     = random.choice(HOURLY_RATES)
    return {"name": name, "initials": initials, "rate": rate}


def random_invoice_number(firm_name):
    words  = [w for w in firm_name.split() if w not in ("&", "LLP", "LLC")]
    prefix = "".join(w[0] for w in words[:2])
    year   = random.randint(2025, 2027)
    num    = random.randint(1, 150)
    return f"{prefix}-{year}-{num:03d}"


def random_matter_number():
    return (f"{random.randint(1,9)}"
            f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}"
            f"{random.randint(100000, 999999)}")


def random_irs_number():
    return "".join(str(random.randint(0, 9)) for _ in range(9))


def format_invoice_date(dt):
    """MARCH 1, 2026  style"""
    # Windows-compatible: use %#d instead of %-d
    return dt.strftime("%B %#d, %Y").upper()


def format_billing_end(dt):
    """February 28, 2026  style"""
    # Windows-compatible: use %#d instead of %-d
    return dt.strftime("%B %#d, %Y")


# ─────────────────────────────────────────────────────────────
# MAIN DATA GENERATOR
# ─────────────────────────────────────────────────────────────

def generate_invoice_data(num_items: int = None) -> dict:
    """
    Returns a fully populated invoice dict with randomized values.
    num_items controls how many line items (= page count).
    If None, randomly chosen: 6-9 → 2 pages, 10-14 → 3 pages, 15-20 → 4 pages.
    """

    # ── firm ──
    firm_name, po_box, city = random.choice(LAW_FIRMS)
    irs_no = random_irs_number()

    # ── attorneys: 3-4 unique ──
    attorneys = []
    used_initials = set()
    while len(attorneys) < random.randint(3, 4):
        a = random_attorney()
        if a["initials"] not in used_initials:
            attorneys.append(a)
            used_initials.add(a["initials"])
    billing_attorney = random.choice(attorneys)

    # ── dates ──
    year       = random.randint(2025, 2027)
    month      = random.randint(1, 12)
    invoice_dt = datetime(year, month, 1) + timedelta(days=random.randint(0, 27))
    billing_end_dt = invoice_dt - timedelta(days=random.randint(1, 5))
    # last day of billing month
    if billing_end_dt.month == 12:
        last_day = datetime(billing_end_dt.year, 12, 31)
    else:
        last_day = datetime(billing_end_dt.year, billing_end_dt.month + 1, 1) - timedelta(days=1)
    billing_end_dt = last_day

    # ── item count → page count ──
    if num_items is None:
        num_items = random.choices(
            population=[
                random.randint(6, 9),    # → 2 pages
                random.randint(10, 14),  # → 3 pages
                random.randint(15, 20),  # → 4 pages
            ],
            weights=[40, 40, 20],
        )[0]

    # ── line items ──
    days_in_month  = billing_end_dt.day
    sampled_days   = sorted(random.choices(range(1, days_in_month + 1), k=num_items))
    case_title_full = f"{fake.company()} {random.choice(CASE_TYPES)}"
    case_short      = case_title_full.split()[-2] + " " + case_title_full.split()[-1]  # last 2 words

    line_items = []
    for i in range(num_items):
        atty    = random.choice(attorneys)
        day     = sampled_days[i]
        date_dt = datetime(billing_end_dt.year, billing_end_dt.month, day)
        hours   = random.choice(HOURS_POOL)
        desc    = random.choice(LEGAL_TASKS).format(case=case_short.lower())
        amount  = round(hours * atty["rate"], 2)

        line_items.append({
            "date"        : date_dt.strftime("%b %d, %Y"),
            "initials"    : atty["initials"],
            "counsel"     : atty["name"],
            "hours"       : hours,
            "rate"        : atty["rate"],
            "amount"      : amount,
            "description" : desc,
        })

    # sort chronologically
    line_items.sort(key=lambda x: datetime.strptime(x["date"], "%b %d, %Y"))

    # ── attorney summary ──
    attorney_summary = {}
    for item in line_items:
        ini = item["initials"]
        if ini not in attorney_summary:
            attorney_summary[ini] = {
                "name"  : item["counsel"],
                "hours" : 0.0,
                "rate"  : item["rate"],
                "amount": 0.0,
            }
        attorney_summary[ini]["hours"]  = round(attorney_summary[ini]["hours"]  + item["hours"],  2)
        attorney_summary[ini]["amount"] = round(attorney_summary[ini]["amount"] + item["amount"], 2)

    total_hours  = round(sum(i["hours"]  for i in line_items), 2)
    total_amount = round(sum(i["amount"] for i in line_items), 2)

    # ── buyer ──
    buyer_company = fake.company().upper() + " " + random.choice(["LLC", "INC.", "CORP.", "LTD.", "GROUP"])
    buyer_street  = f"{fake.building_number()} {fake.street_name().upper()}"
    buyer_city    = f"{fake.city().upper()}, {fake.state_abbr()} {fake.zipcode()}"
    buyer_email   = fake.email()
    contact_email = fake.email()

    return {
        "invoice_number"  : random_invoice_number(firm_name),
        "invoice_date"    : format_invoice_date(invoice_dt),
        "billing_end"     : format_billing_end(billing_end_dt),
        "currency"        : "USD",
        "format_type"     : "Legal Services Invoice",

        "seller": {
            "company_name": firm_name,
            "po_box"      : po_box,
            "city"        : city,
            "irs_number"  : irs_no,
        },

        "buyer": {
            "company_name"  : buyer_company,
            "address_line1" : buyer_street,
            "address_line2" : buyer_city,
            "email"         : buyer_email,
            "contact_email" : contact_email,
        },

        "legal_fields": {
            "client_matter_number": random_matter_number(),
            "attorney_name"       : billing_attorney["name"],
            "case_title"          : case_title_full,
        },

        "line_items"      : line_items,
        "attorney_summary": attorney_summary,

        "totals": {
            "total_hours"  : total_hours,
            "total_fees"   : total_amount,
            "total_invoice": total_amount,
        },

        "metadata": {
            "total_pages"  : None,      
            "layout"       : "legal",
            "document_type": "invoice",
        },
    }