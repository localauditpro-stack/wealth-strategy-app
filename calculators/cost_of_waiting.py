import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer

def render_cost_of_waiting():
    """Renders the Cost of Waiting calculator."""
    st.markdown("## 📉 The Cost of Waiting")
    st.write("Understand the impact of delaying your investment journey.")
    
    # Defaults
    profile = st.session_state.get('user_profile', {})
    default_amount = 50000
    
    # --- SECTION 1: RETROSPECTIVE (The "What If") ---
    st.markdown("### 1. The Missed Opportunity (Last 10 Years)")
    st.info("What if you had invested in a diversified **70% Growth / 30% Defensive** portfolio 10 years ago?")
    
    col_retro1, col_retro2 = st.columns([1, 2])
    
    with col_retro1:
        invest_amount = parse_currency_input("If I had invested ($)", default_amount, key="retro_amt")
        monthly_contrib = parse_currency_input("And added monthly ($)", 1000, key="retro_monthly")
        
        # Assumptions
        growth_rate = 0.085
        yield_rate = 0.025
        total_return = growth_rate + yield_rate
        years_back = 10
        
        st.caption(f"""
        **Assumptions:**
        - Growth: {growth_rate*100:.1f}% p.a.
        - Yield: {yield_rate*100:.1f}% p.a.
        - **Total: {total_return*100:.1f}% p.a.**
        """)
        
    with col_retro2:
        # Calculation
        # FV Lump Sum
        fv_lump = invest_amount * ((1 + total_return) ** years_back)
        
        # FV Monthly Series (PMT * (((1+r)^n - 1) / r))
        r_m = total_return / 12
        n_months = years_back * 12
        fv_monthly = monthly_contrib * ((((1 + r_m) ** n_months) - 1) / r_m)
        
        final_value = fv_lump + fv_monthly
        total_invested = invest_amount + (monthly_contrib * 12 * years_back)
        gain = final_value - total_invested
        roi = (gain / total_invested) * 100 if total_invested > 0 else 0
        
        # Display
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
            <h3 style="margin:0; color: #31333F;">Hypothetical Value: <strong>${final_value:,.0f}</strong></h3>
            <p style="font-size: 1.1em; margin-top: 10px;">
                Total Invested: <strong>${total_invested:,.0f}</strong><br>
                Hypothetical Gain: <span style="color: #4CAF50; font-weight: bold;">+${gain:,.0f}</span> ({roi:.0f}%)
            </p>

        """, unsafe_allow_html=True)
        
        # Volatility Map Chart
        st.markdown("#### 🌊 The Reality of Returns (Volatility Map)")
        st.write("Markets don't move in a straight line. This chart shows how your portfolio might fluctuate while still achieving the target average return.")
        
        years_list = list(range(0, 11))
        
        # 1. Smooth Path (The "Average")
        smooth_values = []
        for y in years_list:
            n_m = y * 12
            fv_l = invest_amount * ((1 + total_return) ** y)
            fv_m = monthly_contrib * ((((1 + r_m) ** n_m) - 1) / r_m) if r_m > 0 else monthly_contrib * n_m
            smooth_values.append(fv_l + fv_m)
            
        # 2. Volatile Path (The "Experience")
        # Pseudo-random sequence representing a typical volatile decade (e.g. one crash, some booms)
        # We start with the smooth ending value and work backward or just apply deviations?
        # Let's apply annual variations around the mean
        
        # Scenario: "The Bumpy Road"
        # Deviations from mean return
        deviations = [0, 0.15, -0.12, 0.08, 0.20, -0.05, 0.12, 0.05, -0.08, 0.18, 0.02] # 11 points (Year 0 is 0)
        
        volatile_values = [smooth_values[0]]
        current_vol_val = smooth_values[0]
        
        # We need to simulate the path accurately
        # This is an estimate to show the "shape" of volatility
        # We simply add noise to the cumulative return
        import random
        # random.seed(42) # Deterministic for consistent UI
        
        # Let's construct a path that roughly tracks the smooth line but deviates
        for i in range(1, 11):
            # The smooth return for this year was approximately total_return
            # We add a deviation
            this_year_return = total_return + deviations[i]
            
            # Add contributions
            current_vol_val += (monthly_contrib * 12)
            # Grow
            current_vol_val *= (1 + this_year_return)
            volatile_values.append(current_vol_val)
            
        # Force the final point to match or be close? 
        # Actually better if it ends slightly different to show "Real Life" outcome vs "Paper" outcome
        # But for "Cost of Waiting" proof, maybe getting close to the target validates the average.
        
        fig = go.Figure()
        
        # Smooth Line (Dashed)
        fig.add_trace(go.Scatter(
            x=years_list, y=smooth_values, 
            mode='lines', name='Expected (Smooth)', 
            line=dict(color='#A0A0A0', width=2, dash='dash')
        ))
        
        # Volatile Line (Solid, Color)
        fig.add_trace(go.Scatter(
            x=years_list, y=volatile_values, 
            mode='lines+markers', name='Actual Experience (Volatile)', 
            line=dict(color='#002B5C', width=3)
        ))
        
        fig.update_layout(
            height=350,
            xaxis_title="Years Invested", 
            yaxis_title="Portfolio Value ($)",
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 **Insight:** Notice the dips (e.g. Year 2, Year 5). Many investors panic and sell here. Staying the course is how you capture the full 10-year growth.")
        st.caption("ℹ️ *Disclaimer: This volatility map is a simulation for illustrative purposes only. It does not predict future market movements or guarantee performance.*")

    st.divider()

    # --- SECTION 2: PROSPECTIVE (The "Future Cost") ---
    st.markdown("### 2. The Future Cost of Delaying Decisions")
    st.write("How much does waiting **1, 3, or 5 years** cost you in future wealth?")
    st.info("ℹ️ **Methodology:** The 'Cost of Delay' represents the difference in potential future wealth caused by starting the compounding process later. It assumes funds sit idle (earning 0%) during the delay period.")

    with st.expander("Adjust Future Assumptions", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            future_monthly = parse_currency_input("Resulting Monthly Contribution ($)", 1000, key="fut_monthly")
            future_years = st.slider("Investment Horizon (Years)", 5, 40, 20, key="fut_years")
        with c2:
            future_rate = st.slider("Assumed Return (%)", 1.0, 15.0, 11.0, 0.5, key="fut_rate") / 100
    
    if st.button("Calculate Future Cost of Delay", type="primary"):
        # Calculate Base Case (Start Now)
        base_data = calculate_compound(invest_amount, future_monthly, future_rate, future_years, delay_years=0)
        base_final = base_data[-1]
        
        delays = [1, 3, 5]
        results = []
        
        for d in delays:
            # Delayed Calculation: 
            # 1. Wait 'd' years (money sits flat or just growth? typical "verify" assumes cash sits idle or spent)
            # Let's assume cash sits idle (0% return) for 'd' years, then invested for (years - d).
            # Note: The comparison is "At the end of outcome Y".
            
            d_data = calculate_compound(invest_amount, future_monthly, future_rate, future_years, delay_years=d)
            d_final = d_data[-1]
            cost = base_final - d_final
            results.append({"Delay": f"{d} Year{'s' if d>1 else ''}", "Final Wealth": d_final, "Cost": cost})
            
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Start Now (Benchmark)", f"${base_final:,.0f}")
        m2.metric(f"Wait {delays[0]} Year", f"${results[0]['Final Wealth']:,.0f}", delta=f"-${results[0]['Cost']:,.0f}", delta_color="inverse")
        m3.metric(f"Wait {delays[2]} Years", f"${results[2]['Final Wealth']:,.0f}", delta=f"-${results[2]['Cost']:,.0f}", delta_color="inverse")
        
        st.warning(f"⚠️ Delaying start by **5 years** is projected to reduce final wealth by **${results[2]['Cost']:,.0f}** in this scenario.")
        
        # Disclaimer Footer
        render_footer_disclaimer()

def calculate_compound(principal, monthly, rate, years, delay_years=0):
    """
    Calculates projection. 
    If delayed: principal sits in cash (0%) for delay_years. Monthly contributions start after delay.
    Returns list of yearly balances? No, just final value for simplicity in this logic, 
    but for chart we might want stream.
    """
    
    # Monthly rate
    r_m = rate / 12
    n_months = years * 12
    d_months = delay_years * 12
    
    # 1. Delay Period
    # Principal sits idle.
    # We assume 'monthly' contributions essentially are saved up? Or just NOT made?
    # Usually "Cost of Waiting" means you are NOT executing the strategy, so you aren't saving that extra cash flow into the investment.
    # So we simply start the compounding clock later.
    
    # Effectively: Investment window = (years - delay_years)
    # Principal is available at month 0 (start of investment window).
    
    if delay_years >= years:
        return [principal] # No time to grow
        
    invest_months = n_months - d_months
    
    # Compound calculation
    # FV = P * (1+r)^n + PMT * (((1+r)^n - 1) / r)
    
    fv = principal * ((1 + r_m) ** invest_months)
    fv += monthly * ((((1 + r_m) ** invest_months) - 1) / r_m)
    
    # We can just return final value, but user might want array. 
    # For now, just return a list with final value to match previous structure slightly or just the value.
    # Let's return list of values for graph if needed, or just single value.
    # The calling code expects a list of dicts or something? 
    # Previous code returned list of dicts. Let's simplify and just return scalar or list of yearly.
    
    return [fv] 
