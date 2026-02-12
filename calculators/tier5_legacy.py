import streamlit as st
import plotly.graph_objects as go
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer, get_projection_disclaimer

def render_tier5_legacy():
    """Renders the Tier 5 'Legacy & Estate' Calculator."""
    
    # --- 1. Header Compliance Warning ---
    st.warning("⚠️ **Hypothetical Scenarios**: The following results are hypothetical scenarios based on the data provided and historical tax facts. They are not a recommendation to acquire or dispose of a financial product.")

    st.markdown("### 🏛️ Tier 5: Legacy & Estate Planning")
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
        taxable_portion = st.slider("Taxable Component of Super (%)", 0, 100, 85, help="Source: ATO data implies high taxable components for most accumulation accounts (unless recontribution strategies used). Taxed at 15% + 2% Medicare for non-dependants.") / 100

    st.divider()

    # --- 3. Core Logic & Visualization ---
    
    # A. FIRE Bridge Link
    st.markdown("#### 🔥 FIRE Bridge Calculation")
    st.markdown("Planning to retire before 60? You need a 'Bridge' of capital to get you to preservation age.")
    
    col_fire_1, col_fire_2 = st.columns([3, 1])
    with col_fire_1:
         st.info("💡 We've moved the FIRE Bridge to its own dedicated calculator with advanced market modeling.")
    with col_fire_2:
         # Visual placeholder or button handled in app navigation mostly, but we can add a direct link button style if needed
         # or just text directing them.
         st.write("👉 Select **FIRE Path** from the main menu")


    st.divider()

    # B. Estate Scorer (Death Benefits Tax)
    st.markdown("#### 💀 Estate Tax Liability Scorer")
    st.markdown(f"Estimate the potential tax bill for non-dependants (e.g., adult children) inheriting your Super.")
    
    # Calculation: CurrentSuper * Taxable% * 17% (15% tax + 2% Medicare)
    estate_tax_liability = super_balance * taxable_portion * 0.17
    
    # Scope Note
    # Scope Note
    st.caption("ℹ️ *Estate Tax Note: Estimates potential 'Death Benefits Tax' (Taxable Component x 15% + 2% Medicare Levy) applicable to non-dependant beneficiaries (e.g. adult children).*")

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
            title="Impact of Death Benefits Tax (Today)",
            height=200,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_estate, use_container_width=True)

    # --- Future Projection (The "Wake Up Call") ---
    
    # Calculate Projected Balance (if not already simulated)
    projected_balance = 0
    if tier3_results and 'hg_projection' in tier3_results:
         projected_balance = tier3_results['hg_projection']['balance'][-1]
    elif tier3_results and 'bal_projection' in tier3_results:
         projected_balance = tier3_results['bal_projection']['balance'][-1]
    else:
        # Simple Fallback: 7% return + $15k contrib until 65
        years_to_65 = max(0, 65 - current_age)
        if years_to_65 > 0:
            r = 0.07
            c = 15000 
            projected_balance = super_balance * ((1 + r) ** years_to_65)
            projected_balance += c * (((1 + r) ** years_to_65 - 1) / r)
        else:
            projected_balance = super_balance

    future_tax = projected_balance * taxable_portion * 0.17
    
    st.info(f"""
    🔮 **Future Projection:** If your balance grows to **${projected_balance/1000000:.1f}M** by retirement, 
    the potential tax bill for your beneficiaries swells to **${future_tax:,.0f}**.
    
    *Legacy planning isn't just for today—it's about protecting your future wealth.*
    """)

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

    # Save results to session state for Summary Page
    st.session_state['legacy_results'] = {
        'current_tax': estate_tax_liability,
        'future_tax': future_tax,
        'taxable_portion': taxable_portion,
        'projected_balance': projected_balance
    }

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
