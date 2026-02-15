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
    st.title("Information Summary (Illustrative Synthesis)")
    
    from utils.compliance import render_general_advice_warning_above_fold, render_data_usage_explanation
    render_general_advice_warning_above_fold()
    render_data_usage_explanation()

    st.markdown("""
    **Synthesis of Illustrative Scenarios**
    
    This page provides a synthesized view of the various mathematical models and concepts explored throughout the tool. 
    It is provided for educational purposes only and does not constitute a recommendation or financial advice.
    """)
    
    # --- 1. Lead Gate ---
    # Check if lead data exists (email/phone captured)
    if 'lead_data' not in st.session_state or not st.session_state.lead_data.get('email'):
        st.info("🔒 **This information summary is reserved for registered users.**")
        st.write("Unlock a synthesized view of the illustrative scenarios, concepts, and areas for potential exploration identified in the previous tiers.")
        
        if render_lead_capture_form("summary_gate", button_label="Unlock My Information Summary"):
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
            go_to_page("Tier 1: Clarity (Readiness)")
        return

    # --- 3. Dashboard Layout ---
    
    st.markdown(f"### 👤 Profile Scenario: {profile.get('risk_tolerance', 'Balanced')} Investor Category")
    
    # Top Row: Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Opportunity Cost (Super)
        if tier3 and 'hg_projection' in tier3 and 'bal_projection' in tier3:
            hg_final = tier3['hg_projection']['balance'][-1]
            bal_final = tier3['bal_projection']['balance'][-1]
            diff = hg_final - bal_final
            if diff > 0:
                st.metric("Illustrative Super Gain", f"+${diff:,.0f}", help="Potential mathematical difference by modeling High Growth (Projected at retirement)")
            else:
                st.metric("Super Strategy", "Optimized", help="Your current strategy appears aligned.")
        else:
            st.metric("Super Opportunity", "Not Calculated", help="Run Tier 3 calculator to see this.")

    with col2:
        # FIRE Gap
        if fire:
            gap = fire.get('gap', 0)
            if fire.get('success'):
                st.metric("Illustrative FIRE Model", "Sustained", delta="Modeled")
            else:
                st.metric("Illustrative FIRE Gap", f"-${gap:,.0f}", delta="Gap modeled", delta_color="inverse")
        else:
             st.metric("FIRE Gap", "Pending", help="Run Tier 4 calculator.")

    with col3:
        # Estate Tax
        if legacy:
            future_tax = legacy.get('future_tax', 0)
            st.metric("Illustrative Death Tax Impact", f"${future_tax:,.0f}")
        else:
             st.metric("Estate Risk", "Pending", help="Run Tier 5 calculator.")

    st.divider()
    
    # --- 4. Synthesis & Actions ---
    
    c_syn, c_act = st.columns([1, 1])
    
    with c_syn:
        st.subheader("🔍 Illustrative Insights")
        
        # Risk Insight
        risk = profile.get('risk_tolerance', 'Balanced')
        if risk in ["High Growth", "Moderate Growth"]:
             st.success(f"**Growth Orientation:** This **{risk}** profile is often associated with efforts to capture long-term market premiums, assuming one is comfortable with volatility.")
        else:
             st.info(f"**Defensive Orientation:** This **{risk}** profile prioritizes historical stability. It's often helpful to monitor how inflation might impact purchasing power over very long timeframes.")

        # Super Insight
        if tier3:
             gain_val = tier3.get('hg_projection', {}).get('balance', [0])[-1] - tier3.get('bal_projection', {}).get('balance', [0])[-1]
             if gain_val > 100000:
                 st.write(f"🚀 **Compounding Concept:** In this model, optimizing the allocation represents a potential projection difference of over **\${gain_val:,.0f}** by retirement.")

        # Legacy Insight
        if legacy and legacy.get('future_tax', 0) > 100000:
             st.warning(f"⚠️ **Preserved Wealth:** Without considering preservation concepts such as recontribution, this model suggests a potential tax impact of approx **\${legacy['future_tax']:,.0f}** upon estate transfer.")

    with c_act:
        st.subheader("✅ Common Areas for Exploration")
        
        actions = []
        
        # Logic for actions
        if fire and not fire.get('success'):
             actions.append("1. **Modeled FIRE Gaps:** Many people in this scenario explore how adjusting 'Outside Super' savings rates might affect the projection.")
        
        if tier3:
             actions.append("2. **Investment Options:** You could consider reviewing your Super PDS and how your current allocation aligns with different risk-return models.")
        
        if legacy and legacy.get('future_tax', 0) > 50000:
             actions.append("3. **Preservation Concepts:** Consider learning more about how 'Recontribution' models work as a potential way to manage future tax impacts.")
             
        if not actions:
             actions.append("1. **Information Deep-Dive:** Run Tiers 2-5 to see the various mathematical models applied to your scenario.")
             
        for action in actions:
            st.markdown(action)
            
        st.markdown("---")
        st.caption("Want to discuss these concepts further?")
        if st.button("📅 Book Information Session", type="primary", use_container_width=True):
             st.success("Request received! We will contact you shortly to arrange an educational session.")

    render_footer_disclaimer()
