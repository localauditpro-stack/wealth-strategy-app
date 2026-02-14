import streamlit as st
import plotly.graph_objects as go


from utils.ui import parse_currency_input, go_to_page
from utils.compliance import render_footer_disclaimer, get_projection_disclaimer
from utils.leads import render_lead_capture_form

def render_tier1():
    """Renders the enhanced Tier 1 'Financial Readiness Assessment' calculator."""
    st.markdown("### 🔍 Tier 1: Clarity (Readiness)")
    st.markdown("""
    **"Am I ready for this?"**
    
    Before building a skyscraper, you need a solid foundation. 
    This tool assesses your **financial clarity** and readiness for advanced wealth strategies.
    """)
    
    st.markdown("#### Your Financial Profile")
    
    col1, col2, col3 = st.columns(3)
    
    # Load defaults from session state
    profile = st.session_state.user_profile

    with col1:
        age = st.number_input(
            "👤 Age",
            min_value=18,
            max_value=80,
            value=profile.get('age', 35),
            step=1,
            format="%d",
            help="Your current age"
        )
        
        # Split Equity into Value and Loan for better downstream data
        home_value = parse_currency_input(
            "🏠 Home Value ($)", 
            profile.get('home_value', 1000000), 
            "Current market value of your home",
            key="t1_home_value"
        )
        mortgage = parse_currency_input(
            "🏦 Mortgage Balance ($)", 
            profile.get('mortgage', 600000), 
            "Remaining loan on your home",
            key="t1_mortgage"
        )
        
        equity = home_value - mortgage
        
    with col2:
        marital_status = st.selectbox(
            "💑 Marital Status",
            ["Single", "Married/De facto", "Divorced", "Widowed"],
            index=["Single", "Married/De facto", "Divorced", "Widowed"].index(profile.get('marital_status', "Married/De facto")),
            help="Your current relationship status"
        )
        # Income Logic
        if marital_status == "Married/De facto":
            col_inc_a, col_inc_b = st.columns(2)
            with col_inc_a:
                user_income = parse_currency_input(
                    "Your Income ($)", 
                    profile.get('user_income', 90000), 
                    "Your individual pre-tax income",
                    key="t1_user_income_sp"
                )
            with col_inc_b:
                partner_income = parse_currency_input(
                    "Partner Income ($)", 
                    profile.get('partner_income', 60000), 
                    "Partner's individual pre-tax income",
                    key="t1_partner_income"
                )
            income = user_income + partner_income
            st.caption(f"**Total Household Income:** ${income:,.0f}")
        else:
            user_income = parse_currency_input(
                "Annual Income ($)", 
                profile.get('user_income', profile.get('income', 120000)), 
                "Your pre-tax income",
                key="t1_user_income"
            )
            partner_income = 0
            income = user_income
        state = st.selectbox(
            "📍 State",
            ["NSW", "VIC", "QLD", "WA", "SA"],
            index=["NSW", "VIC", "QLD", "WA", "SA"].index(profile.get('state', "NSW")),
            help="Your state of residence"
        )
        
    with col3:
        dependants = st.number_input(
            "👨‍👩‍👧‍👦 Number of Dependants",
            min_value=0,
            max_value=10,
            value=profile.get('dependants', 0),
            step=1,
            help="Children or other financial dependants"
        )
        experience = st.selectbox(
            "📊 Investment Experience", 
            ["Beginner (Cash/Term Deposits)", 
             "Intermediate (Some Shares/Property)", 
             "Advanced (Active Portfolio/SMSF)"],
            index=["Beginner (Cash/Term Deposits)", "Intermediate (Some Shares/Property)", "Advanced (Active Portfolio/SMSF)"].index(profile.get('experience', "Intermediate (Some Shares/Property)")),
            help="Your current level of investment knowledge and activity"
        )
    
    st.markdown("**Risk Tolerance**")
    risk_options = [
        "Conservative", 
        "Moderately Conservative", 
        "Balanced", 
        "Moderate Growth", 
        "High Growth"
    ]
    
    risk_descriptions = {
        "Conservative": "Prioritizes capital preservation above all else, typically investing in fixed-income securities, bonds, and cash equivalents to avoid volatility. (20% Growth, 80% Defensive)",
        "Moderately Conservative": "Seeks slightly higher returns than a conservative portfolio but still prioritizes safety. Usually holds a high percentage of bonds with a small allocation to equities. (50% Growth, 50% Defensive)",
        "Balanced": "Aims for a balance between growth and income, often holding a roughly equal mix of stocks and bonds to mitigate risk while allowing for moderate growth. (70% Growth 30% Defensive)",
        "Moderate Growth": "Focuses on long-term capital appreciation and is willing to accept high volatility. The portfolio is heavily weighted toward equities with only a small portion in bonds. (80% Growth 20% Defensive)",
        "High Growth": "Willing to endure maximum risk and substantial short-term losses for the potential of high long-term returns, often investing almost entirely in stocks or speculative, high-growth assets. (95% Growth and 5% Defensive)"
    }
    
    current_risk = profile.get('risk_tolerance', "Balanced")
    if current_risk not in risk_options: current_risk = "Balanced"
    
    risk_tolerance = st.select_slider(
        "How comfortable are you with investment volatility?", 
        options=risk_options,
        value=current_risk,
        help="Your comfort level with market fluctuations",
        label_visibility="collapsed"
    )
    
    st.info(f"ℹ️ **{risk_tolerance}:** {risk_descriptions[risk_tolerance]}")
    
    
    # Calculate button logic
    # Real-time updates: Once clicked, it stays active and updates on input changes
    if st.button("🚀 Assess My Readiness", type="primary", use_container_width=True):
        st.session_state['tier1_submitted'] = True

    if st.session_state.get('tier1_submitted', False):
        # Update Global Profile
        st.session_state.user_profile.update({
            "age": age,
            "marital_status": marital_status,
            "income": income,
            "user_income": user_income,
            "partner_income": partner_income,
            "dependants": dependants,
            "home_value": home_value,
            "mortgage": mortgage,
            "risk_tolerance": risk_tolerance,
            "experience": experience,
            "state": state
        })
        # Calculate scores
        scores = calculate_readiness_scores(equity, income, experience, risk_tolerance, age, dependants)
        st.session_state['tier1_results'] = {
            'scores': scores,
            'equity': equity,
            'income': income,
            'user_income': user_income,
            'partner_income': partner_income,
            'experience': experience,
            'risk_tolerance': risk_tolerance,
            'age': age,
            'dependants': dependants,
            'marital_status': marital_status
        }
        
    # Display Results if they exist in state
    if 'tier1_results' in st.session_state:
        results = st.session_state['tier1_results']
        scores = results['scores']
        total_score = scores['total']
        
        # Display Results
        st.markdown("## 📊 Your Readiness Score")
        
        st.info("""
        **ℹ️ How this score is calculated:**
        The **Financial Readiness Score** is a composite metric derived from 4 key pillars:
        1.  **Equity Strength (30%)**: Your accessible home equity relative to property value.
        2.  **Income Capacity (30%)**: Household surplus income potential.
        3.  **Experience (20%)**: Your history with different asset classes.
        4.  **Risk Profile (20%)**: Alignment with growth-oriented strategies.
        """)
        
        # Gauge Chart
        fig = create_gauge_chart(total_score)
        st.plotly_chart(fig, use_container_width=True)
        
        # Overall Assessment
        assessment = get_assessment_level(total_score)
        if assessment == "Ready":
            st.success(f"**🎉 Readiness Score: Strong.** Score: {total_score}/100. Your financial position suggests you may be ready for advanced strategies.")
        elif assessment == "Building":
            st.warning(f"**⚡ Readiness Score: Building Foundation.** Score: {total_score}/100. You are on track to building a strong foundation.")
        else:
            st.info(f"**🌱 Readiness Score: Early Stage.** Score: {total_score}/100. Focus on strengthening your base first.")
        
        # Component Breakdown
        st.markdown("### 📈 Score Breakdown")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**💰 Equity Score**")
            st.progress(scores['equity'] / 30)
            st.caption(f"{scores['equity']}/30 points • {get_equity_feedback(results['equity'])}")
            
            st.markdown("**📊 Experience Score**")
            st.progress(scores['experience'] / 20)
            st.caption(f"{scores['experience']}/20 points • {results['experience']}")
        
        with col_b:
            st.markdown("**💵 Income Score**")
            st.progress(scores['income'] / 30)
            st.caption(f"{scores['income']}/30 points • {get_income_feedback(results['income'])}")
            
            st.markdown("**🎯 Risk Capacity Score**")
            st.progress(scores['risk'] / 20)
            st.caption(f"{scores['risk']}/20 points • {results['risk_tolerance']} investor")
            st.caption(get_projection_disclaimer())
        
        # Strategy Recommendations
        st.markdown("### 💡 Strategies to Explore")
        show_recommendations(total_score, assessment)
        
    
        render_footer_disclaimer()
        
        return {
            "age": results['age'],
            "marital_status": results['marital_status'],
            "dependants": results['dependants'],
            "equity": results['equity'],
            "income": results['income'],
            "experience": results['experience'],
            "risk_tolerance": results['risk_tolerance'],
            "total_score": total_score
        }
    
    return None


def calculate_readiness_scores(equity, income, experience, risk_tolerance, age=35, dependants=0):
    """Calculate component scores and total readiness score."""
    
    # Equity Score (0-30)
    if equity >= 500000:
        equity_score = 30
    elif equity >= 200000:
        equity_score = 25
    elif equity >= 100000:
        equity_score = 20
    elif equity >= 50000:
        equity_score = 12
    else:
        equity_score = max(0, int(equity / 10000))
    
    # Income Score (0-30)
    if income >= 200000:
        income_score = 30
    elif income >= 150000:
        income_score = 26
    elif income >= 120000:
        income_score = 22
    elif income >= 100000:
        income_score = 18
    elif income >= 80000:
        income_score = 14
    else:
        income_score = max(0, int(income / 10000))
    
    # Adjust income score based on dependants (more dependants = higher income needed)
    if dependants > 0:
        income_adjustment = min(5, dependants * 2)  # Lose up to 5 points for dependants
        income_score = max(0, income_score - income_adjustment)
    
    # Experience Score (0-20)
    if "Advanced" in experience:
        experience_score = 20
    elif "Intermediate" in experience:
        experience_score = 12
    else:
        experience_score = 5
    
    # Risk Score (0-20)
    risk_map = {
        "Conservative": 5,
        "Moderately Conservative": 8,
        "Balanced": 12,
        "Moderate Growth": 16,
        "High Growth": 20
    }
    risk_score = risk_map.get(risk_tolerance, 12)
    
    # Age bonus: younger investors have more time for compounding
    age_bonus = 0
    if age < 35:
        age_bonus = 5
    elif age < 45:
        age_bonus = 3
    elif age < 55:
        age_bonus = 1
    
    total = equity_score + income_score + experience_score + risk_score + age_bonus
    
    return {
        'equity': equity_score,
        'income': income_score,
        'experience': experience_score,
        'risk': risk_score,
        'age_bonus': age_bonus,
        'total': total
    }


def create_gauge_chart(score):
    """Create a gauge chart for the readiness score."""
    
    # Determine color based on score
    if score >= 70:
        color = "#4CAF50"  # Green
    elif score >= 40:
        color = "#FF9800"  # Orange
    else:
        color = "#F44336"  # Red
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Readiness Score", 'font': {'size': 24}},
        number = {'suffix': "/100", 'font': {'size': 40}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#FFEBEE'},
                {'range': [40, 70], 'color': '#FFF3E0'},
                {'range': [70, 100], 'color': '#E8F5E9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def get_assessment_level(score):
    """Get assessment level based on total score."""
    if score >= 70:
        return "Ready"
    elif score >= 40:
        return "Building"
    else:
        return "Foundation"


def get_equity_feedback(equity):
    """Get feedback text for equity level."""
    if equity >= 500000:
        return "Excellent equity position"
    elif equity >= 200000:
        return "Strong equity available"
    elif equity >= 100000:
        return "Good equity base"
    elif equity >= 50000:
        return "Building equity"
    else:
        return "Focus on building equity"


def get_income_feedback(income):
    """Get feedback text for income level."""
    if income >= 200000:
        return "High income household"
    elif income >= 150000:
        return "Above average income"
    elif income >= 120000:
        return "Good income level"
    elif income >= 100000:
        return "Median+ income"
    else:
        return "Building income capacity"





def show_recommendations(score, assessment):
    """Show personalized strategy recommendations."""
    
    if assessment == "Ready":
        st.success("""
        **✅ Your Next Strategic Move:**
        
        You have the foundation to accelerate wealth creation. The key comparison for you is typically **Investment Property vs. Debt Funded Investment Portfolio**.
        
        **1. Investment Property**
        *   Traditional route with high leverage.
        *   High entry costs (Stamp Duty, LMI).
        *   Often negatively geared for long periods.

        **2. Debt Funded Investment Portfolio (Recommended for Flexibility)**
        *   **Tax Effective**: Convert non-deductible debt into tax-deductible investment debt (Debt Recycling).
        *   **Flexible**: Start small, dollar-cost average, and access funds if needed (liquidity).
        *   **Efficient**: No Stamp Duty means 100% of your capital works for you immediately.
        
        **💡 Recommendation:** Explore the **Debt Funded Portfolio** model to see how flexibility and tax benefits compare.
        """)
    
    elif assessment == "Building":
        st.warning("""
        **⚡ Concepts to Consider:**
        - **Super Optimization** (Tier 3): See the projected difference a High Growth allocation could make.
        - **Debt Recycling**: Model the effects of starting with conservative amounts (e.g., $50k-$100k).
        - **Equity Building**: Calculate the impact of paying down your mortgage vs. renovating.
        - **Income Factors**: Explore how income changes could affect your borrowing capacity.
        
        **💡 Suggested Next Step**: Run the Tier 3 Super Power calculator to view projections.
        """)
    
    else:
        st.info("""
        **🌱 Foundational Concepts:**
        - **Emergency Funds**: Consider the security of maintaining a 3-6 month expense buffer.
        - **Debt Management**: Evaluate the guaranteed return of reducing high-interest debt.
        - **Super Contributions**: Model the result of salary sacrifice or voluntary contributions.
        - **Financial Knowledge**: Access educational resources on investing principles.
        
        **💡 Suggested Next Step**: Review the effectiveness of savings and debt reduction strategies.
        """)
        
    st.caption("⚠️ *Disclaimer: This tool provides general information and projections for educational purposes only. It does not constitute personal financial advice and has not considered your personal circumstances.*")





def analyze_tier1(data):
    """Legacy function for compatibility - returns status based on score."""
    score = data.get("total_score", 0)
    
    if score >= 70:
        return "ready", "Assessment suggests strong positioning for advanced strategies."
    elif score >= 40:
        return "maybe", "Assessment suggests focus on building equity and income."
    else:
        return "not_ready", "Assessment suggests focusing on foundations."

