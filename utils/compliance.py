import streamlit as st

def render_sidebar_disclaimer():
    """Renders the mandatory general advice disclaimer in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.caption(
            "⚠️ **IMPORTANT DISCLAIMER**\n\n"
            "This tool provides **general information and mathematical projections only**. "
            "It does not take into account your personal objectives, financial situation, or needs. "
            "It is **not** financial advice.\n\n"
            "Before acting on this information, you should consider its appropriateness to your circumstances "
            "and seek professional advice."
        )

def render_footer_disclaimer():
    """Renders the 'Off-Ramp' disclaimer at the bottom of calculators."""
    st.markdown("---")
    st.info(
        "👋 **Next Steps**\n\n"
        "Projections are not guarantees. Strategies discussed here are complex and rely on specific "
        "tax and legal structures. For a strategy tailored to your specific circumstances, "
        "we recommend speaking with a licensed professional."
    )

def get_projection_disclaimer():
    """Returns standard text for use near calculation results."""
    return (
        "Figures are mathematical projections based on the variables provided. "
        "They are not predictions or guarantees of future performance. "
        "Actual results will vary independently of these projections."
    )
