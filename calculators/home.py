import streamlit as st
from utils.ui import go_to_page

def render_home():
    """Renders the simplified and educational Home Page."""
    
    # Hero Section
    st.markdown("""
        <div class="hero">
            <h1>Structure Your Wealth</h1>
            <p>From chaos to clarity. A data-driven roadmap for Australian investors to build, accelerate, and protect their future.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # The Problem / Hook
    st.markdown("### ⚠️ Why Most Investors Fail")
    st.markdown("""
    Most people build wealth by accident—buying a property here, some shares there, and hoping for the best. 
    This leads to **"Financial Clutter"**: inefficient tax structures, lazy equity, and no clear direction.
    
    **The Solution? Structure.** We break wealth building into 5 clear stages.
    """)
    
    st.divider()

    # The 5 Pillars (Philosophy)
    st.markdown("## 🏛️ The 5 Pillars of Wealth")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            st.markdown("### 1. Clarity (Readiness)")
            st.caption("The Foundation")
            st.write("Before you build, you must measure. Do you have the equity, income, and cash flow to support advanced strategies?")
            if st.button("Start Assessment 👉", key="btn_p1", type="primary"):
                go_to_page("Tier 1: Clarity (Readiness)")

        with st.container(border=True):
            st.markdown("### 2. Direction (Strategy)")
            st.caption("The Vehicle")
            st.write("Debt Recycling vs. Investment Property. Mathematical comparison of the two most powerful wealth vehicles in Australia.")
            if st.button("Compare Strategies 👉", key="btn_p2"):
                go_to_page("Tier 2: Direction (Strategy)")

        with st.container(border=True):
            st.markdown("### 3. Acceleration (Super)")
            st.caption("The Engine")
            st.write("Super isn't just for retirement. It's a low-tax environment that accelerates compounding. See the cost of waiting.")
            if st.button("Optimise Super 👉", key="btn_p3"):
                go_to_page("Tier 3: Acceleration (Super)")

    with col2:
        with st.container(border=True):
            st.markdown("### 4. Freedom (FIRE)")
            st.caption("The Destination")
            st.write("Financial Independence Retire Early. calculating your 'Example Number' and the bridge required to get there.")
            if st.button("Plan Freedom 👉", key="btn_p4"):
                go_to_page("Tier 4: Freedom (FIRE)")

        with st.container(border=True):
            st.markdown("### 5. Protection (Legacy)")
            st.caption("The Fortress")
            st.write("Building wealth is half the battle. Keeping it requires managing the hidden tax liability of death.")
            if st.button("Protect Legacy 👉", key="btn_p5"):
                go_to_page("Tier 5: Protection (Legacy)")
                
    st.divider()
    
    # Educational Hooks / Insights
    st.markdown("### 💡 Did You Know?")
    
    e1, e2 = st.columns(2)
    with e1:
         st.info("**The Silent Tax Leak:** \n\nEarning **\$180,000+**? You're losing nearly half your extra income to tax. Structural changes can convert personal debt into tax-deductible debt.")
    with e2:
         st.warning("**The Cost of Laziness:** \n\nLeaving **\$100,000** in cash vs. offsetting a mortgage vs. investing in Super can mean a difference of **over \$500,000** during a 20 year period.")

    st.markdown("---")
    st.caption("Select a pillar above or use the sidebar navigation to begin.")
