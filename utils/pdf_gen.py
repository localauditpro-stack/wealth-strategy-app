from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
import datetime

# --- BRANDING CONSTANTS ---
BRAND_NAVY = colors.Color(15/255, 23/255, 42/255) # #0F172A
BRAND_INDIGO = colors.Color(99/255, 102/255, 241/255) # #6366F1
BRAND_PURPLE = colors.Color(168/255, 85/255, 247/255) # #A855F7
BRAND_GREY = colors.Color(248/255, 250/255, 252/255) # #F8FAFC

def header_footer(canvas, doc):
    """Draws the header and footer on every page."""
    canvas.saveState()
    width, height = A4
    
    # --- HEADER ---
    # Logo Placeholder (Text for now)
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(BRAND_NAVY)
    canvas.drawString(inch, height - 50, "WEALTH ACCELERATOR")
    
    # Top Line
    canvas.setStrokeColor(BRAND_INDIGO)
    canvas.setLineWidth(2)
    canvas.line(inch, height - 60, width - inch, height - 60)
    
    # --- FOOTER ---
    # Disclaimer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    disclaimer_text = "Disclaimer: This projection is for educational purposes only and does not constitute financial advice."
    canvas.drawCentredString(width / 2, 40, disclaimer_text)
    
    # Page Number
    page_num = f"Page {doc.page}"
    canvas.drawRightString(width - inch, 40, page_num)
    
    canvas.restoreState()

def generate_pdf_report(user_data, dr_results, ip_results, chart_image=None):
    """
    Generates a premium PDF report using ReportLab Platypus.
    
    Args:
        user_data (dict): Lead details (Name, Goal, etc.)
        dr_results (dict): Debt Recycling calculation results
        ip_results (dict): Investment Property calculation results
        chart_image (bytes): PNG image data of the main chart (optional)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=APT_NAVY,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=APT_NAVY,
        spaceBefore=20,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # --- TITLE PAGE / HEADER ---
    elements.append(Paragraph("Wealth Strategy Analysis", title_style))
    elements.append(Paragraph(f"Prepared for: {user_data.get('name', 'Valued Client')}", normal_style))
    elements.append(Paragraph(f"Date: {datetime.date.today().strftime('%d %B %Y')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # --- CLIENT GOAL ---
    if user_data.get('goal'):
        elements.append(Paragraph("Primary Objective", h2_style))
        elements.append(Paragraph(f"Target: {user_data['goal']}", normal_style))
        elements.append(Spacer(1, 10))

    # --- MAIN CHART ---
    if chart_image:
        elements.append(Paragraph("Projected Net Wealth Growth (10 Years)", h2_style))
        # Keep aspect ratio
        img = Image(io.BytesIO(chart_image), width=6*inch, height=3.5*inch) 
        elements.append(img)
        elements.append(Spacer(1, 20))

    # --- COMPARISON TABLE ---
    elements.append(Paragraph("Strategy Comparison", h2_style))
    
    dr_final = dr_results['net_wealth'][-1]
    ip_final = ip_results['net_wealth'][-1]
    dr_tax = dr_results['tax_saved'][-1]
    ip_tax = ip_results['tax_saved'][-1]
    
    data = [
        ["Metric", "Debt Recycling", "Investment Property"],
        ["Projected Net Wealth", f"${dr_final:,.0f}", f"${ip_final:,.0f}"],
        ["Estimated Tax Saved", f"${dr_tax:,.0f}", f"${ip_tax:,.0f}"],
        ["Liquidity", "High (Shares)", "Low (Property)"],
        ["Effort Required", "Low (Set & Forget)", "High (Management)"]
    ]
    
    t = Table(data, colWidths=[2.5*inch, 1.75*inch, 1.75*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Left align first col
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), BRAND_GREY),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # --- BUILD ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    
    buffer.seek(0)
    return buffer
