import streamlit as st

def parse_currency_input(label, default_value, help_text=None, key=None):
    """
    Creates a text input that behaves like a currency input (with commas),
    parsing user input (e.g. '1,000,000') into an integer.
    """
    # If key is provided, we can force formatting on persistent state
    if key and key in st.session_state:
        # Get current raw value
        current_val = st.session_state[key]
        # Clean and parse it
        try:
            # Handle if it's already an int/float (from previous runs) or string
            if isinstance(current_val, (int, float)):
                 parsed = int(current_val)
            else:
                 clean_str = str(current_val).replace(",", "").replace("$", "").replace(" ", "")
                 if not clean_str: 
                     parsed = 0
                 else:
                     parsed = int(float(clean_str))
            
            # Re-format to string with commas
            formatted_str = f"{parsed:,}"
            
            # Update state if different (this forces the input to show the formatted value)
            if st.session_state[key] != formatted_str:
                st.session_state[key] = formatted_str
                
        except (ValueError, TypeError):
            # If invalid, leave as is (let user correct it)
            pass

    # We use text_input allows commas
    # We format the default value with commas for display
    str_val = f"{default_value:,}"
    
    val_input = st.text_input(
        label, 
        value=str_val, 
        help=help_text,
        key=key
    )
    
    try:
        # Strip commas, spaces, dollars
        clean_val = val_input.replace(",", "").replace("$", "").replace(" ", "")
        if not clean_val: return 0
        return int(float(clean_val)) # Handle float strings
    except ValueError:
        return default_value

def go_to_page(page_name):
    """
    Navigates to the specified page by updating session state and rerunning.
    Requires 'page_selection' to be the key used by streamlit-option-menu in app.py.
    """
    st.session_state.page_selection = page_name
    st.rerun()
