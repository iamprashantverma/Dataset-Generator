"""
src/templates/layout2.py
────────────────────────
Layout 2: Multi-office law firm invoice (Mosby, Eriksen & Stinson style)

Key differences from layout1:
- Multiple office locations displayed at top
- Simpler first page with summary totals
- Time entries on page 2+ with initials column
- Fee summary on last page showing attorney breakdown
- No email forwarding section
- Different footer format
"""

# This file defines the structure for layout2
# The actual rendering is done in src/renderer.py based on layout type

LAYOUT2_CONFIG = {
    "name": "layout2",
    "description": "Multi-office law firm invoice",
    "pages": {
        "first": {
            "header": ["firm_name", "office_locations"],
            "content": ["invoice_date", "billing_period", "client_info", "matter_info", "case_title", "summary_totals"],
            "footer": ["remit_to", "payment_instructions"]
        },
        "continuation": {
            "header": ["firm_name", "client_info", "invoice_info", "matter_number", "case_title"],
            "content": ["time_entries_table"],
            "footer": None
        },
        "summary": {
            "header": ["firm_name", "client_name", "case_title", "page_number"],
            "content": ["client_info", "invoice_info", "fee_summary_table"],
            "footer": None
        }
    }
}
