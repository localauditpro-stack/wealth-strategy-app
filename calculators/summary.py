import streamlit as st
import plotly.graph_objects as go
from utils.leads import render_lead_capture_form
from utils.compliance import render_footer_disclaimer
from utils.ui import go_to_page

def render_summary_page():
    """
    Renders the 'Strategy Summary' page.
    This is a synthesis of all previous tiers, gated by lead capture.
    """
    st.markdown("## 📋 Your Strategy Snapshot")
    st.write("A synthesized view of your financial position, risks, and opportunities.")
    
    # --- 1. Lead Gate ---
    # Check if lead data exists (email/phone captured)
    if 'lead_data' not in st.session_state or not st.session_state.lead_data.get('email'):
        st.info("🔒 **This strategic summary is reserved for registered users.**")
        st.write("Unlock your personalized 1-page synthesis to see your key risks, opportunities, and next best actions.")
        
        if render_lead_capture_form("summary_gate", button_label="Unlock My Strategy Snapshot"):
            st.rerun()
            
        # Stop rendering rest of page if locked
        return

    # --- 2. Data Aggregation ---
    profile = st.session_state.get('user_profile', {})
    tier3 = st.session_state.get('tier3_results', {})
    fire = st.session_state.get('fire_results', {})
    legacy = st.session_state.get('legacy_results', {})
    
    if not profile:
        st.warning("⚠️ No profile data found. Please complete Tier 1 first.")
        if st.button("Go to Tier 1"):
            go_to_page("Tier 1: Financial Readiness")
        return

    # --- 3. Dashboard Layout ---
    
    st.markdown(f"### 👤 Profile: {profile.get('risk_tolerance', 'Balanced')} Investor")
    
    # Top Row: Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Opportunity Cost (Super)
        if tier3 and 'hg_projection' in tier3 and 'bal_projection' in tier3:
            hg_final = tier3['hg_projection']['balance'][-1]
            bal_final = tier3['bal_projection']['balance'][-1]
            diff = hg_final - bal_final
            if diff > 0:
                st.metric("Super Optimization Gain", f"+${diff:,.0f}", help="Potential gain by switching to High Growth (Projected at retirement)")
            else:
                st.metric("Super Strategy", "Optimized", help="Your current strategy appears aligned.")
        else:
            st.metric("Super Opportunity", "Not Calculated", help="Run Tier 3 calculator to see this.")

    with col2:
        # FIRE Gap
        if fire:
            gap = fire.get('gap', 0)
            if fire.get('success'):
                st.metric("FIRE Viability", "On Track", delta="Funded")
            else:
                st.metric("FIRE Shortfall", f"-${gap:,.0f}", delta="Gap detected", delta_color="inverse")
        else:
             st.metric("FIRE Gap", "Pending", help="Run Tier 4 calculator.")

    with col3:
        # Estate Tax
        if legacy:
            future_tax = legacy.get('future_tax', 0)
            st.metric("Projected Death Tax", f"${future_tax:,.0f}", delta="Wealth Erosion", delta_color="inverse")
        else:
             st.metric("Estate Risk", "Pending", help="Run Tier 5 calculator.")

    st.divider()
    
    # --- 4. Synthesis & Actions ---
    
    c_syn, c_act = st.columns([1, 1])
    
    with c_syn:
        st.subheader("🔍 Key Insights")
        
        # Risk Insight
        risk = profile.get('risk_tolerance', 'Balanced')
        if risk in ["High Growth", "Moderate Growth"]:
             st.success(f"**Growth Orientation:** Your **{risk}** profile suggests you are well-positioned to capture long-term market premiums, provided you can weather volatility.")
        else:
             st.info(f"**Defensive Bias:** Your **{risk}** profile prioritizes safety. Ensure this doesn't lead to inflation eroding your purchasing power over time.")

        # Super Insight
        if tier3:
             gain_val = tier3.get('hg_projection', {}).get('balance', [0])[-1] - tier3.get('bal_projection', {}).get('balance', [0])[-1]
             if gain_val > 100000:
                 st.write(f"🚀 **Super Power:** optimizing your allocation could add over **${gain_val:,.0f}** to your retirement without contributing an extra cent.")

        # Legacy Insight
        if legacy and legacy.get('future_tax', 0) > 100000:
             st.warning(f"⚠️ **Legacy Alarm:** Without a recontribution strategy, the ATO could become a major beneficiary of your estate (approx **${legacy['future_tax']:,.0f}**).")

    with c_act:
        st.subheader("✅ Next Best Actions")
        
        actions = []
        
        # Logic for actions
        if fire and not fire.get('success'):
             actions.append("1. **Bridge the FIRE Gap:** Review your 'Outside Super' savings rate. A 10% increase now can reduce your FIRE age by years.")
        
        if tier3:
             actions.append("2. **Review Super Fund:** Check your current PDS to ensure you aren't in a default 'Balanced' option if your risk profile allows for 'High Growth'.")
        
        if legacy and legacy.get('future_tax', 0) > 50000:
             actions.append("3. **Implement Wash Strategy:** Consider a 'Recontribution' strategy between age 60-65 to wash out the taxable component of your super.")
             
        if not actions:
             actions.append("1. **Complete All Calculators:** Run Tiers 2-5 to generate specific actions.")
             
        for action in actions:
            st.markdown(action)
            
        st.markdown("---")
        st.caption("Need help implementing this?")
        if st.button("📅 Book Strategy Call with Advisor", type="primary", use_container_width=True):
             st.success("Booking request sent! We will contact you shortly.")

    render_footer_disclaimer()
