import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.pdf_gen import generate_pdf_report
    print("SUCCESS: Imported utils.pdf_gen")
except ImportError as e:
    print(f"ERROR: Could not import utils.pdf_gen: {e}")
    sys.exit(1)

# Mock Data
user_data = {"name": "Test User", "goal": "Retirement"}
dr_results = {"net_wealth": [100000, 200000], "tax_saved": [5000, 10000]}
ip_results = {"net_wealth": [100000, 150000], "tax_saved": [2000, 4000]}

print("Attempting to generate PDF...")
try:
    pdf_buffer = generate_pdf_report(user_data, dr_results, ip_results, chart_image=None)
    print(f"SUCCESS: PDF generated, size: {pdf_buffer.getbuffer().nbytes} bytes")
except Exception as e:
    print(f"ERROR: PDF generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test Kaleido/Plotly if available
try:
    import plotly.graph_objects as go
    print("Attempting to generate Chart Image (Kaleido)...")
    fig = go.Figure(go.Scatter(x=[1, 2], y=[1, 2]))
    img_bytes = fig.to_image(format="png")
    print(f"SUCCESS: Chart image generated, size: {len(img_bytes)} bytes")
except Exception as e:
    print(f"ERROR: Chart image generation failed: {e}")
