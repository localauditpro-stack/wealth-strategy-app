import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
from utils.ui import parse_currency_input
from utils.compliance import render_footer_disclaimer, get_projection_disclaimer
from utils.leads import render_lead_capture_form

# Load fund fee data
@st.cache_data
def load_fund_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fund_fees.json')
    with open(data_path, 'r') as f:
        return json.load(f)

def render_tier3_super():
    st.title("Tier 3: Acceleration (Superannuation Concepts)")
    
    from utils.compliance import render_general_advice_warning_above_fold, render_data_usage_explanation, render_chart_disclaimer
    render_general_advice_warning_above_fold()
    render_data_usage_explanation()

    st.markdown("""
    **Understanding Superannuation Compounding**
    
    The power of compounding is a fundamental concept in wealth building. This tool allows you to explore how different allocation concepts and contribution levels might model over time.
    """)
    
    # Load fund data
    fund_data = load_fund_data()
    fund_names = sorted(fund_data.keys())
    
    # Fund selector - now reactive!
    st.markdown("#### Your Super Fund")
    
    selected_fund = st.selectbox(
        "Which fund are you with?", 
        fund_names,
        index=fund_names.index("AustralianSuper") if "AustralianSuper" in fund_names else 0,
        help="We'll use your fund's actual fees from their latest PDS"
    )
    
    # Display fund fees (updates immediately when fund changes)
    fund_info = fund_data[selected_fund]
    st.info(f"ℹ️ **Data Source:** Fee data sourced from {selected_fund} Product Disclosure Statement (PDS) for standard accumulation accounts.")
    
    st.caption(f"""
    **{selected_fund} Fees (from latest PDS):**  
    Admin: ${fund_info['admin_fee_flat']}/year + {fund_info['admin_fee_percent']*100:.2f}% (capped at ${fund_info['admin_fee_cap']})  
    Investment (Balanced): {fund_info['investment_fee_balanced']*100:.2f}% | Investment (High Growth): {fund_info['investment_fee_high_growth']*100:.2f}%  
    Transaction: {fund_info['transaction_cost']*100:.2f}%
    
    **Historical Returns (10-year avg):**  
    Balanced: {fund_info['return_balanced_10y']*100:.1f}% | High Growth: {fund_info['return_high_growth_10y']*100:.1f}%
    """)
    
    
    # Get fund's historical returns for defaults
    balanced_default = fund_info['return_balanced_10y'] * 100
    high_growth_default = fund_info['return_high_growth_10y'] * 100
    
    # Debug: Show what defaults we're using
    st.info(f"📊 Using {selected_fund}'s historical returns: Balanced {balanced_default:.2f}%, High Growth {high_growth_default:.2f}%")
    
    # Personal Profile - NO FORM
    st.markdown("#### Your Super Profile")
    
    # Load defaults
    profile = st.session_state.get('user_profile', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        current_age = st.number_input("Current Age", value=profile.get('age', 25), min_value=18, max_value=65, step=1, key="age")
        retirement_age = st.selectbox("Retirement Age", [60, 65, 67], index=1, key="ret_age")
    with col2:
        current_balance = parse_currency_input("Current Super Balance ($)", 30000, key="balance")
        # Use profile income as default salary
        annual_salary = parse_currency_input("Annual Salary ($)", profile.get('income', 75000), key="salary")
    with col3:
        employer_contrib = st.slider("Employer Contribution (%)", 9.5, 15.0, 11.5, 0.5, help="Source: ATO Super Guarantee rate (11.5% for FY2024-25, rising to 12% on 1 July 2025).", key="employer") / 100
        voluntary_contrib = parse_currency_input("Illustrative Voluntary Contributions ($/year)", 0, help_text="Extra amount for modeling (e.g. Salary Sacrifice or Personal Deductible)", key="voluntary")
    
    
    # Investment Options - sliders now update with fund changes!
    st.markdown("#### Investment Options to Compare")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("📊 **High Growth Option**")
        high_growth_return = st.slider(
            "Expected Return (% p.a.)", 
            6.0, 12.0, 
            float(high_growth_default), 
            0.1, 
            key=f"hg_{selected_fund}",  # Key includes fund name so it resets when fund changes
            help=f"Source: {selected_fund} Product Disclosure Statement (10-year avg return for High Growth option)."
        ) / 100
    with col_b:
        st.warning("⚖️ **Balanced Option**")
        balanced_return = st.slider(
            "Expected Return (% p.a.)", 
            4.0, 10.0, 
            float(balanced_default), 
            0.1, 
            key=f"bal_{selected_fund}",  # Key includes fund name so it resets when fund changes
            help=f"Source: {selected_fund} Product Disclosure Statement (10-year avg return for Balanced option)."
        ) / 100
    
    
    with st.expander("⚙️ Advanced: Catch-up & Salary Growth"):
        salary_growth = st.number_input("Salary Growth (% p.a.)", value=3.0, step=0.5, key="sal_growth", help="Source: ABS Wage Price Index (long-term assumption ~3%).") / 100
        
        st.markdown("---")
        st.markdown("#### 🏃‍♂️ Concessional Catch-up")
        use_catchup = st.checkbox("Include Carry-Forward Contributions?", help="Utilize unused concessional cap from previous 5 years")
        
        unused_cap = 0
        if use_catchup:
            unused_cap = parse_currency_input("Unused Concessional Cap Amount ($)", 30000, help_text="Check your ATO Portal (via myGov) for this figure", key="t3_unused_cap")
            st.caption(f"ℹ️ Boosting Year 1 contribution by **${unused_cap:,.0f}**")
    
    # Calculate button
    if st.button("🚀 Model Super Scenarios", type="primary", use_container_width=True):
        st.session_state['tier3_submitted'] = True

    if st.session_state.get('tier3_submitted', False):
        years_to_retirement = retirement_age - current_age
        
        # Get fund-specific fees
        fund_info = fund_data[selected_fund]
        
        # Determine Marginal Rate for Tax Benefit Calc (Simple estimate based on income)
        # Using 2024-25 resident tax rates
        income = annual_salary
        if income > 190000:
            marginal_rate = 0.45
        elif income > 135000:
            marginal_rate = 0.37
        elif income > 45000:
            marginal_rate = 0.30
        else:
            marginal_rate = 0.19
            
        # Medicare levy
        marginal_rate += 0.02 
        
        # Calculate projections with fund-specific fees
        hg_projection = calculate_super_projection(
            current_balance, annual_salary, employer_contrib, voluntary_contrib,
            high_growth_return, fund_info['investment_fee_high_growth'], 
            fund_info['admin_fee_flat'], fund_info['admin_fee_percent'], 
            fund_info['admin_fee_cap'], fund_info['transaction_cost'],
            salary_growth, years_to_retirement, unused_cap, marginal_rate
        )
        
        bal_projection = calculate_super_projection(
            current_balance, annual_salary, employer_contrib, voluntary_contrib,
            balanced_return, fund_info['investment_fee_balanced'], 
            fund_info['admin_fee_flat'], fund_info['admin_fee_percent'], 
            fund_info['admin_fee_cap'], fund_info['transaction_cost'],
            salary_growth, years_to_retirement, unused_cap, marginal_rate
        )
        
        st.session_state['tier3_results'] = {
            'hg_projection': hg_projection,
            'bal_projection': bal_projection,
            'current_age': current_age,
            'retirement_age': retirement_age,
            'selected_fund': selected_fund,
            'current_balance': current_balance,
            'unused_cap': unused_cap,
            'tax_saved_catchup': hg_projection.get('tax_saved_catchup', 0)
        }

    if 'tier3_results' in st.session_state:
        results = st.session_state['tier3_results']
        hg_projection = results['hg_projection']
        bal_projection = results['bal_projection']
        current_age = results['current_age']
        retirement_age = results['retirement_age']
        selected_fund = results['selected_fund']
        current_balance = results['current_balance']

        # Results
        st.markdown("## 📊 Illustrative Super Projections")
        render_chart_disclaimer()
        
        # Inflation Toggle
        col_res_header, col_toggle = st.columns([3, 1])
        with col_res_header:
             st.write("Compare the projected growth of your Super over time.")
        with col_toggle:
             show_real = st.toggle("Show in Today's Dollars", value=False, help="Adjusts future values for inflation (2.5% p.a.) to show for purchasing power parity.")
        
        inflation_rate = 0.025 if show_real else 0.0
        
        tab1, tab2, tab3 = st.tabs(["📈 The Divergence", "🏆 Fund Comparison", "📋 Year-by-Year"])
        
        with tab1:
            # KPIs
            k1, k2, k3 = st.columns(3)
            
            # Adjust Final Balances
            years_elapsed = retirement_age - current_age
            discount_factor = (1 + inflation_rate) ** years_elapsed
            
            hg_final = hg_projection['balance'][-1] / discount_factor
            bal_final = bal_projection['balance'][-1] / discount_factor
            
            difference = hg_final - bal_final
            current_balance_adj = current_balance # Present value is already present value
            
            k1.metric("High Growth Final Balance", f"${hg_final:,.0f}", delta=f"+${hg_final - current_balance_adj:,.0f}")
            k2.metric("Balanced Final Balance", f"${bal_final:,.0f}", delta=f"+${bal_final - current_balance_adj:,.0f}")
            
            tax_saved = results.get('tax_saved_catchup', 0)
            if tax_saved > 0:
                k3.metric("Immediate Tax Benefit", f"${tax_saved:,.0f}", delta="Instant Saving", help="Tax saved by using Catch-up vs taking as income")
            else:
                k3.metric("The Cost of 'Balanced'", f"-${difference:,.0f}", delta_color="inverse", help="What you LOSE by not choosing High Growth")
            
            # Chart 1: Growth Lines
            years = list(range(current_age, retirement_age + 1))
            
            # Prepare Display Data
            hg_display = []
            bal_display = []
            
            for i, (hg, bal) in enumerate(zip(hg_projection['balance'], bal_projection['balance'])):
                factor = (1 + inflation_rate) ** i
                hg_display.append(hg / factor)
                bal_display.append(bal / factor)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=years, 
                y=hg_display, 
                name="High Growth",
                line={'color': '#6366F1', 'width': 4},
                mode='lines',
                fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=years, 
                y=bal_display, 
                name="Balanced",
                line={'color': '#0F172A', 'width': 4, 'dash': 'dash'},
                mode='lines'
            ))
            
            fig.update_layout(
                title=f"Super Balance Growth: Age {current_age} → {retirement_age}",
                xaxis_title="Age",
                yaxis_title="Super Balance ($)",
                hovermode="x unified",
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Chart 2: The Gap (Difference)
            gap_values = [h - b for h, b in zip(hg_display, bal_display)]
            
            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(
                x=years,
                y=gap_values,
                name="The Gap",
                marker_color='#A855F7'
            ))
            fig_gap.update_layout(
                title="The Cost of Waiting: Cumulative Difference Over Time",
                xaxis_title="Age",
                yaxis_title="Difference ($)",
                height=300
            )
            st.plotly_chart(fig_gap, use_container_width=True)
            
            # Insight
            if difference > 100000:
                st.success(f"""
                🎯 **Illustrative Impact:** In this scenario, the High Growth model projects a balance **\${difference:,.0f} higher** compared to the Balanced model.
                
                **Concepts to consider:**
                - How different return targets impact potential retirement lifestyles.
                - How your risk tolerance aligns with various investment options.
                """)
            else:
                st.info(f"💡 Illustrative model shows a \${difference:,.0f} difference between these two scenarios over the projection period.")
        
        with tab2:
            st.markdown("### 🏆 How Does Your Fund Stack Up?")
            st.markdown(f"Comparing **{selected_fund}** against the top 5 performing funds (based on 10-year High Growth returns)")
            
            # Get top 5 funds by high growth returns
            fund_performance = [(name, data['return_high_growth_10y']) for name, data in fund_data.items()]
            fund_performance.sort(key=lambda x: x[1], reverse=True)
            top_5_funds = [f[0] for f in fund_performance[:5]]
            
            # Make sure user's fund is included
            comparison_funds = top_5_funds.copy()
            if selected_fund not in comparison_funds:
                comparison_funds.append(selected_fund)
            
            # Calculate projections for each fund
            fund_projections = {}
            for fund_name in comparison_funds:
                fund = fund_data[fund_name]
                projection = calculate_super_projection(
                    current_balance, annual_salary, employer_contrib, voluntary_contrib,
                    fund['return_high_growth_10y'], fund['investment_fee_high_growth'], 
                    fund['admin_fee_flat'], fund['admin_fee_percent'], 
                    fund['admin_fee_cap'], fund['transaction_cost'],
                    salary_growth, years_to_retirement, unused_cap, 0.32 # Use default rate for comparison
                )
                fund_projections[fund_name] = projection['balance']
            
            # Create comparison chart
            years = list(range(current_age, retirement_age + 1))
            fig2 = go.Figure()
            
            # Color palette
            colors = ['#6366F1', '#10B981', '#A855F7', '#F59E0B', '#3B82F6', '#EF4444']
            
            for idx, (fund_name, balances) in enumerate(fund_projections.items()):
                # Adjust for inflation
                adj_balances = [b / ((1 + inflation_rate) ** i) for i, b in enumerate(balances)]
                
                is_user_fund = (fund_name == selected_fund)
                fig2.add_trace(go.Scatter(
                    x=years,
                    y=adj_balances,
                    name=f"{fund_name} {'(YOUR FUND)' if is_user_fund else ''}",
                    line={
                        'color': colors[idx % len(colors)],
                        'width': 5 if is_user_fund else 2,
                        'dash': 'solid' if is_user_fund else 'dot'
                    },
                    mode='lines'
                ))
            
            fig2.update_layout(
                title=f"Fund Performance Comparison (High Growth Option)",
                xaxis_title="Age",
                yaxis_title="Super Balance ($)",
                hovermode="x unified",
                height=500,
                legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(get_projection_disclaimer())
            
            # Show final balances comparison
            st.markdown("#### Final Balances at Retirement")
            comparison_data = []
            for fund_name in comparison_funds:
                final_balance = fund_projections[fund_name][-1] / discount_factor # Apply same discount
                fund_return = fund_data[fund_name]['return_high_growth_10y'] * 100
                
                # Compare against adjusted user fund
                user_final_adj = fund_projections[selected_fund][-1] / discount_factor
                
                comparison_data.append({
                    'Fund': f"{fund_name} {'⭐ (You)' if fund_name == selected_fund else ''}",
                    'Final Balance': final_balance,
                    '10-Year Return': f"{fund_return:.2f}%",
                    'vs Your Fund': final_balance - user_final_adj
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            df_comparison = df_comparison.sort_values('Final Balance', ascending=False)
            
            st.dataframe(
                df_comparison.style.format({
                    'Final Balance': '${:,.0f}',
                    'vs Your Fund': '${:+,.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Insight
            user_final = fund_projections[selected_fund][-1]
            best_fund = max(fund_projections.items(), key=lambda x: x[1][-1])
            best_fund_name, best_fund_balance = best_fund[0], best_fund[-1][-1]
            
            if selected_fund == best_fund_name:
                st.success(f"🎉 **Historical Comparison:** Your fund ({selected_fund}) has the highest historical returns among those compared over the last 10 years.")
            else:
                difference_to_best = best_fund_balance - user_final
                st.warning(f"""
                ⚠️ **Historical Comparison:** {best_fund_name} has historically outperformed {selected_fund} over the last 10 years. 
                
                Projected difference based on past returns: **${difference_to_best:,.0f}**.
                
                *Past performance is not a reliable indicator of future performance.*
                """)
        
        with tab3:
            # GATED CONTENT
            if 'lead_data' in st.session_state and st.session_state.lead_data.get('email'):
                st.markdown("#### Detailed Projection")
                
                df = pd.DataFrame({
                    'Age': years,
                    'High Growth Balance': hg_projection['balance'],
                    'Balanced Balance': bal_projection['balance'],
                    'Gap': [hg - bal for hg, bal in zip(hg_projection['balance'], bal_projection['balance'])]
                })
                
                st.dataframe(
                    df.style.format({
                        'High Growth Balance': '${:,.0f}',
                        'Balanced Balance': '${:,.0f}',
                        'Gap': '${:,.0f}'
                    }),
                    use_container_width=True
                )
            else:
                 st.info("🔒 **Detailed Projection Locked**")
                 if render_lead_capture_form("tier3_tab3", button_label="Unlock Detailed View"):
                     st.rerun()
            
        # Disclaimer Footer
        render_footer_disclaimer()

        # PDF Generation (if data exists)
        st.divider()
        if 'lead_data' in st.session_state and st.session_state.lead_data.get('email'):
             # PDF logic would go here
             st.info("📄 PDF Report generation for Super is coming soon.")
        else:
             st.markdown("### 📄 Want a Professional PDF Report?")
             if render_lead_capture_form("tier3_pdf", button_label="Generate PDF Report"):
                 st.rerun()

def calculate_super_projection(balance, salary, employer_rate, voluntary, return_rate, 
                               investment_fee_rate, admin_fee_flat, admin_fee_percent, 
                               admin_fee_cap, transaction_cost, salary_growth, years, 
                               unused_cap=0, marginal_rate=0.32):
    """
    Calculate super balance projection with compounding and fund-specific fees
    """
    balances = [balance]
    current_salary = salary
    
    # Calculate tax efficacy of catch-up
    # Catch-up contributions are taxed at 15% in fund, vs marginal_rate outside
    # Saving = Amt * (Marginal - 0.15)
    tax_saved_catchup = 0
    if unused_cap > 0:
        tax_saved_catchup = unused_cap * (marginal_rate - 0.15)
    
    for year in range(years):
        # Contributions
        employer_contrib = current_salary * employer_rate
        total_contrib = employer_contrib + voluntary
        
        # Apply catch-up in Year 1 (index 0 loop)
        if year == 0 and unused_cap > 0:
            total_contrib += unused_cap
        
        # Contributions Tax (15%)
        # Note: We haven't deducted 15% tax from contributions in previous simpler version?
        # Let's check logic. Typically input is Gross Salary. SG is pre-tax.
        # It's safer to assume the "Employer Contribution" % is the gross amount going in, 
        # and we strip 15% tax upon entry.
        # NOTE: Previous code did `balance + total_contrib`. It missed the 15% contributions tax?
        # Let's add it for accuracy, or keep consistent if we were simplifying.
        # User asked for "Tax Benefit", so we SHOULD model tax.
        
        contrib_tax = total_contrib * 0.15
        net_contrib = total_contrib - contrib_tax
        
        # Admin fees (flat + percentage, capped)
        admin_percent_fee = balance * admin_fee_percent
        admin_total = min(admin_fee_flat + admin_percent_fee, admin_fee_cap)
        
        # Investment return (on opening balance + half of contributions)
        avg_balance = balance + (net_contrib / 2)
        gross_return = avg_balance * return_rate
        
        # Investment fees
        investment_fees = balance * investment_fee_rate
        
        # Transaction costs
        transaction_fees = balance * transaction_cost
        
        # Net return after fees
        net_return = gross_return - investment_fees - transaction_fees
        
        # New balance
        balance = balance + net_contrib + net_return - admin_total
        balances.append(balance)
        
        # Salary growth
        current_salary *= (1 + salary_growth)
    
    
    return {'balance': balances, 'tax_saved_catchup': tax_saved_catchup}

    render_footer_disclaimer()
