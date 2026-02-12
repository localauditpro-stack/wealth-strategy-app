import streamlit as st
import plotly.graph_objects as go
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer, get_projection_disclaimer

def render_tier4():
    """Renders the Tier 4 'Strategy & Legacy' Calculator."""
    
    # --- 1. Header Compliance Warning ---
    st.warning("⚠️ **Hypothetical Scenarios**: The following results are hypothetical scenarios based on the data provided and historical tax facts. They are not a recommendation to acquire or dispose of a financial product.")

    st.markdown("### 🏛️ Strategy & Legacy Planner")
    st.markdown("""
    Model advanced wealth preservation strategies including **FIRE (Financial Independence)**, **Estate Planning**, and **Tax Optimization**.
    """)

    # --- 2. Data Integration ---
    # Pull from Tier 1 (Profile)
    profile = st.session_state.get('user_profile', {})
    age = profile.get('age', 50)
    income = profile.get('income', 200000) # HHI
    
    # Pull from Tier 3 (Super)
    # Try to get projected balance, otherwise fallback to current or default
    tier3_results = st.session_state.get('tier3_results', {})
    
    default_super_balance = 500000
    if tier3_results:
        # If they've done Tier 3, use their current balance or projected? 
        # The prompt says "CurrentSuperBalance from Tier 3".
        # Let's use current balance + maybe a growth factor if they are older? 
        # For simple integration, let's use the 'current_balance' from Tier 3 inputs if available.
        default_super_balance = tier3_results.get('current_balance', 500000)
    
    # If not in Tier 3 results, check if they put it in global profile? (Tier 1 doesn't ask for Super balance)
    # We will just ask for it here with a sensible default.

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Your Profile")
        current_age = st.number_input("Current Age", value=age, min_value=18, max_value=90, step=1)
        hhi = parse_currency_input("Household Income ($)", income, key="t4_income")
        
    with col2:
        st.subheader("💰 Asset Base")
        super_balance = parse_currency_input("Current Super Balance ($)", default_super_balance, key="t4_super")
        # Taxable portion input (Default 100% for general advice simplicity, but allow edit)
        taxable_portion = st.slider("Taxable Component of Super (%)", 0, 100, 85, help="Percentage of super balance subject to death benefits tax (usually 100% minus non-concessional contributions)") / 100

    st.divider()

    # --- 3. Core Logic & Visualization ---
    
    # A. FIRE Bridge
    st.markdown("#### 🔥 FIRE Bridge Calculation")
    st.markdown("Determine the gap between your desired early retirement age and access to Super (Age 60).")
    
    col_fire_1, col_fire_2 = st.columns(2)
    with col_fire_1:
        lifestyle_target = parse_currency_input("Desired Annual Lifestyle ($)", 100000, key="t4_lifestyle")
        
    preservation_age = 60
    years_to_bridge = max(0, preservation_age - current_age)
    bridge_fund_needed = years_to_bridge * lifestyle_target
    
    with col_fire_2:
        if current_age < 60:
            st.metric(
                label=f"Bridge Fund Needed (Age {current_age} to 60)", 
                value=f"${bridge_fund_needed:,.0f}",
                delta=f"{years_to_bridge} Years funding required",
                delta_color="inverse"
            )
        else:
            st.success("✅ You have reached preservation age. Full access to Super is available (subject to retirement condition).")

    st.divider()

    # B. Estate Scorer (Death Benefits Tax)
    st.markdown("#### 💀 Estate Tax Liability Scorer")
    st.markdown(f"Estimate the potential tax bill for non-dependants (e.g., adult children) inheriting your Super.")
    
    # Calculation: CurrentSuper * Taxable% * 17% (15% tax + 2% Medicare)
    estate_tax_liability = super_balance * taxable_portion * 0.17
    
    # Scope Note
    st.caption("ℹ️ *Estate Tax Note: Death benefits tax modeling assumes payment to a non-tax dependent beneficiary (e.g., an adult child). Medicare Levy (2%) is included in the 17% calculation.*")

    col_est_1, col_est_2 = st.columns([1, 2])
    
    with col_est_1:
         st.metric(
            label="Potential Death Benefits Tax",
            value=f"${estate_tax_liability:,.0f}",
            delta=f"Erodes {17 * taxable_portion:.1f}% of Balance",
            delta_color="inverse"
        )
         
    with col_est_2:
        # Minimalist Bar Chart for Wealth Gap / Tax
        fig_estate = go.Figure()
        fig_estate.add_trace(go.Bar(
            y=['Estate Value'],
            x=[super_balance],
            name='Total Super',
            orientation='h',
            marker_color='#1A2B3C' # Deep Navy
        ))
        fig_estate.add_trace(go.Bar(
            y=['Estate Value'],
            x=[estate_tax_liability],
            name='Potential Tax',
            orientation='h',
            marker_color='#C5A059' # Champagne Gold
        ))
        
        fig_estate.update_layout(
            barmode='overlay', 
            title="Impact of Death Benefits Tax",
            height=200,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_estate, use_container_width=True)

    st.divider()

    # C. Recontribution Strategy
    st.markdown("#### 🔄 Recontribution Strategy")
    st.markdown("Model the tax savings of a **'Wash Strategy'**: Withdrawing taxable super and re-contributing it as Non-Concessional (Tax-Free).")
    
    wash_amount = 360000 # Max bring-forward cap
    # Can only wash up to the balance amount
    wash_amount = min(wash_amount, super_balance)
    
    # Savings = WashAmount * TaxablePortion * 17%
    # Logic: We are converting 'WashAmount' from Taxable to Tax-Free.
    # The tax saved is the tax that WOULD have been paid on that component.
    tax_saved = wash_amount * taxable_portion * 0.17
    
    # Scope Note
    st.caption("ℹ️ *Recontribution Note: Calculations assume the user meets all eligibility criteria for non-concessional contributions and the bring-forward rule. The proportioning rule is applied conceptually; actual results depend on specific fund components.*")
    
    col_re_1, col_re_2 = st.columns(2)
    
    with col_re_1:
        st.info(f"**Strategy:** Withdraw & Re-contribute **${wash_amount:,.0f}**")
        
    with col_re_2:
        st.metric(
            label="Projected Tax Saved for Beneficiaries",
            value=f"${tax_saved:,.0f}",
            delta="Wealth Preserved",
            delta_color="normal" # Green/Positive
        )

    # --- 4. Call to Action (CTA) ---
    st.divider()
    
    # 'Whale' Lead Logic
    is_whale = hhi >= 300000
    
    cta_container = st.container(border=True)
    with cta_container:
        if is_whale:
            col_cta_1, col_cta_2 = st.columns([2, 1])
            with col_cta_1:
                st.markdown("### 🌟 Specialized Strategy Required")
                st.write("Your scenario involves complex tax and structure considerations. Move from a general model to a tailored plan.")
                st.write("_Our partners provide formal Statements of Advice (SOA) that consider your personal objectives._")
            with col_cta_2:
                # Gold Button
                st.markdown("""
                    <style>
                    div.stButton > button.gold-button {
                        background-color: #C5A059 !important;
                        color: white !important;
                        font-weight: bold;
                        border: none;
                        padding: 0.5rem 1rem;
                    }
                    </style>
                """, unsafe_allow_html=True)
                if st.button("Request Formal Strategy Audit", key="btn_audit", type="primary"): 
                     st.success("Request received. A Senior Strategist will contact you shortly.")
        else:
             st.markdown("### 📅 Book a Discovery Call")
             st.write("Discuss these results with a financial adviser to understand your options.")
             if st.button("Book Discovery Call", key="btn_discovery"):
                 st.success("Booking system loading...")

    # --- 5. Mandatory Footer ---
    # Rendered via fixed HTML/CSS component
    render_sticky_footer_disclaimer()

def render_sticky_footer_disclaimer():
    """Renders a sticky footer disclaimer as per compliance requirements."""
    st.markdown("""
        <style>
        .sticky-footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f0f2f6;
            color: #666;
            text-align: center;
            padding: 10px;
            font-size: 0.8rem;
            border-top: 1px solid #ddd;
            z-index: 999;
        }
        .main .block-container {
            padding-bottom: 60px; /* Make space for footer */
        }
        </style>
        <div class="sticky-footer">
            Scenario modelling for illustrative purposes only. No Financial Advice provided.
        </div>
    """, unsafe_allow_html=True)
