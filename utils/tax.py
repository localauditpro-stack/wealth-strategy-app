def calculate_income_tax(income):
    """
    Calculates annual income tax based on 2024-25 (Stage 3) tax rates + 2% Medicare Levy.
    
    Rates:
    0 – $18,200: 0%
    $18,201 – $45,000: 16%
    $45,001 – $135,000: 30%
    $135,001 – $190,000: 37%
    $190,001+: 45%
    """
    tax = 0
    if income <= 18200:
        return 0
    
    # 18,201 - 45,000 @ 16%
    tax += (min(income, 45000) - 18200) * 0.16
    
    if income > 45000:
        # 45,001 - 135,000 @ 30%
        tax += (min(income, 135000) - 45000) * 0.30
        
    if income > 135000:
        # 135,001 - 190,000 @ 37%
        tax += (min(income, 190000) - 135000) * 0.37
        
    if income > 190000:
        # 190,001+ @ 45%
        tax += (income - 190000) * 0.45
        
    # Medicare Levy (simplified 2%)
    # Note: Medicare reduction/surcharge logic omitted for MVP simplicity
    medicare = income * 0.02
    
    return tax + medicare

def calculate_marginal_rate(income):
    """Returns the marginal tax rate for a given income level (including Medicare)."""
    if income <= 18200:
        return 0.0
    elif income <= 45000:
        return 0.16 + 0.02
    elif income <= 135000:
        return 0.30 + 0.02
    elif income <= 190000:
        return 0.37 + 0.02
    else:
        return 0.45 + 0.02

def calculate_stamp_duty(state, property_value, investor=True):
    """
    Estimates Stamp Duty based on State and Property Value.
    These are approximations for 2024/25.
    """
    duty = 0
    
    if state == "NSW":
        # Simplified NSW brackets
        if property_value <= 16000:
            duty = property_value * 0.0125
        elif property_value <= 35000:
            duty = 200 + (property_value - 16000) * 0.015
        elif property_value <= 93000:
            duty = 485 + (property_value - 35000) * 0.0175
        elif property_value <= 351000:
            duty = 1500 + (property_value - 93000) * 0.035
        elif property_value <= 1168000:
            duty = 10530 + (property_value - 351000) * 0.045
        else:
            duty = 47295 + (property_value - 1168000) * 0.055
            
    elif state == "VIC":
        # Simplified VIC brackets
        if property_value <= 25000:
            duty = property_value * 0.014
        elif property_value <= 130000:
            duty = 350 + (property_value - 25000) * 0.024
        elif property_value <= 440000:
            duty = 2870 + (property_value - 130000) * 0.05
        elif property_value <= 960000:
            duty = 18370 + (property_value - 440000) * 0.06
        else:
            duty = property_value * 0.055 # Flatish rate above threshold approximation
            
    elif state == "QLD":
        # Simplified QLD brackets
        if property_value <= 5000:
            duty = 0
        elif property_value <= 75000:
            duty = (property_value - 5000) * 0.015
        elif property_value <= 540000:
            duty = 1050 + (property_value - 75000) * 0.035
        elif property_value <= 1000000:
            duty = 17325 + (property_value - 540000) * 0.045
        else:
            duty = 38025 + (property_value - 1000000) * 0.0575
            
    # Default fallback for other states (approx 4%)
    else: 
        duty = property_value * 0.04
        
    return duty

def calculate_lmi(loan_amount, property_value):
    """
    Estimates Lenders Mortgage Insurance (LMI).
    Normally applicable if LVR > 80%.
    """
    lvr = loan_amount / property_value
    
    if lvr <= 0.80:
        return 0
    
    # Very rough approximation of Genworth/QBE tables
    # LMI scales exponentially with LVR
    if lvr <= 0.85:
        rate = 0.01 # 1%
    elif lvr <= 0.90:
        rate = 0.02 # 2%
    elif lvr <= 0.95:
        rate = 0.04 # 4%
    else:
        rate = 0.05 # 5%
        
    return loan_amount * rate

def calculate_land_tax(state, land_value):
    """
    Estimates Land Tax. 
    Note: Land Value is usually 50-70% of Property Value.
    """
    # Simplified threshold check
    tax = 0
    if state == "NSW":
        threshold = 1075000
        if land_value > threshold:
            tax = 100 + (land_value - threshold) * 0.016
    elif state == "VIC":
        threshold = 50000
        if land_value > threshold:
             # Vic has lower thresholds and higher rates generally
            tax = 500 + (land_value - threshold) * 0.015 # rough avg
            
    elif state == "QLD":
        threshold = 600000
        if land_value > threshold:
            tax = 500 + (land_value - threshold) * 0.01 # simplified
    elif state == "WA":
        threshold = 300000
        if land_value > threshold:
            tax = 300 + (land_value - threshold) * 0.0055 # simplified
    elif state == "SA":
        threshold = 534000
        if land_value > threshold:
             tax = (land_value - threshold) * 0.005 # simplified 

    return tax
