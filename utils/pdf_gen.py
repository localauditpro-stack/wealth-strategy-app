from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

def generate_pdf_report(user_data, dr_results, ip_results):
    """Generates a PDF report comparing Debt Recycling vs Investment Property."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Wealth Strategy Analysis")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Personalized Report for Australian Investors")
    c.line(50, height - 90, width - 50, height - 90)

    # User Profile (Mock)
    y = height - 130
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Your Profile")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Strategy Horizon: 10 Years")
    y -= 20
    # Add more user details here if passed in user_data

    # Strategy Comparison
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Strategy Comparison (10-Year Projection)")
    y -= 30
    
    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Metric")
    c.drawString(250, y, "Debt Recycling")
    c.drawString(450, y, "Investment Property")
    y -= 20
    c.line(50, y + 10, width - 50, y + 10)
    
    # Data Rows
    dr_final_wealth = dr_results['net_wealth'][-1]
    ip_final_wealth = ip_results['net_wealth'][-1]
    dr_tax = dr_results['tax_saved'][-1]
    ip_tax = ip_results['tax_saved'][-1]

    metrics = [
        ("Projected Net Wealth", f"${dr_final_wealth:,.0f}", f"${ip_final_wealth:,.0f}"),
        ("Est. Tax Efficiency", f"${dr_tax:,.0f}", f"${ip_tax:,.0f}"),
        ("Liquidity", "High (Shares)", "Low (Property)"),
        ("Effort Required", "Low", "High"),
    ]

    c.setFont("Helvetica", 12)
    for name, dr_val, ip_val in metrics:
        c.drawString(50, y, name)
        c.drawString(250, y, dr_val)
        c.drawString(450, y, ip_val)
        y -= 25

    # Recommendation / Disclaimer
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    disclaimer = ("Disclaimer: This report is for educational purposes only and does not constitute financial advice. "
                  "Projections are based on assumptions and past performance is not indicative of future results.")
    
    text_object = c.beginText(50, y)
    text_object.setFont("Helvetica-Oblique", 10)
    text_object.setTextOrigin(50, y)
    # Simple word wrap logic isn't here, just printing one line for MVP
    c.drawString(50, y, "Disclaimer: This report is for educational purposes only. Not financial advice.")

    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
