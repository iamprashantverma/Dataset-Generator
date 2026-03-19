import jsonlines
import json

# Read first entry from train.jsonl
with jsonlines.open('output/jsonl/train.jsonl') as reader:
    data = list(reader)[0]

# Extract invoice data from assistant message
invoice_data = json.loads(data['messages'][1]['content'][0]['text'])

print("=" * 60)
print("INVOICE CALCULATION VERIFICATION")
print("=" * 60)

print(f"\nInvoice Number: {invoice_data['invoice_number']}")
print(f"Number of Line Items: {len(invoice_data['line_items'])}")

# Verify line item calculations
print("\n" + "=" * 60)
print("LINE ITEM VERIFICATION (First 3 items)")
print("=" * 60)

for i, item in enumerate(invoice_data['line_items'][:3]):
    calculated = round(item['hours'] * item['rate'], 2)
    match = abs(item['amount'] - calculated) < 0.01
    
    print(f"\nItem {i+1}:")
    print(f"  Date: {item['date']}")
    print(f"  Hours: {item['hours']}")
    print(f"  Rate: ${item['rate']}")
    print(f"  Reported Amount: ${item['amount']:.2f}")
    print(f"  Calculated Amount: ${calculated:.2f}")
    print(f"  ✓ Match: {match}")

# Verify total calculations
print("\n" + "=" * 60)
print("TOTAL CALCULATIONS VERIFICATION")
print("=" * 60)

# Calculate totals from line items
total_hours_calc = sum(item['hours'] for item in invoice_data['line_items'])
total_fees_calc = sum(item['amount'] for item in invoice_data['line_items'])

print(f"\nTotal Hours:")
print(f"  Reported: {invoice_data['totals']['total_hours']}")
print(f"  Calculated: {total_hours_calc}")
print(f"  ✓ Match: {abs(invoice_data['totals']['total_hours'] - total_hours_calc) < 0.01}")

print(f"\nTotal Fees:")
print(f"  Reported: ${invoice_data['totals']['total_fees']:,.2f}")
print(f"  Calculated: ${total_fees_calc:,.2f}")
print(f"  ✓ Match: {abs(invoice_data['totals']['total_fees'] - total_fees_calc) < 0.01}")

print(f"\nTotal Invoice:")
print(f"  Reported: ${invoice_data['totals']['total_invoice']:,.2f}")
print(f"  Should Equal Total Fees: ${invoice_data['totals']['total_fees']:,.2f}")
print(f"  ✓ Match: {abs(invoice_data['totals']['total_invoice'] - invoice_data['totals']['total_fees']) < 0.01}")

# Verify attorney summary
print("\n" + "=" * 60)
print("ATTORNEY SUMMARY VERIFICATION")
print("=" * 60)

for initials, summary in invoice_data['attorney_summary'].items():
    # Calculate from line items
    atty_items = [item for item in invoice_data['line_items'] if item['initials'] == initials]
    calc_hours = sum(item['hours'] for item in atty_items)
    calc_amount = sum(item['amount'] for item in atty_items)
    
    print(f"\n{initials} - {summary['name']}:")
    print(f"  Reported Hours: {summary['hours']}")
    print(f"  Calculated Hours: {calc_hours}")
    print(f"  ✓ Match: {abs(summary['hours'] - calc_hours) < 0.01}")
    print(f"  Reported Amount: ${summary['amount']:,.2f}")
    print(f"  Calculated Amount: ${calc_amount:,.2f}")
    print(f"  ✓ Match: {abs(summary['amount'] - calc_amount) < 0.01}")

print("\n" + "=" * 60)
print(" VERIFICATION COMPLETE")
print("=" * 60)
