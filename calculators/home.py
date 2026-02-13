import streamlit as st
from utils.ui import go_to_page

def render_home():
    """Renders the comprehensive and educational Home Page."""
    
    # Hero Section - Enhanced
    st.markdown("""
        <div class="hero">
            <h1>Structure Your Wealth</h1>
            <p>The difference between earning money and building wealth is <b>structure</b>.<br>
            A data-driven roadmap to build, accelerate, and protect your financial future.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # The Problem / Hook - Educational
    st.markdown("### ⚠️ The Problem: Financial Clutter")
    st.markdown("""
    Most high-income earners build wealth by accident—buying a property here, some shares there, and hoping for the best. 
    This leads to **"Financial Clutter"**: inefficient tax structures, lazy equity, and no clear direction.
    
    Without a cohesive strategy, you are likely leaking wealth to **Tax**, **Inflation**, and **Opportunity Cost**.
    """)
    
    st.divider()

    # The Methodology: The Wealth Pyramid
    st.markdown("## 🏛️ The Methodology: A Structured Approach")
    st.write("We break wealth building into 3 distinct phases, supported by 5 Pillars. You cannot build the roof before the foundation.")

    # Phase 1: Foundation
    st.markdown("### Phase 1: Foundation")
    
    # Full-width card for Phase 1
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown("### 1. Clarity")
            st.caption("The Assessment")
            st.info("**Start Here**")
        with c2:
            st.markdown("**Why it matters:** You can't build a skyscraper on quicksand. Before engaging complex tax structures or debt recycling, you must quantify your **Readiness Score**.")
            st.write("Do you have the surplus income, equity buffer, and risk tolerance to support leverage?")
            if st.button("Start Assessment (Tier 1) 👉", key="btn_p1", type="primary"):
                go_to_page("Tier 1: Clarity (Readiness)")

    st.markdown("---")

    # Phase 2: Growth & Acceleration
    st.markdown("### Phase 2: Growth & Acceleration")
    c_g1, c_g2 = st.columns(2)
    
    with c_g1:
        with st.container(border=True):
            st.markdown("#### 2. Direction (Strategy)")
            st.caption("The Vehicle")
            st.markdown("""
            **The Dilemma:** Should I buy an investment property or a share portfolio?
            
            **The Solution:** Compare the long-term outcomes of **Debt Recycling** vs. **Leveraged Property**.
            
            **Key Metric:** 10-Year Net Wealth Gap.
            """)
            if st.button("Compare Strategies (Tier 2) 👉", key="btn_p2"):
                go_to_page("Tier 2: Direction (Strategy)")

    with c_g2:
        with st.container(border=True):
            st.markdown("#### 3. Acceleration (Super)")
            st.caption("The Engine")
            st.markdown("""
            **The Dilemma:** Super feels locked away, so I usually ignore it.
            
            **The Reality:** It is your most powerful tax shelter. Small changes now compound massively.
            
            **Key Metric:** The Cost of Waiting.
            """)
            st.button("Optimise Super (Tier 3) 👉", key="btn_p3", on_click=lambda: go_to_page("Tier 3: Acceleration (Super)"))

    st.markdown("---")

    # Phase 3: Freedom & Legacy
    st.markdown("### Phase 3: Freedom & Legacy")
    c_f1, c_f2 = st.columns(2)
    
    with c_f1:
        with st.container(border=True):
            st.markdown("#### 4. Freedom (FIRE)")
            st.caption("The Destination")
            st.markdown("""
            **The Goal:** Work becomes optional.
            
            **The Mechanism:** Calculate your "FI Number" and build a **"Bridge"** to get you there.
            
            **Key Metric:** Years to Financial Freedom.
            """)
            st.button("Plan Freedom (Tier 4) 👉", key="btn_p4", on_click=lambda: go_to_page("Tier 4: Freedom (FIRE)"))

    with c_f2:
        with st.container(border=True):
            st.markdown("#### 5. Protection (Legacy)")
            st.caption("The Fortress")
            st.markdown("""
            **The Risk:** "Death Benefits Tax" can take **17%** of your Super to the ATO.
            
            **The Fix:** Recontribution strategies and testamentary trusts to protect it.
            
            **Key Metric:** Projected Tax Saving.
            """)
            st.button("Protect Legacy (Tier 5) 👉", key="btn_p5", on_click=lambda: go_to_page("Tier 5: Protection (Legacy)"))
                
    st.divider()
    
    # Educational Section: The 3 Enemies
    st.markdown("### ⚔️ The 3 Enemies of Wealth")
    st.write("Even high earners fail because they ignore these three silent killers.")
    
    e1, e2, e3 = st.columns(3)
    with e1:
         st.error("**1. The Silent Tax Leak**")
         st.markdown("""
         Earning **\$180,000+**? You are losing nearly half your extra effort to tax. 
         
         *The Fix:* Structural changes convert personal debt into tax-deductible debt.
         """)
    with e2:
         st.warning("**2. Inflation (The Thief)**")
         st.markdown("""
         Leaving **\$100,000** in cash feels safe, but at 3% inflation, its purchasing power halves.
         
         *The Fix:* Assets must work harder than inflation. Lazy equity is a wasted resource.
         """)
    with e3:
         st.info("**3. Procrastination**")
         st.markdown("""
         The "Cost of Waiting" is exponential. Delaying investment by 5 years costs **over \$500,000**.
         
         *The Fix:* Start structurally, even if you start small.
         """)

    st.divider()
    
    # Who is this for?
    with st.expander("🤔 Who is this tool designed for?"):
        st.markdown("""
        This Strategy Generator is optimized for Australian investors who typically fit this profile:
        
        *   **Homeowners** with some equity (approx. \$200k+) looking to "recycle" it.
        *   **High Income Households** (\$180k+ combined) seeking tax efficiency.
        *   **Aspirational Builders** who want data-driven validation.
        
        *If you are just starting out, Tier 1 (Readiness) will give you a clear roadmap.*
        """)

    st.markdown("---")
    st.caption("Select a **Tier** above or use the sidebar navigation to begin your assessment.")
