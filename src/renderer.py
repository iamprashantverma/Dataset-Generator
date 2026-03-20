import fitz  # pymupdf
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class FooteredDocTemplate(SimpleDocTemplate):
    """Custom document template that adds header and footer to every page"""
    
    def __init__(self, *args, footer_data=None, header_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.footer_data = footer_data or {}
        self.header_data = header_data or {}
        self.page_num = 0
        self.case_title = header_data.get('case', '') if header_data else ''
    
    def build(self, flowables, onFirstPage=None, onLaterPages=None, canvasmaker=canvas.Canvas):
        """Override build to add header and footer callbacks"""
        
        def add_header_footer_first(canvas_obj, doc):
            """First page header/footer"""
            self.page_num = 1
            canvas_obj.saveState()
            
            # HEADER
            header_y = A4[1] - 0.5 * inch  # Fixed position from top
            
            firm = self.header_data.get('firm', '')
            inv_date = self.header_data.get('inv_date', '')
            inv_num = self.header_data.get('inv_num', '')
            matter = self.header_data.get('matter', '')
            atty = self.header_data.get('atty', '')
            
            # First page: Firm name (left) | INVOICE (right)
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.drawString(doc.leftMargin, header_y, firm)
            
            canvas_obj.setFont('Helvetica', 34)
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, header_y - 5, 'INVOICE')
            
            # Date below firm name
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(doc.leftMargin, header_y - 40, inv_date)
            
            # Matter info (right aligned)
            y_pos = header_y - 60
            canvas_obj.setFont('Helvetica', 11)
            
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Client/Matter Number: {matter}')
            y_pos -= 15
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Invoice Number: {inv_num}')
            y_pos -= 15
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Billing Attorney: {atty}')
            
            # Add footer
            self._draw_footer(canvas_obj, doc)
            canvas_obj.restoreState()
        
        def add_header_footer_later(canvas_obj, doc):
            """Continuation pages header/footer"""
            self.page_num += 1
            canvas_obj.saveState()
            
            # HEADER
            header_y = A4[1] - 0.5 * inch  # Fixed position from top
            
            firm = self.header_data.get('firm', '')
            inv_date = self.header_data.get('inv_date', '')
            inv_num = self.header_data.get('inv_num', '')
            matter = self.header_data.get('matter', '')
            atty = self.header_data.get('atty', '')
            case = self.header_data.get('case', '')
            
            # Continuation pages: Firm name (left) | Date (right)
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.drawString(doc.leftMargin, header_y, firm)
            
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, header_y, inv_date)
            
            # INVOICE (left) | Matter info (right)
            y_pos = header_y - 25
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(doc.leftMargin, y_pos, 'INVOICE')
            
            # Matter info (right aligned)
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Client/Matter Number: {matter}')
            y_pos -= 15
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Invoice Number: {inv_num}')
            y_pos -= 15
            canvas_obj.drawRightString(A4[0] - doc.rightMargin, y_pos, 
                                     f'Billing Attorney: {atty}')
            
            # Re: line on continuation pages
            y_pos -= 20
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(doc.leftMargin, y_pos, f'Re: {case}')
            
            # Add footer
            self._draw_footer(canvas_obj, doc)
            canvas_obj.restoreState()
        
        # Reset page counter
        self.page_num = 0
        
        # Use different callbacks for first and later pages
        super().build(flowables, onFirstPage=add_header_footer_first, onLaterPages=add_header_footer_later, canvasmaker=canvasmaker)
    
    def _draw_footer(self, canvas_obj, doc):
        """Draw footer on page"""
        footer_y = 0.75 * inch - 10
        
        # Draw single line border at top of footer
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(
            doc.leftMargin,
            footer_y + 50,
            A4[0] - doc.rightMargin,
            footer_y + 50
        )
        
        # Footer text
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(doc.leftMargin, footer_y + 35, 
                            f"I.R.S NO. {self.footer_data.get('irs', '')}")
        
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(doc.leftMargin, footer_y + 20, 
                            "Please reference client/matter and invoice numbers when making payment.")
        canvas_obj.drawString(doc.leftMargin, footer_y + 7, 
                            "PLEASE REMIT TO")
        canvas_obj.drawString(doc.leftMargin, footer_y - 6, 
                            f"{self.footer_data.get('firm', '')} , {self.footer_data.get('po', '')} , {self.footer_data.get('city', '')}")


def _parse_invoice_data_from_html(html_content: str, data: dict) -> dict:
    """
    Extract structured data from the data dict for PDF generation.
    The HTML template is no longer used - we build PDF directly.
    """
    return data


def html_to_images(
    html_content: str,
    output_dir: str,
    invoice_id: str,
    dpi: int = 200,
    data: dict = None,
) -> tuple[list[str], int]:
    """
    Render invoice data → PDF → page images.

    Parameters
    ----------
    html_content : HTML string (not used with reportlab, kept for compatibility)
    output_dir   : directory to write .jpg files into
    invoice_id   : prefix for file names  e.g. "invoice_0042"
    dpi          : render resolution  (200 = A4 1654×2339 px)
    data         : invoice data dict (required for reportlab approach)

    Returns
    -------
    (image_paths, actual_page_count)
    """
    if data is None:
        raise ValueError("data parameter is required for reportlab renderer")

    layout = data.get("metadata", {}).get("layout", "layout1")
    
    # Route to appropriate layout renderer
    if layout == "layout2":
        pdf_bytes = _generate_layout2_pdf(data)
    else:  # layout1 or default
        pdf_bytes = _generate_layout1_pdf(data)

    # 2. PDF bytes → page images (PyMuPDF)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_paths = []

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 = default PDF DPI
        pix = page.get_pixmap(matrix=mat)
        img_path = str(Path(output_dir) / f"{invoice_id}_{page_num}.jpg")
        pix.save(img_path)
        image_paths.append(img_path)

    actual_pages = len(doc)
    doc.close()

    return image_paths, actual_pages


def html_to_pdf(html_content: str, output_path: str, data: dict = None) -> None:
    """
    Save invoice data as a PDF file (used for preview / inspection).
    """
    if data is None:
        raise ValueError("data parameter is required for reportlab renderer")

    layout = data.get("metadata", {}).get("layout", "layout1")
    
    if layout == "layout2":
        pdf_bytes = _generate_layout2_pdf(data)
    else:
        pdf_bytes = _generate_layout1_pdf(data)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)


def _generate_layout1_pdf(data: dict) -> bytes:
    """
    Generate PDF using ReportLab matching the HTML template structure exactly.
    
    Structure:
    - Page 1..N-1: Time entries (8 rows per page)
    - Page N: Last time entries + Total + Total Invoice
    - Last page: Summary of Services (attorney breakdown)
    - Footer on every page
    """
    buffer = BytesIO()
    
    seller = data["seller"]
    buyer = data["buyer"]
    legal = data["legal_fields"]
    items = data["line_items"]
    totals = data["totals"]
    atty_s = data["attorney_summary"]

    firm = seller["company_name"]
    po = seller["po_box"]
    city = seller["city"]
    irs = seller["irs_number"]

    inv_num = data["invoice_number"]
    inv_date = data["invoice_date"]
    bill_end = data["billing_end"]
    matter = legal["client_matter_number"]
    atty = legal["attorney_name"]
    case = legal["case_title"]

    total_h = totals["total_hours"]
    total_f = totals["total_fees"]
    total_i = totals["total_invoice"]

    # Create PDF with custom header/footer template
    doc = FooteredDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=1.6 * inch,  # Reduced to bring content closer to header
        bottomMargin=1.5 * inch,  # Space for footer
        footer_data={'firm': firm, 'po': po, 'city': city, 'irs': irs},
        header_data={'firm': firm, 'inv_date': inv_date, 'inv_num': inv_num, 'matter': matter, 'atty': atty, 'case': case}
    )

    # Styles
    styles = getSampleStyleSheet()
    
    firm_style = ParagraphStyle(
        'FirmName',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        leading=16,
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontSize=34,
        fontName='Helvetica',
        alignment=TA_RIGHT,
        leading=36,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
    )
    
    small_style = ParagraphStyle(
        'SmallNormal',
        parent=styles['Normal'],
        fontSize=9,
        leading=14,
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        leading=15,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
    )

    # Build story
    story = []
    
    # ══════════════════════════════════════════════════════════
    # FIRST PAGE CONTENT (client info, email)
    # ══════════════════════════════════════════════════════════
    # No spacer needed - topMargin handles the space
    
    # Client address (left side only, matter info is in header)
    client_info = f"""<b>{buyer["company_name"]}</b><br/>
{buyer["address_line1"]},<br/>
{buyer["address_line2"]}"""
    
    story.append(Paragraph(client_info, normal_style))
    story.append(Spacer(1, 12))
    
    # Email forwarding
    email_text = f"""<b>This invoice has been forwarded via e-mail to:</b><br/>
{buyer["email"]}"""
    story.append(Paragraph(email_text, small_style))
    story.append(Spacer(1, 10))
    
    copy_text = f"""<b>A copy of this invoice has been forwarded to:</b><br/>
{buyer["contact_email"]}"""
    story.append(Paragraph(copy_text, small_style))
    story.append(Spacer(1, 18))
    
    # Re: line
    story.append(Paragraph(f"<b>Re: {case}</b>", bold_style))
    story.append(Spacer(1, 6))
    
    # Fees heading
    story.append(Paragraph(f"<b>Fees for services posted through {bill_end}:</b>", bold_style))
    story.append(Spacer(1, 10))
    
    # ══════════════════════════════════════════════════════════
    # TIME ENTRIES TABLE (ALL ITEMS - will flow across pages)
    # ══════════════════════════════════════════════════════════
    table_data = [['Date', 'Initials', 'Description', 'Hours']]
    
    for item in items:
        # Wrap description text in Paragraph for proper text wrapping
        desc_para = Paragraph(item["description"], small_style)
        table_data.append([
            item["date"],
            item["initials"],
            desc_para,
            f'{item["hours"]:.2f}'
        ])
    
    # Add Total row
    table_data.append([
        'Total',
        '',
        f'{total_h:.2f}',
        f'${total_f:,.2f}'
    ])
    
    # Create table with proper column widths
    col_widths = [1.1 * inch, 0.7 * inch, 3.5 * inch, 0.8 * inch]
    time_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    table_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Bold total row with top border
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
    ]
    
    time_table.setStyle(TableStyle(table_style))
    story.append(time_table)
    
    # Total Invoice line
    total_inv_data = [['Total Invoice', f'${total_i:,.2f}']]
    total_inv_table = Table(total_inv_data, colWidths=[5.5 * inch, 1.1 * inch])
    total_inv_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(total_inv_table)
    
    # ══════════════════════════════════════════════════════════
    # SUMMARY OF SERVICES PAGE (always last)
    # ══════════════════════════════════════════════════════════
    story.append(PageBreak())
    
    # Re: line already in header, so skip it here
    story.append(Paragraph("<b>Summary of Services</b>", bold_style))
    story.append(Spacer(1, 10))
    
    # Summary table
    summary_data = [['Initials', 'Name', 'Hours', 'Eff. Rates', 'Amount']]
    
    for ini, d in atty_s.items():
        summary_data.append([
            ini,
            d["name"],
            f'{d["hours"]:.2f}',
            f'${d["rate"]}',
            f'${d["amount"]:,.2f}'
        ])
    
    summary_data.append([
        'Total',
        '',
        f'{total_h:.2f}',
        '',
        f'${total_f:,.2f}'
    ])
    
    summary_col_widths = [0.65 * inch, 2.6 * inch, 0.8 * inch, 1.1 * inch, 1.5 * inch]
    summary_table = Table(summary_data, colWidths=summary_col_widths)
    
    summary_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
    ]
    
    summary_table.setStyle(TableStyle(summary_style))
    story.append(summary_table)
    
    # Build PDF (footer added automatically to all pages)
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes



# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT 2: Multi-office law firm invoice (Mosby, Eriksen & Stinson style)
# ══════════════════════════════════════════════════════════════════════════════

def _generate_layout2_pdf(data: dict) -> bytes:
    """
    Generate PDF for layout2: Multi-office law firm invoice
    
    Structure:
    - Page 1: Firm header with offices, invoice summary, totals
    - Page 2+: Time entries 
    - Last page: Fee Summary by attorney
    """
    buffer = BytesIO()
    
    seller = data["seller"]
    buyer = data["buyer"]
    legal = data["legal_fields"]
    items = data["line_items"]
    totals = data["totals"]
    atty_s = data["attorney_summary"]

    firm = seller["company_name"]
    inv_num = data["invoice_number"]
    inv_date = data["invoice_date"]
    bill_end = data["billing_end"]
    matter = legal["client_matter_number"]
    atty = legal["attorney_name"]
    case = legal["case_title"]

    total_h = totals["total_hours"]
    total_f = totals["total_fees"]
    total_i = totals["total_invoice"]

    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    
    firm_style = ParagraphStyle(
        'FirmName',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=18,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
    )
    
    small_style = ParagraphStyle(
        'SmallNormal',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        leading=12,
    )

    story = []
    
    # ══════════════════════════════════════════════════════════
    # PAGE 1: SUMMARY PAGE
    # ══════════════════════════════════════════════════════════
    
    # Firm name (centered)
    story.append(Paragraph(firm, firm_style))
    story.append(Spacer(1, 12))
    
    # Office locations (4 offices in one row)
    office1 = "<b>New York</b><br/>245 Madison Avenue<br/>New York, NY 10016<br/>Tel: (212) 555-0147"
    office2 = "<b>Chicago</b><br/>180 W Monroe Street<br/>Chicago, IL 60603<br/>Tel: (312) 555-0192"
    office3 = "<b>Los Angeles</b><br/>900 Wilshire Blvd<br/>Los Angeles, CA 90017<br/>Tel: (213) 555-0118"
    office4 = "<b>Manchester</b><br/>600 Morgan St.<br/>Man, CA 90017<br/>Tel: (213) 555-0118"
    
    office_data = [[
        Paragraph(office1, small_style), 
        Paragraph(office2, small_style),
        Paragraph(office3, small_style),
        Paragraph(office4, small_style)
    ]]
    office_table = Table(office_data, colWidths=[1.625*inch, 1.625*inch, 1.625*inch, 1.625*inch])
    office_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(office_table)
    story.append(Spacer(1, 20))
    
    # Invoice date and billing period (centered)
    date_style = ParagraphStyle(
        'DateCenter',
        parent=bold_style,
        alignment=TA_CENTER,
    )
    story.append(Paragraph(f"<b>INVOICE DATE: {inv_date}</b>", date_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>FOR PERIOD THROUGH: {bill_end}</b>", date_style))
    story.append(Spacer(1, 20))
    
    # Client and matter info
    client_text = f"{buyer['company_name']}<br/>{buyer['address_line1']}<br/>{buyer['address_line2']}"
    matter_text = f"<b>Matter Number:</b> {matter}<br/><b>Billing Attorney:</b> {atty}<br/><b>Invoice Number:</b> {inv_num}"
    
    info_data = [[Paragraph(client_text, normal_style), Paragraph(matter_text, normal_style)]]
    info_table = Table(info_data, colWidths=[3.25*inch, 3.25*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Re: line
    story.append(Paragraph(f"<b>Re: {case}</b>", bold_style))
    story.append(Spacer(1, 30))
    
    # Summary totals
    story.append(Paragraph(f"Total Fees: ${total_f:,.2f}", normal_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Total Fees & Disbursements: ${total_f:,.2f}", normal_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>TOTAL THIS INVOICE: ${total_i:,.2f}</b>", bold_style))
    story.append(Spacer(1, 30))
    
    # Remit to
    story.append(Paragraph("Remit to: 180 W Monroe Street Chicago, IL 60603", normal_style))
    story.append(Paragraph("<b>Please include invoice number on check</b>", bold_style))
    
    # ══════════════════════════════════════════════════════════
    # PAGE 2: TIME ENTRIES
    # ══════════════════════════════════════════════════════════
    story.append(PageBreak())
    
    story.append(Paragraph(firm, firm_style))
    story.append(Spacer(1, 10))
    
    # Header with left and right alignment (matching table column widths)
    left_info = f"{buyer['company_name']}<br/>{buyer['address_line1']}"
    right_info = f"{inv_date}<br/>Billing Attorney: {atty}<br/>Invoice Number: {inv_num}"
    
    # Left section width = Date + Description columns = 0.85 + 3.0 = 3.85"
    # Right section width = Init + Hours + Rate + Amount = 0.45 + 0.6 + 0.7 + 0.9 = 2.65"
    header_data = [[Paragraph(left_info, normal_style), Paragraph(right_info, normal_style)]]
    header_table = Table(header_data, colWidths=[3.85*inch, 2.65*inch], spaceBefore=0, spaceAfter=0)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 25))
    
    story.append(Paragraph(f"For Services through: {bill_end}", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Matter #: {matter}</b>", bold_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Re: {case}</b>", bold_style))
    story.append(Spacer(1, 15))
    
    # Time entries table
    table_data = [['Date', 'Description', 'Init', 'Hours', 'Rate', 'Amount']]
    
    for item in items:
        desc_para = Paragraph(item["description"], small_style)
        table_data.append([
            item["date"],
            desc_para,
            item["initials"],
            f'{item["hours"]:.2f}',
            f'${item["rate"]}',
            f'${item["amount"]:,.2f}'
        ])
    
    # Totals row
    table_data.append([
        '', 'Totals', '', f'{total_h:.2f}', '', f'${total_f:,.2f}'
    ])
    
    col_widths = [0.85*inch, 3.0*inch, 0.45*inch, 0.6*inch, 0.7*inch, 0.9*inch]
    time_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    time_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    story.append(time_table)
    
    # ══════════════════════════════════════════════════════════
    # PAGE 3: FEE SUMMARY
    # ══════════════════════════════════════════════════════════
    story.append(PageBreak())
    
    # Row 1: Firm name, company, case title (left) | Date, Invoice Number, Page (right)
    # Left section width = Name + Init columns = 2.5 + 0.6 = 3.1"
    # Right section width = Hours + Eff. Rate + Amount = 0.7 + 1.2 + 1.5 = 3.4"
    left_row1 = f"<b>{firm}</b><br/><b>{buyer['company_name']}</b><br/><b>{case.upper()}</b>"
    right_row1 = f"{inv_date}<br/>Invoice Number: {inv_num}<br/><b>Page: 3</b>"
    
    row1_data = [[Paragraph(left_row1, normal_style), Paragraph(right_row1, normal_style)]]
    row1_table = Table(row1_data, colWidths=[3.1*inch, 3.4*inch])
    row1_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    story.append(row1_table)
    story.append(Spacer(1, 40))
    
    # Row 2: Client name, address, email (left) | Billing Attorney, Invoice Number (right)
    left_row2 = f"{buyer['company_name']}<br/>{buyer['address_line1']}<br/>{buyer['email']}"
    right_row2 = f"<b>Billing Attorney:</b> {atty}<br/><b>Invoice Number:</b> {inv_num}"
    
    row2_data = [[Paragraph(left_row2, normal_style), Paragraph(right_row2, normal_style)]]
    row2_table = Table(row2_data, colWidths=[3.1*inch, 3.4*inch])
    row2_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    story.append(row2_table)
    story.append(Spacer(1, 30))
    
    # Fee Summary
    story.append(Paragraph("<b>FEE SUMMARY</b>", bold_style))
    story.append(Spacer(1, 10))
    
    summary_data = [['Name', 'Init', 'Hours', 'Eff. Rate', 'Amount']]
    
    for ini, d in atty_s.items():
        summary_data.append([
            d["name"],
            ini,
            f'{d["hours"]:.2f}',
            f'${d["rate"]}',
            f'${d["amount"]:,.2f}'
        ])
    
    summary_col_widths = [2.5*inch, 0.6*inch, 0.7*inch, 1.2*inch, 1.5*inch]
    summary_table = Table(summary_data, colWidths=summary_col_widths)
    
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
