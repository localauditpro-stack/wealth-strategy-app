import streamlit as st

def render_lead_capture_form(key_suffix, button_label="Unlock Full Report"):
    """
    Renders a standard lead capture form with qualifying questions.
    Returns True if valid submission, False otherwise.
    Stores data in st.session_state.lead_data.
    """
    with st.form(f"lead_capture_{key_suffix}"):
        st.markdown("### 🔓 Unlock Your Detailed Strategy Report")
        st.write("Get the full breakdown, year-by-year analysis, and professional PDF report.")
        
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name (Optional)", key=f"name_{key_suffix}")
            email = st.text_input("Email Address (Required)*", key=f"email_{key_suffix}")
        with c2:
            phone = st.text_input("Mobile Number (Required for Report)*", key=f"phone_{key_suffix}")
            goal = st.selectbox(
                "Primary Financial Goal",
                ["Build Wealth / Expand Portfolio", "Buy First Home", "Retirement Planning", "Reduce Tax / Debt", "Other"],
                key=f"goal_{key_suffix}"
            )
            
        advisor_status = st.radio(
            "Are you currently working with a financial advisor?",
            ["No", "Yes", "Previously"],
            horizontal=True,
            key=f"advisor_{key_suffix}"
        )
        
        submitted = st.form_submit_button(button_label, type="primary", use_container_width=True)
        
        if submitted:
            if not email or "@" not in email:
                st.error("Please enter a valid email address.")
                return False
            if not phone:
                st.error("Please enter a mobile number to unlock the detailed report.")
                return False
                
            # Initialize or update lead data
            if 'lead_data' not in st.session_state:
                st.session_state.lead_data = {}
                
            st.session_state.lead_data.update({
                "name": name,
                "email": email,
                "phone": phone,
                "goal": goal,
                "advisor_status": advisor_status,
                "source": key_suffix
            })
            
            # Simple success feeling
            st.success(f"Success! Unlocking your report now...")
            return True
            
    return False
