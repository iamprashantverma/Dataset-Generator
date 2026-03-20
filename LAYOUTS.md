# Invoice Layouts

This project supports multiple invoice layouts for diverse training data.

## Available Layouts

### Layout 1: Single-office Law Firm (Richard & Matthews style)
**File:** `src/templates/layout1.py`

**Structure:**
- **Page 1:** Firm name, INVOICE title, date, client address, matter info, email forwarding, Re: line, time entries
- **Continuation pages:** Firm name, date, INVOICE, matter info, Re: line, time entries
- **Last page:** Summary of Services with attorney breakdown
- **Footer:** Single line, IRS number, remittance info (on every page)

**Features:**
- Automatic headers/footers on all pages
- Table headers repeat when flowing across pages
- Clean, professional layout

---

### Layout 2: Multi-office Law Firm (Mosby, Eriksen & Stinson style)
**File:** `src/templates/layout2.py`

**Structure:**
- **Page 1:** Firm name (centered), 4 office locations, invoice date, billing period, client info, matter info, Re: line, summary totals, remit to
- **Page 2+:** Firm name, client info, invoice info, matter #, Re: line, time entries table (Date, Description, Initials, Hours, Rate, Amount)
- **Last page:** Firm name, client name, case title, page number, Fee Summary by attorney

**Features:**
- Multiple office locations displayed
- Simpler first page with summary
- Initials column in time entries
- No email forwarding section
- Different footer format

---

## Usage

### Generate with specific layout:

```cmd
# Layout 1 (default)
venv\Scripts\python.exe src\scripts\generate.py --n 1000 --layout layout1

# Layout 2
venv\Scripts\python.exe src\scripts\generate.py --n 1000 --layout layout2

# Mixed (randomly selects between layouts)
venv\Scripts\python.exe src\scripts\generate.py --n 1000 --layout mixed
```

### Output naming:
- Layout 1 images: `layout1_invoice_0001_0.jpg`, `layout1_invoice_0001_1.jpg`, ...
- Layout 2 images: `layout2_invoice_0001_0.jpg`, `layout2_invoice_0001_1.jpg`, ...

### Dataset format:
Each entry includes layout info in metadata:
```json
{
  "metadata": {
    "layout": "layout1",  // or "layout2"
    "total_pages": 3,
    "document_type": "invoice"
  }
}
```

---

## Adding New Layouts

To add layout3, layout4, etc.:

1. Create `src/templates/layout3.py` with configuration
2. Add `_generate_layout3_pdf()` function in `src/renderer.py`
3. Update routing in `html_to_images()` and `html_to_pdf()`
4. Update `generate_dataset()` in `src/dataset_builder.py` to include new layout in "mixed" mode

---

## Layout Comparison

| Feature | Layout 1 | Layout 2 |
|---------|----------|----------|
| Office locations | Single | Multiple (4) |
| First page | Detailed | Summary only |
| Email forwarding | Yes | No |
| Time entry columns | Date, Initials, Description, Hours | Date, Description, Initials, Hours, Rate, Amount |
| Footer | Every page | First page only |
| Summary page | Yes | Yes |
| Page headers | Automatic | Manual |

---

## Benefits of Multiple Layouts

1. **Diverse training data** - Model learns different invoice formats
2. **Better generalization** - Handles various real-world layouts
3. **Realistic dataset** - Mimics actual business scenarios
4. **Easy expansion** - Add more layouts as needed
