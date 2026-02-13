import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.tax import calculate_income_tax, calculate_marginal_rate, calculate_stamp_duty, calculate_lmi, calculate_land_tax
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer, get_projection_disclaimer
from utils.leads import render_lead_capture_form

def render_tier2():
    st.markdown("### 🎯 Tier 2: Direction (Strategy)")
    st.markdown("""
    **"Where should I go?"**
    
    Compare the mathematical projections of using home equity for a share portfolio vs buying an investment property.
    This gives you clear **financial direction**.
    
    ✅ **Tax-Deductible Interest** on investment loans  
    ✅ **No Stamp Duty, LMI, or Maintenance** for shares  
    ✅ **Liquidity** - shares vs property  
    ✅ **Diversification** - market exposure differences
    
    See the modeled numbers below 👇
    """)
    
    # Load shared profile
    profile = st.session_state.user_profile

    with st.container():
        # --- Section 1: Personal Profile ---
        st.markdown("#### 1. Personal Profile")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            age = st.number_input("Age", value=profile.get('age', 35), step=1)
            state = st.selectbox("State (Properties)", ["NSW", "VIC", "QLD", "WA", "SA"], index=["NSW", "VIC", "QLD", "WA", "SA"].index(profile.get('state', "NSW")))
        with col_p2:
            income_user = parse_currency_input("Your Annual Income ($)", profile.get('income', 120000))
            partner_income = parse_currency_input("Partner Income ($)", profile.get('partner_income', 0), help_text="Leave 0 if single")
        with col_p3:
            dependants = st.number_input("Dependents", value=profile.get('dependants', 0), step=1)
            
        total_income = income_user + partner_income
        marginal_tax_rate = calculate_marginal_rate(total_income)
        st.caption(f"ℹ️ Combined Household Income: **${total_income:,.0f}** | Est. Marginal Tax Rate: **{marginal_tax_rate:.1%}**")
    
        # --- Section 2: Current Position ---
        st.markdown("#### 2. Your Home (The Engine)")
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            home_value = parse_currency_input("Current Home Value ($)", profile.get('home_value', 1000000))
        with col_h2:
            home_loan = parse_currency_input("Current Home Loan ($)", profile.get('mortgage', 600000))
        with col_h3:
            loan_rate = st.number_input("Mortgage Rate (%)", value=6.10, step=0.05) / 100
            
        equity = home_value - home_loan
        usable_equity = (home_value * 0.80) - home_loan
        
        # visual feedback for equity
        if usable_equity > 50000:
            st.success(f"✅ **Usable Equity:** ${usable_equity:,.0f} (calculated at 80% LVR)")
        else:
            st.warning(f"⚠️ **Usable Equity:** ${max(0, usable_equity):,.0f} (You may need LMI to access more)")
    
        # --- Section 3: Strategy Comparison ---
        st.markdown("#### 3. Strategy Configuration")
        
        # Define defaults
        DEFAULT_ASSET_VALUE = 650000
        
        # Detailed Market Data (10y Averages)
        PROPERTY_MARKET_DATA = {
            "NSW": {"growth": 5.8, "yield": 2.0, "name": "New South Wales"},
            "VIC": {"growth": 4.5, "yield": 1.3, "name": "Victoria"},
            "QLD": {"growth": 7.5, "yield": 2.3, "name": "Queensland"},
            "WA":  {"growth": 5.5, "yield": 2.0, "name": "Western Australia"},
            "SA":  {"growth": 6.5, "yield": 2.0, "name": "South Australia"},
            "TAS": {"growth": 7.5, "yield": 2.0, "name": "Tasmania"},
            "ACT": {"growth": 5.5, "yield": 1.0, "name": "Australian Capital Territory"},
            "NT":  {"growth": 0.5, "yield": 1.0, "name": "Northern Territory"}
        }
        
        col_strat1, col_strat2 = st.columns(2)
        
        # -- Strategy A: Shares --
        with col_strat1:
            st.info("📊 **Strategy A: Debt-Funded Share Portfolio**")
            # Default to same as property for like-for-like comparison
            dr_amount = parse_currency_input("Investment Amount ($)", DEFAULT_ASSET_VALUE, help_text="Defaults to match property value for fair comparison")
            
            st.markdown("**Portfolio Assumptions (Diversified 70/30):**")
            dr_growth = st.slider("Expected Growth (%)", 4.0, 12.0, 8.5, 0.1, key="dr_growth", help="Source: ASX Long Term Investing Report (~8.5-9% 10y avg for Aus Shares).") / 100
            dr_yield = st.slider("Dividend Yield (%)", 1.0, 8.0, 2.5, 0.1, key="dr_yield", help="Source: RBA Bulletin. Typical yield ex-franking for Aus market.") / 100
            
            st.caption("ℹ️ **Franking Bias:** Assumes 30% allocation to Aussie companies paying fully franked dividends (30% tax credit).")

        # -- Strategy B: Property --
        with col_strat2:
            # Get current state from session state (or default) for the title
            current_state = st.session_state.get("tier2_ip_state", "NSW")
            st.warning(f"🏠 **Strategy B: Investment Property ({current_state})**")
            
            ip_state = st.selectbox("Investment Property State", list(PROPERTY_MARKET_DATA.keys()), index=0, key="tier2_ip_state")
            ip_price = parse_currency_input("Purchase Price ($)", DEFAULT_ASSET_VALUE)
            
            # Get specific defaults
            market_data = PROPERTY_MARKET_DATA[ip_state]
            
            st.markdown(f"**Assumptions ({ip_state} 10y Avg):**")
            st.caption(f"ℹ️ Applying {ip_state} market data: **Growth {market_data['growth']}%**, **Yield {market_data['yield']}%**")
            ip_growth = st.slider("Property Growth (%)", 0.0, 10.0, float(market_data['growth']), 0.1, key=f"ip_growth_{ip_state}", help=f"Source: CoreLogic Hedonic Home Value Index (10y annualized growth for {ip_state}).") / 100
            ip_yield = st.slider("Rental Yield (%)", 0.5, 7.0, float(market_data['yield']), 0.1, key=f"ip_yield_{ip_state}", help=f"Source: SQM Research / CoreLogic (Gross rental yield estimate for {ip_state}).") / 100
        
            
        st.markdown("#### 4. Loan Settings")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
             loan_type = st.radio("Loan Repayment Type", ["Interest Only", "Principal & Interest"], horizontal=True)
        with c_l2:
             loan_term = st.selectbox("Loan Term", [30, 25, 20], index=0)
    
        # --- Section 5: Advanced Settings (Collapsed) ---
        with st.expander("⚙️ Fine-Tune: Expenses, Inflation & Holding Costs"):
            c_a1, c_a2, c_a3 = st.columns(3)
            with c_a1:
                st.markdown("**Property Expenses**")
                maint_rate = st.number_input("Maintenance (% of Value)", value=1.0, step=0.1, help="Industry rule of thumb: 1% of property value p.a.") / 100
                mgmt_rate = st.number_input("Mgmt Fee (% of Rent)", value=7.0, step=0.5, help="Typical agency management rate.") / 100
            with c_a2:
                st.markdown("**Fixed Costs**")
                rates = parse_currency_input("Rates & Insurance ($/yr)", 2500, help_text="Council rates, water, and building insurance.")
            with c_a3:
                st.markdown("**Economic**")
                inflation = st.number_input("Inflation Rate (%)", value=3.0, help="Source: RBA Inflation Target Band (2-3%).") / 100
                
        st.divider()
        
        # --- Lead Capture (The Gate) ---
        col_cta1, col_cta2 = st.columns([2, 1])
        with col_cta1:
            st.write("") # spacing
        with col_cta2:
             # Use session state to track if we should show results
             # This enables "Real-Time" updates. Once clicked, it stays active.
             if st.button("🚀 Calculate Projection", type="primary", use_container_width=True):
                 st.session_state['tier2_submitted'] = True

    # Check session state var instead of just button return
    if st.session_state.get('tier2_submitted', False):
        # 1. Update Lead Data & Shared Profile
        st.session_state.user_profile.update({
            "age": age,
            "state": state,
            "income": income_user,
            "partner_income": partner_income,
            "dependants": dependants,
            "home_value": home_value,
            "mortgage": home_loan
        })

        if 'lead_data' in st.session_state:
            st.session_state.lead_data.update({
                "age": age,
                "state": state,
                "target_investment_state": ip_state,
                "income": total_income,
                "dependents": dependants, # standardizing on 'dependents' for lead_data might be needed if that's what it expects, checking lead_data struct
                "loan_type": loan_type
            })

        # 2. Calculate Costs (Use IP State)
        stamp_duty = calculate_stamp_duty(ip_state, ip_price)
        
        # Loan Calcs
        total_ip_loan = ip_price + stamp_duty + 2000 # 2k legal
        lvr_ip = total_ip_loan / ip_price
        lmi = calculate_lmi(total_ip_loan, ip_price) if lvr_ip > 0.8 else 0
        total_ip_cost = total_ip_loan + lmi
        
        # 3. Run Projections with P&I Logic
        dr_results = calculate_dr_projection(dr_amount, dr_growth, dr_yield, loan_rate, marginal_tax_rate, loan_type, loan_term)
        # Pass ip_state for Land Tax
        ip_results = calculate_ip_projection(ip_price, total_ip_cost, ip_growth, ip_yield, loan_rate, marginal_tax_rate, 
                                             maint_rate, mgmt_rate, rates, ip_state, loan_type, loan_term)
        
        # Store in session state
        st.session_state['tier2_results'] = {
            'dr_results': dr_results,
            'ip_results': ip_results,
            'stamp_duty': stamp_duty,
            'lmi': lmi
        }

    # Display Results if present
    if 'tier2_results' in st.session_state:
        results = st.session_state['tier2_results']
        dr_results = results['dr_results']
        ip_results = results['ip_results']
        stamp_duty = results['stamp_duty']
        lmi = results['lmi']
        
        # 4. Results Display (Tabbed)
        st.markdown("## 📊 Analysis Results")
        
        with st.expander("ℹ️ Assumptions & Methodology", expanded=False):
            st.markdown(f"""
            **How these projections are calculated:**
            *   **Property Growth:** Based on 10-year average data for **{ip_state}** (Source: CoreLogic/REIA historical datasets).
            *   **Tax Rates:** 2024-25 Resident Tax Rates + 2% Medicare Levy.
            *   **Loan Costs:** Interest calculations assume a constant rate of **{loan_rate*100:.2f}%** over the selected term.
            *   **Inflation:** All future values are nominal (not inflation-adjusted) unless specified.
            *   **Rental Yield:** Gross yield estimate derived from state averages; actual yields vary by suburb and property type.
            """)
        
        tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "📋 Yearly Breakdown", "💰 Cashflow Analysis"])
        
        with tab1:
            # KPIS
            k1, k2, k3 = st.columns(3)
            # k1.metric("Est. Upfront Costs (IP)", f"${stamp_duty + lmi:,.0f}", help=f"Stamp Duty: ${stamp_duty:,.0f}, LMI: ${lmi:,.0f}")
            
            dr_final = dr_results['net_wealth'][-1]
            ip_final = ip_results['net_wealth'][-1]
            
            # Show Loan Balance remaining in metric help or delta?
            dr_loan_rem = dr_results['loan_balance'][-1]
            ip_loan_rem = ip_results['loan_balance'][-1]
            
            # Year 1 Tax Impact
            ip_tax_y1 = ip_results['tax_saved_yearly'][0]
            k3.metric("Year 1 Tax Benefit (Property)", f"${ip_tax_y1:,.0f}", help="Positive means tax refund/saving. Negative means tax payable.")

            # Inflation Toggle
            st.markdown("---")
            col_chart_header, col_toggle = st.columns([3, 1])
            with col_chart_header:
                 st.markdown("### 📈 Wealth Projection")
            with col_toggle:
                 show_real = st.toggle("Show in Today's Dollars", value=False, help="Adjusts future values for inflation (2.5% p.a.) to show purchasing power in today's terms.")
            
            # Adjustment Logic
            years = list(range(1, 11))
            inflation_rate = 0.025 if show_real else 0.0
            
            dr_wealth_display = []
            ip_wealth_display = []
            
            for i, (dr_val, ip_val) in enumerate(zip(dr_results['net_wealth'], ip_results['net_wealth'])):
                factor = (1 + inflation_rate) ** (i + 1)
                dr_wealth_display.append(dr_val / factor)
                ip_wealth_display.append(ip_val / factor)
                
            # Update Metrics with Final Adjusted Values
            k1.metric("Option A: Shares Net Wealth (10y)", f"${dr_wealth_display[-1]:,.0f}", delta=f"Loan Rem: ${dr_results['loan_balance'][-1]:,.0f}")
            k2.metric("Option B: Property Net Wealth (10y)", f"${ip_wealth_display[-1]:,.0f}", delta=f"Loan Rem: ${ip_results['loan_balance'][-1]:,.0f}", delta_color="normal")

            # Chart
            fig_wealth = go.Figure()
            # Gold for Shares (Growth/Opportunity)
            fig_wealth.add_trace(go.Scatter(x=years, y=dr_wealth_display, name="Debt Recycling (Shares)", 
                                    line={'color': '#C5A059', 'width': 4}, mode='lines+markers'))
            # Navy for Property (Stability/Foundation)
            fig_wealth.add_trace(go.Scatter(x=years, y=ip_wealth_display, name="Investment Property", 
                                    line={'color': '#002B5C', 'width': 4}, mode='lines+markers'))
                                    
            fig_wealth.update_layout(
                title="Projected Net Wealth Accumulation",
                xaxis_title="Years",
                yaxis_title="Net Wealth ($)",
                legend={'yanchor': "top", 'y': 0.99, 'xanchor': "left", 'x': 0.01},
                hovermode="x unified",
                height=400
            )
            st.plotly_chart(fig_wealth, use_container_width=True)
            st.caption(get_projection_disclaimer())
            
            # New Tax Comparison Chart
            st.markdown("### 💸 Annual Tax Impact Comparison")
            fig_tax = go.Figure()
            fig_tax.add_trace(go.Bar(x=years, y=dr_results['tax_saved_yearly'], name="Shares Tax Benefit", marker_color='#C5A059'))
            fig_tax.add_trace(go.Bar(x=years, y=ip_results['tax_saved_yearly'], name="Property Tax Benefit", marker_color='#002B5C'))
            fig_tax.update_layout(
                title="Annual Tax Savings (Negative Gearing Benefit)",
                xaxis_title="Year",
                yaxis_title="Tax Saved ($)",
                barmode='group',
                height=350
            )
            st.plotly_chart(fig_tax, use_container_width=True)
            
            with st.expander("💡 Why does the Property Tax Benefit increase over time?"):
                st.markdown("""
                You might notice the **Property Tax Benefit** stays high or increases, while the **Shares Benefit** declines. Here's why:
                
                1.  **Shares become "Self-Sustaining":**
                    *   Your dividend income grows, but your costs (Interest Only loan) stay flat.
                    *   The gap shrinks, meaning you lose less money each year and rely less on tax breaks. This is a **good thing**!
                
                2.  **Property Costs Scale with Value:**
                    *   While rent grows, so do your **Maintenance**, **Management Fees**, and **Land Tax**.
                    *   These rising costs often outpace rental growth, keeping you "negatively geared" (losing money) for longer.
                """)
            
            # Recommendation Logic (Basic)
            dr_final_adj = dr_wealth_display[-1]
            ip_final_adj = ip_wealth_display[-1]
            
            diff = abs(dr_final_adj - ip_final_adj)
            higher_scenario = "Property Scenario" if ip_final_adj > dr_final_adj else "Share Scenario"
            
            val_type = "Real (Today's)" if show_real else "Nominal"
            
            if higher_scenario == "Share Scenario":
                st.success(f"""
                💡 **Scenario Analysis:** The **Share Portfolio model** projects a result **\${diff:,.0f} higher** over 10 years ({val_type} Value).
                
                **Key Drivers in this Model:** 
                - Interest deductibility
                - Tax flexibility (CGT management)
                - Liquidity differences
                - Absence of stamp duty (**\${stamp_duty:,.0f}**) and ongoing property costs
                """)
            else:
                st.info(f"💡 **Scenario Analysis:** The **Property model** projects a result **\${diff:,.0f} higher** over 10 years ({val_type} Value). Consider also liquidity and tax flexibility.")

        with tab2:
            # GATED CONTENT
            if 'lead_data' in st.session_state and st.session_state.lead_data.get('email'):
                st.markdown("#### Year-by-Year Net Wealth")
                df = pd.DataFrame({
                    "Year": range(1, 11),
                    "Shares (Net Wealth)": [f"${x:,.0f}" for x in dr_results['net_wealth']],
                    "Property (Net Wealth)": [f"${x:,.0f}" for x in ip_results['net_wealth']],
                    "Shares (Annual Tax)": [f"${x:,.0f}" for x in dr_results['tax_saved_yearly']],
                    "Property (Annual Tax)": [f"${x:,.0f}" for x in ip_results['tax_saved_yearly']]
                })
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("🔒 **Detailed Breakdown Locked**")
                if render_lead_capture_form("tier2_tab2", button_label="Unlock Breakdown"):
                    st.rerun()
            
        with tab3:
            st.info("🚧 Cashflow Dashboard enables detailed income vs expense tracking.")
            
            # Simple Cashflow Table for now
            cf_df = pd.DataFrame({
                "Metric": ["Estimated Tax Saved (Cumulative)", "Net Equity Gain (10y)"],
                "Shares": [f"${dr_results.get('tax_saved', [0]*10)[-1]:,.0f}", f"${dr_final - dr_results['net_wealth'][0]:,.0f}"],
                "Property": [f"${ip_results.get('tax_saved', [0]*10)[-1]:,.0f}", f"${ip_final - ip_results['net_wealth'][0]:,.0f}"]
            })
            st.table(cf_df)
    
        # Disclaimer Footer
        render_footer_disclaimer()
    
        # PDF Generation (Gated)
        st.divider()
        if 'lead_data' in st.session_state and st.session_state.lead_data.get('email'):
             from utils.pdf_gen import generate_pdf_report
             
             # Capture Chart Image
             chart_img = None
             try:
                 # Ensure we have the figure to export
                 if 'fig_wealth' in locals():
                     chart_img = fig_wealth.to_image(format="png")
             except Exception as e:
                 st.error(f"Could not export chart for PDF: {e}")
                 
             pdf = generate_pdf_report(
                 st.session_state.lead_data, 
                 dr_results, 
                 ip_results, 
                 chart_image=chart_img
             )
             
             c1, c2, c3 = st.columns([1,2,1])
             with c2:
                 st.download_button(
                     "📄 Download Professional Wealth Report (PDF)", 
                     pdf, 
                     "Wealth_Strategy_Report.pdf", 
                     "application/pdf",
                     type="primary",
                     use_container_width=True
                 )
        else:
             st.markdown("### 📄 Want a Professional PDF Report?")
             if render_lead_capture_form("tier2_pdf", button_label="Generate PDF Report"):
                 st.rerun()
        
import numpy_financial as npf

def calculate_dr_projection(amount, growth, yield_rate, interest_rate, tax_rate, loan_type="Interest Only", loan_term=30, years=10, franking_allocation=0.30, company_tax_rate=0.30):
    net_wealth = []
    tax_saved_cum = []
    tax_saved_yearly = []
    loan_balances = []
    
    current_val = amount
    loan = amount
    total_tax_saved = 0
    
    # Yearly Repayment if P&I
    yearly_payment = 0
    if loan_type == "Principal & Interest":
        # Standard amortization formula
        if interest_rate > 0:
            yearly_payment = (loan * interest_rate * (1 + interest_rate)**loan_term) / ((1 + interest_rate)**loan_term - 1)
        else:
            yearly_payment = loan / loan_term
            
    for i in range(years):
        # Growth
        current_val *= (1 + growth)
        
        # Interest & Principal
        if loan_type == "Interest Only":
            interest = loan * interest_rate
            principal_paid = 0
        else:
            interest = loan * interest_rate
            # Ensure we don't overpay the last bit
            principal_paid = yearly_payment - interest
            if principal_paid > loan:
                principal_paid = loan
                interest = 0 # simplified end of loan
            
        # Cashflow
        cash_dividends = current_val * yield_rate
        
        # Franking Credit Logic
        # Apply allocation (e.g. 30% of portfolio is Aussie shares paying fully franked dividends)
        franked_portion = cash_dividends * franking_allocation
        unfranked_portion = cash_dividends * (1 - franking_allocation)
        
        # Gross up limits
        franking_credits = (franked_portion / (1 - company_tax_rate)) * company_tax_rate
        gross_income = cash_dividends + franking_credits
        
        # Taxable Income = Gross Income - Deductions (Interest)
        taxable_income = gross_income - interest
        
        # Tax Liability (Negative means tax loss/refund)
        tax_liability = taxable_income * tax_rate
        
        # Net Tax Position = Tax Liability - Franking Credits (Offsets)
        # If Liability is negative (Refund), we add credits to refund (credits are refundable)
        # If Liability is positive (Payable), credits reduce it.
        # Actually: Tax Payable = (Taxable Income * Rate) - Offsets
        # If Result < 0, it's a refund.
        
        net_tax_payable = tax_liability - franking_credits
        
        # We display "Tax Saved" (Benefit). 
        # If net_tax_payable is negative (Refund), Benefit is positive.
        # If net_tax_payable is positive (Payable), Benefit is negative.
        current_tax_saving = -net_tax_payable
        
        total_tax_saved += current_tax_saving

        tax_saved_cum.append(total_tax_saved)
        tax_saved_yearly.append(current_tax_saving)
        
        # Update Loan
        loan -= principal_paid
        loan_balances.append(loan)
        
        # Net Wealth
        net_equity = current_val - loan
        net_wealth.append(net_equity)
        
    return {"net_wealth": net_wealth, "tax_saved": tax_saved_cum, "tax_saved_yearly": tax_saved_yearly, "loan_balance": loan_balances}

def calculate_ip_projection(price, loan, growth, yield_rate, interest_rate, tax_rate, maint, mgmt, rates, state, loan_type="Interest Only", loan_term=30, years=10):
    net_wealth = []
    tax_saved_cum = []
    tax_saved_yearly = []
    loan_balances = []
    
    current_val = price
    current_loan = loan
    total_tax_saved = 0
    
    # Yearly Repayment if P&I
    yearly_payment = 0
    if loan_type == "Principal & Interest":
        if interest_rate > 0:
            yearly_payment = (current_loan * interest_rate * (1 + interest_rate)**loan_term) / ((1 + interest_rate)**loan_term - 1)
        else:
             yearly_payment = current_loan / loan_term
    
    for i in range(years):
        # Value Growth
        current_val *= (1 + growth)
        
        # Interest & Principal
        if loan_type == "Interest Only":
            interest = current_loan * interest_rate
            principal_paid = 0
        else:
            interest = current_loan * interest_rate
            principal_paid = yearly_payment - interest
            if principal_paid > current_loan:
                principal_paid = current_loan
                interest = 0
        
        # Expenses
        rent = current_val * yield_rate
        maintenance = current_val * maint
        management = rent * mgmt
        # Land Tax
        land_val = current_val * 0.6 
        land_tax = calculate_land_tax(state, land_val)
        
        total_expenses = interest + maintenance + management + rates + land_tax
        net_cash = rent - total_expenses
        
        # Tax Impact
        if net_cash < 0:
            tax_saving = abs(net_cash) * tax_rate
            total_tax_saved += tax_saving
            current_tax_saving = tax_saving
        else:
            current_tax_saving = -(net_cash * tax_rate)
            total_tax_saved += current_tax_saving
            
        tax_saved_cum.append(total_tax_saved)
        tax_saved_yearly.append(current_tax_saving)
        
        # Update Loan
        current_loan -= principal_paid
        loan_balances.append(current_loan)
        
        # Net Equity
        net_equity = current_val - current_loan
        net_wealth.append(net_equity)
        
    render_footer_disclaimer()
        
    return {"net_wealth": net_wealth, "tax_saved": tax_saved_cum, "tax_saved_yearly": tax_saved_yearly, "loan_balance": loan_balances}
