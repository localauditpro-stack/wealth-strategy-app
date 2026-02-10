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
            color: #002B5C !important; /* Apt Navy */
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        /* Metric Cards - Target the value and label */
        [data-testid="stMetricValue"] {
            color: #C5A059 !important; /* Apt Gold */
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #002B5C !important;
        }
        
        /* Sidebar Background */
        section[data-testid="stSidebar"] {
            background-color: #F0F2F6;
            border-right: 2px solid #C5A059;
        }
        
        /* Primary Buttons */
        div.stButton > button {
            background-color: #002B5C !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            width: 100%; /* Full width on mobile */
        }
        div.stButton > button:hover {
            background-color: #C5A059 !important;
            color: white !important;
            border: 1px solid #002B5C;
        }
        
        /* Expander Headers */
        .streamlit-expanderHeader {
            color: #002B5C !important;
            font-weight: 600;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #002B5C 0%, #001A38 100%);
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
        
        /* Card Styling for Inputs */
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            border: 1px solid #E0E0E0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation
    with st.sidebar:
        # st.title("Navigation") # Option menu has its own style
        
        # Use simple indices to map selection to pages for easier logic
        pages = [
            "Home", 
            "Tier 1: Am I Ready?", 
            "Tier 2: Portfolio vs Property", 
            "Tier 3: Super Power",
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
            icons=['house', 'check-circle', 'graph-up-arrow', 'lightning', 'hourglass-split'], 
            menu_icon="cast", 
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#C5A059", "font-size": "16px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#002B5C"},
            }
        )
        
        # Sync Sidebar Selection -> Session State
        # Only update if the user manually clicked the sidebar (different from current state)
        if selected_nav != st.session_state.page_selection:
             st.session_state.page_selection = selected_nav
             st.rerun()

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
            st.info("Start Here")
            st.markdown("### 🔍 Readiness Check")
            st.write("Assess your financial health and eligibility for advanced strategies in under 2 minutes.")
            if st.button("Start Assessment", key="btn_tier1", type="primary"):
                go_to_page("Tier 1: Am I Ready?")
                
        with c2:
            st.markdown("### 📈 Strategy Compare")
            st.write("Data-driven comparison of Debt Recycling vs. Investment Property.")
            if st.button("Compare Strategies", key="btn_tier2"):
                 go_to_page("Tier 2: Portfolio vs Property")

        with c3:
            st.markdown("### ⏱️ Cost of Waiting")
            st.write("Visualize the compound impact of delaying your investment decisions.")
            if st.button("View Cost of Waiting", key="btn_cow"):
                go_to_page("Cost of Waiting (Bonus)")
            
        st.divider()
        st.markdown("### 🎯 Identify Your Opportunity")

        # Educational Grid
        e1, e2 = st.columns(2)
        with e1:
             st.markdown("""
                <div class="card" style="border-left: 5px solid #C5A059;">
                    <h4>💸 The "Silent" Tax Leak</h4>
                    <p>Your 47% marginal rate is eroding your compound growth. See the difference structuring makes.</p>
                </div>
            """, unsafe_allow_html=True)
            
        with e2:
             st.markdown("""
                <div class="card" style="border-left: 5px solid #002B5C;">
                    <h4>📉 The $200k Super Gap</h4>
                    <p>A 1% difference in fees and performance can cost a high-earner six figures by retirement.</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.write("") # Spacing
        
    elif selection == "Tier 1: Am I Ready?":
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
                 go_to_page("Tier 2: Portfolio vs Property")
                 
    elif selection == "Tier 2: Portfolio vs Property":
        render_tier2()
        
        st.divider()
        st.markdown("### See the power of Super?")
        if st.button("Check Super Power 👉", type="primary"):
            go_to_page("Tier 3: Super Power")
        
    elif selection == "Tier 3: Super Power":
        render_tier3_super()
        
        st.divider()
        st.markdown("### Bonus: The Cost of Delay")
        if st.button("View Cost of Waiting 👉", type="primary"):
            go_to_page("Cost of Waiting (Bonus)")
        
    elif selection == "Cost of Waiting (Bonus)":
        render_cost_of_waiting()
        st.divider()
        if st.button("🏠 Back to Home"):
            go_to_page("Home")

if __name__ == "__main__":
    main()
