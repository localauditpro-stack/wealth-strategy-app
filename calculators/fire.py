import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy_financial as npf
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer

def render_fire_calculator():
    """Renders the dedicated FIRE (Financial Independence, Retire Early) Calculator."""
    
    st.markdown("### 🔥 Tier 4: FIRE Strategy")
    st.markdown("""
    **Financial Independence, Retire Early (FIRE)** isn't just about saving—it's about building a bridge of capital to sustain you until you can access your Superannuation (Age 60).
    
    This calculator helps you determine if your **Outside-Super** assets can bridge the gap.
    """)
    
    # --- 1. Inputs ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 You")
        # Get age from profile if available
        profile_age = st.session_state.get('user_profile', {}).get('age', 40)
        current_age = st.number_input("Current Age", 18, 65, profile_age, 1)
        fire_age = st.number_input("Desired FIRE Age", current_age + 1, 65, max(50, current_age + 5), 1)
        
    with col2:
        st.subheader("💰 The Gap")
        annual_spend = parse_currency_input("Desired Annual Spend ($/yr)", 80000, help_text="In today's dollars")
        access_age = 60 # Super preservation age
        
    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🏦 Assets (Outside Super)")
        current_investable = parse_currency_input("Current Investable Assets ($)", 100000)
        monthly_savings = parse_currency_input("Monthly Savings Contribution ($)", 2000)
        
    with col4:
        st.subheader("📈 Assumptions")
        return_rate = st.slider("Invest. Return (%)", 2.0, 12.0, 7.0, 0.5) / 100
        inflation_rate = st.slider("Inflation (%)", 1.0, 8.0, 3.0, 0.5) / 100
        tax_rate = st.slider("Avg Tax on Gains/Yield (%)", 0.0, 47.0, 20.0, 1.0, help="Estimate of tax drag on returns") / 100
        
    # Real Return = ((1 + Return) / (1 + Inflation)) - 1  ... Roughly Return - Inflation
    # But we also have TAX.
    # Net Nominal Return = Return * (1 - Tax)
    # Real Net Return ~ (Net Nominal - Inflation)
    
    # Let's keep it simple but reasonably accurate:
    # We will project in NOMINAL dollars usually, but user thinks in TODAY's dollars.
    # Easier: Project everything in REAL terms (inflation adjusted returns).
    # Real Return = (1 + Return) / (1 + Inflation) - 1
    # Tax drag is tricky in real terms.
    
    # Let's use Nominal Projection for the chart, but adjust the "Target Spend" by inflation.
    
    if st.button("🚀 Run FIRE Simulation", type="primary", use_container_width=True):
        
        # --- CALCULATION ENGINE ---
        
        # 0. Timeline
        years_to_fire = fire_age - current_age
        years_in_bridge = access_age - fire_age
        
        # 1. Accumulation Phase (Now -> FIRE Age)
        # We need to grow the Current Assets + Contributions
        
        net_nominal_return = return_rate * (1 - (tax_rate * 0.3)) # Assume only yield is taxed annually? 
        # Actually simplest is just a "Net Growth Rate" assumption
        effective_growth_rate = return_rate # Let's stick to raw return for growth, and maybe deduct tax from income?
        # Standard approach:
        # User input "Return" is usually pre-tax.
        # Let's apply a simple tax drag factor of 15% on the return (mix of yield/growth).
        effective_return = return_rate * 0.85 
        
        # Project Year by Year
        projection_data = []
        
        balance = current_investable
        age = current_age
        
        # Store for Chart
        ages = []
        balances = []
        needs = []
        phase = [] # 'Accumulation', 'Drawdown', 'Super Access'
        
        # A. Accumulation Loop
        for i in range(years_to_fire):
            # Growth
            balance = balance * (1 + effective_return)
            # Contribution
            balance += (monthly_savings * 12)
            
            # Record
            ages.append(age)
            balances.append(balance)
            needs.append(0) # No need in accum calculation visual usually, or show target?
            phase.append("Accumulation")
            
            age += 1
            
        fire_starting_balance = balance
        
        # B. Drawdown Loop (FIRE Age -> 60)
        # Expense needs to inflate?
        # Yes, if we are using nominal returns, we must inflate the expense.
        
        current_annual_spend = annual_spend * ((1 + inflation_rate) ** years_to_fire)
        
        success = True
        depletion_age = -1
        
        if years_in_bridge > 0:
            for i in range(years_in_bridge):
                # Start of year balance
                start_bal = balance
                
                # Growth (assume mid-year spend? or beginning. Let's do beginning for safety)
                balance -= current_annual_spend
                
                # Check absolute failure
                if balance < 0:
                    balance = 0
                    if success: 
                        success = False
                        depletion_age = age
                
                # Remainder grows
                balance = balance * (1 + effective_return)
                
                # Record
                ages.append(age)
                balances.append(start_bal) # Plotting start of year wealth
                needs.append(current_annual_spend)
                phase.append("Drawdown (Bridge)")
                
                # Inflate spend for next year
                current_annual_spend *= (1 + inflation_rate)
                age += 1
                
        # C. Post-60 (Legacy / Super Integration not modeled here deeply, just showing leftover)
        # Just show a few years post 60 to show if it held up
        for i in range(5):
            ages.append(age)
            balances.append(balance)
            needs.append(current_annual_spend)
            phase.append("Post-Super Access")
            age += 1
           
        
        # --- RESULTS ---
        st.divider()
        st.markdown("## 📊 Simulation Results")
        
        r1, r2, r3 = st.columns(3)
        
        r1.metric("Projected Wealth at FIRE", f"${fire_starting_balance:,.0f}")
        
        bridge_cost_nominal = sum(needs) # Rough sum of nominal dollars spent
        # Better metric: Did we make it?
        
        if success:
            r2.success("✅ **Bridge Successful**")
            r3.metric("Surplus at Age 60", f"${balances[len(ages)-5]:,.0f}", help="Remaining outside-super wealth to add to your Super")
        else:
            r2.error(f"❌ **Funds Depleted at Age {depletion_age}**")
            r3.metric("Shortfall Age", f"{depletion_age}")
            
        # Chart
        fig = go.Figure()
        
        # Wealth Line
        fig.add_trace(go.Scatter(
            x=ages, y=balances,
            name="Investable Assets",
            mode='lines',
            fill='tozeroy',
            line=dict(color='#C5A059', width=3)
        ))
        
        # Critical Zone (Bridge Phase)
        # Highlight the years where Age >= fire_age and Age < 60
        # We can add a shape
        
        fig.update_layout(
            title="FIRE Bridge Trajectory",
            xaxis_title="Age",
            yaxis_title="Wealth ($)",
            height=400,
            hovermode="x unified"
        )
        
        # Add 'Bridge Phase' shading
        if years_in_bridge > 0:
            fig.add_vrect(
                x0=fire_age, x1=60, 
                annotation_text="Bridge Phase", annotation_position="top left",
                fillcolor="#1A2B3C", opacity=0.1, line_width=0
            )

        st.plotly_chart(fig, use_container_width=True)
        
        # Analysis Text
        if not success:
            st.warning(f"""
            ⚠️ **Bridge Gap Detected:** 
            Your outside-super assets are projected to run out at **Age {depletion_age}**, {60 - depletion_age} years before you can access Super.
            
            **Sugestions:**
            1.  Increase Monthly Savings
            2.  Delay FIRE Age (reduce the bridge length)
            3.  Reduce Target Spend
            """)
        else:
            st.success(f"""
            🎉 **You have a robust bridge!** 
            Your strategy projects enough capital to sustain your lifestyle from Age {fire_age} to 60. 
            At Age 60, you still have **${balances[len(ages)-5]:,.0f}** remaining to top up your Super.
            """)

        # --- Shortfall / Gap Analysis (Required vs Projected) ---
        # Calculate Required Capital at FIRE Age (PV of Bridge Spending)
        # Formula: Sum of Geometric Series for N periods
        # Spend starts at S_0, grows by g (inflation). Discounted by r (return).
        # PV = Sum( S_0 * ((1+g)/(1+r))^t ) for t=0 to N-1
        
        req_start_spend = annual_spend * ((1 + inflation_rate) ** years_to_fire)
        
        if years_in_bridge > 0:
            if abs(effective_return - inflation_rate) < 0.001:
                # Growth equals inflation roughly
                required_capital = req_start_spend * years_in_bridge
            else:
                ratio = (1 + inflation_rate) / (1 + effective_return)
                required_capital = req_start_spend * (1 - ratio ** years_in_bridge) / (1 - ratio)
        else:
            required_capital = 0

        # Disclaimer / Rounding
        # st.write(f"Debug: Req {required_capital}, Proj {fire_starting_balance}")

        st.markdown("### 🎯 Target Analysis")
        
        gap = required_capital - fire_starting_balance
        
        col_target_1, col_target_2, col_target_3 = st.columns(3)
        col_target_1.metric(
            label=f"Required Wealth at Age {fire_age}", 
            value=f"${required_capital:,.0f}",
            help=f"Capital needed at age {fire_age} to fund {years_in_bridge} years of spending until age 60, assuming {inflation_rate*100:.1f}% inflation and {effective_return*100:.1f}% return."
        )
        col_target_2.metric(
            label="Projected Wealth", 
            value=f"${fire_starting_balance:,.0f}"
        )
        
        if gap > 0:
             col_target_3.metric(
                label="Gap (Shortfall)", 
                value=f"${gap:,.0f}", 
                delta="Below Target", 
                delta_color="inverse"
            )
             st.info(f"💡 To bridge the **${gap:,.0f}** gap, you need to accumulate more by Age {fire_age}. Consider increasing savings, improving returns, or delaying retirement.")
        else:
             col_target_3.metric(
                label="Surplus", 
                value=f"${-gap:,.0f}", 
                delta="Above Target", 
                delta_color="normal"
            )
            
        render_footer_disclaimer()

