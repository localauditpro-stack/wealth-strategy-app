import streamlit as st
from streamlit_option_menu import option_menu
from calculators.tier1 import render_tier1, analyze_tier1
from calculators.tier2 import render_tier2
from calculators.tier3_super import render_tier3_super
from calculators.cost_of_waiting import render_cost_of_waiting
from utils.scoring import calculate_lead_score, get_lead_tier

def main():
    st.set_page_config(
        page_title="Wealth Strategy Generator",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state for shared user profile data
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            "age": 35,
            "marital_status": "Married/De facto",
            "income": 120000,
            "dependants": 0,
            "home_value": 1000000,
            "mortgage": 600000,
            "risk_tolerance": "Balanced",
            "experience": "Intermediate (Some Shares/Property)",
            "state": "NSW"
        }
    
    # Initialize session state for lead data if not exists
    if 'lead_data' not in st.session_state:
        st.session_state.lead_data = {
            "email": "",
            "phone": "",
            "score": 0,
            "tier": "Unknown",
            "data": {}
        }
        
    # Initialize navigation state
    if 'page_selection' not in st.session_state:
        st.session_state.page_selection = "Home"

    # --- CUSTOM CSS FOR APT WEALTH THEME ---
    st.markdown("""
        <style>
        /* Main Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #1A2B3C !important; /* Apt Deep Navy */
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        /* Metric Cards - Target the value and label */
        [data-testid="stMetricValue"] {
            color: #C5A059 !important; /* Apt Gold */
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #1A2B3C !important;
        }
        
        /* Sidebar Background */
        section[data-testid="stSidebar"] {
            background-color: #F0F2F6;
            border-right: 2px solid #C5A059;
        }
        
        /* Primary Buttons */
        div.stButton > button {
            background-color: #1A2B3C !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            width: 100%; /* Full width on mobile */
        }
        div.stButton > button:hover {
            background-color: #C5A059 !important;
            color: white !important;
            border: 1px solid #1A2B3C;
        }
        
        /* Expander Headers */
        .streamlit-expanderHeader {
            color: #1A2B3C !important;
            font-weight: 600;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #1A2B3C 0%, #001A38 100%);
            padding: 4rem 2rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .hero h1 {
            color: #C5A059 !important;
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1.2rem;
            color: #E0E0E0;
            max-width: 600px;
            margin: 0 auto 2rem auto;
        }
        
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation
    with st.sidebar:
        # st.title("Navigation") # Option menu has its own style
        
        # Use simple indices to map selection to pages for easier logic
        pages = [
            "Home", 
            "Tier 1: Clarity (Readiness)", 
            "Tier 2: Direction (Strategy)", 
            "Tier 3: Acceleration (Super)",
            "Tier 4: Freedom (FIRE)",
            "Tier 5: Protection (Legacy)",
            "Strategy Summary",
            "Cost of Waiting (Bonus)"
        ]
        
        # Determine default index based on session state
        try:
            default_index = pages.index(st.session_state.page_selection)
        except ValueError:
            default_index = 0
            
        selected_nav = option_menu(
            "Navigation", 
            pages, 
            icons=['house', 'check-circle', 'graph-up-arrow', 'lightning', 'fire', 'bank', 'clipboard-check', 'hourglass-split'], 
            menu_icon="cast", 
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#C5A059", "font-size": "16px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#1A2B3C"},
            }
        )
        
        # Sync Sidebar Selection -> Session State
        # Only update if the user manually clicked the sidebar (different from current state)
        if selected_nav != st.session_state.page_selection:
             st.session_state.page_selection = selected_nav
             st.rerun()

        # Compliance Disclaimer
        from utils.compliance import render_sidebar_disclaimer
        render_sidebar_disclaimer()

    # Define a helper to change page
    def go_to_page(page_name):
        st.session_state.page_selection = page_name
        st.rerun()

    # Main Content Rendering based on Session State
    selection = st.session_state.page_selection

    if selection == "Home":
        # Hero Section
        st.markdown("""
            <div class="hero">
                <h1>Wealth Strategy Generator</h1>
                <p>Discover optimized financial strategies tailored for Australian investors. compare debt recycling, investment properties, and more with precision.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature Grid with Interaction
        st.markdown("### 🚀 Start Your Journey")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🔍 Readiness Check")
            st.write("Assess your financial health and eligibility for advanced strategies in under 2 minutes.")
            if st.button("Start Assessment", key="btn_tier1", type="primary"):
                go_to_page("Tier 1: Clarity (Readiness)")
                
        with c2:
            st.markdown("### 📈 Strategy Compare")
            st.write("Data-driven comparison of Debt Recycling vs. Investment Property.")
            if st.button("Compare Strategies", key="btn_tier2"):
                 go_to_page("Tier 2: Direction (Strategy)")

        with c3:
            st.markdown("### ⚡ Super Power")
            st.write("The exponential impact of high growth super over time.")
            if st.button("Optimize Super", key="btn_tier3"):
                go_to_page("Tier 3: Acceleration (Super)")
            
        st.divider()
        st.markdown("### 🎯 Identify Your Opportunity")

        # Educational Grid
        e1, e2 = st.columns(2)
        with e1:
             with st.container(border=True):
                 st.markdown("#### 💸 The \"Silent\" Tax Leak")
                 st.write("Your 47% marginal rate is eroding your compound growth. See the difference structuring makes.")
                 
             with st.container(border=True):
                 st.markdown("#### 🏠 Equity: Idle or Working?")
                 st.write("Is your home's capital appreciation locked away, or are you recycling it into wealth?")

        with e2:
             with st.container(border=True):
                 st.markdown("#### 📉 The $200k Super Gap")
                 st.write("A 1% difference in fees and performance can cost a high-earner six figures by retirement.")
                 
             with st.container(border=True):
                 st.markdown("#### 🏛️ Strategy & Legacy")
                 st.write("Advanced preservation: FIRE bridges, Estate planning, and Recontribution strategies.")
                 if st.button("View Advanced Strategies", key="btn_tier4"):
                     go_to_page("Tier 4: Freedom (FIRE)")
            
        st.write("") # Spacing
        
    elif selection == "Tier 1: Clarity (Readiness)":
        data = render_tier1()
        
        if data:
            status, message = analyze_tier1(data)
            score = calculate_lead_score(data, engagement_metrics={"calculator_complete": 1})
            tier = get_lead_tier(score)
            
            st.divider()
            if status == "ready":
                st.success(f"Result: {message}")
                st.info("You appear ready for advanced strategies. Unlock the full report to see details.")
            elif status == "maybe":
                st.warning(f"Result: {message}")
            else:
                st.error(f"Result: {message}")
                
            # Email Capture
            with st.form("tier1_capture"):
                email = st.text_input("Enter your email to get the full analysis:")
                submit_capture = st.form_submit_button("Get Analysis")
                
                if submit_capture and email:
                    # Mock database save
                    st.session_state['lead_data'] = {
                        "email": email,
                        "score": score,
                        "tier": tier,
                        "data": data
                    }
                    st.success(f"Thank you! Your analysis has been sent to {email}.")
                    st.balloons()
            
            # Next Button logic (independent of form)
            st.write("")
            st.markdown("### Ready for the next step?")
            if st.button("Proceed to Strategy Comparison 👉", type="primary"):
                 go_to_page("Tier 2: Direction (Strategy)")
                 
    elif selection == "Tier 2: Direction (Strategy)":
        render_tier2()
        
        st.divider()
        st.markdown("### See the power of Super?")
        if st.button("Check Super Power 👉", type="primary"):
            go_to_page("Tier 3: Acceleration (Super)")
        
    elif selection == "Tier 3: Acceleration (Super)":
        render_tier3_super()
        
        st.divider()
        st.markdown("### Advanced: FIRE Strategy")
        if st.button("View FIRE Strategy 👉", type="primary"):
            go_to_page("Tier 4: Freedom (FIRE)")

    elif selection == "Tier 4: Freedom (FIRE)":
        from calculators.fire import render_fire_calculator
        render_fire_calculator()
        
        st.divider()
        st.markdown("### Next: Estate & Legacy")
        if st.button("View Legacy & Estate 👉", type="primary"):
             go_to_page("Tier 5: Protection (Legacy)")
            
    elif selection == "Tier 5: Protection (Legacy)":
        from calculators.tier5_legacy import render_tier5_legacy
        render_tier5_legacy()
        
        st.divider()
        st.markdown("### 📋 Final Step: Your Strategy Snapshot")
        if st.button("View Strategy Summary 👉", type="primary"):
            go_to_page("Strategy Summary")
            
    elif selection == "Strategy Summary":
        from calculators.summary import render_summary_page
        render_summary_page()
        
    elif selection == "Cost of Waiting (Bonus)":
        render_cost_of_waiting()
        st.divider()
        if st.button("🏠 Back to Home"):
            go_to_page("Home")

if __name__ == "__main__":
    main()
