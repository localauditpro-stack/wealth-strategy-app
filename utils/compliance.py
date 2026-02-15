import streamlit as st

def render_general_advice_warning_above_fold():
    """Renders a prominent general advice warning intended for the top of calculator pages."""
    st.warning(
        "⚖️ **GENERAL INFORMATION ONLY**\n\n"
        "The following information is for illustrative and educational purposes only. "
        "It does **not** constitute personal financial advice. We have not considered your "
        "personal objectives, financial situation, or needs. "
        "You should consider whether this information is appropriate for you and read the "
        "relevant Product Disclosure Statement (PDS) before making any financial decisions."
    )

def render_data_usage_explanation():
    """Briefly explains that personal data is used for relevance, not personal advice."""
    st.caption(
        "Note: Your answers are used only to show more relevant general information and scenarios, "
        "not to provide personal recommendations."
    )

def render_sidebar_disclaimer():
    """Renders the mandatory general advice disclaimer in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.caption(
            "⚠️ **IMPORTANT DISCLAIMER**\n\n"
            "This tool provides **general information and mathematical projections only**. "
            "It does not take into account your personal objectives, financial situation, or needs. "
            "It is **not** personal financial advice.\n\n"
            "Users should consider whether this information is appropriate and seek professional advice."
        )

def render_footer_disclaimer():
    """Renders the 'Next Steps' info box at the bottom of calculators."""
    st.markdown("---")
    st.info(
        "👋 **General Insights**\n\n"
        "The scenarios and figures shown are illustrative models. "
        "Strategies discussed are complex and rely on specific assumptions. "
        "For information tailored to your specific circumstances, "
        "many Australians find it helpful to seek advice from a licensed professional."
    )

def render_chart_disclaimer():
    """Renders small print specifically for charts and graphs."""
    st.caption(
        "*These results are illustrative only, based on simplified assumptions, and are not a prediction or a recommendation. "
        "They do not account for your full financial situation.*"
    )

def get_projection_disclaimer():
    """Returns standard text for use near calculation results."""
    return (
        "Figures are mathematical projections based on the variables provided and historical assumptions. "
        "They are not predictions or guarantees of future performance. "
        "This is an illustrative model, not a financial forecast."
    )
