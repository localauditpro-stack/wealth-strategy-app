def calculate_lead_score(data, engagement_metrics=None):
    """Calculates a lead score based on financial data and engagement."""
    score = 0
    
    # Financial Scoring
    equity = data.get("equity", 0)
    income = data.get("income", 0)
    
    # Equity Points
    if equity >= 2000000:
        score += 60
    elif equity >= 1000000:
        score += 40
    elif equity >= 500000:
        score += 25
    elif equity >= 250000:
        score += 15
        
    # Income Points
    if income >= 300000:
        score += 50
    elif income >= 200000:
        score += 35
    elif income >= 150000:
        score += 20
    elif income >= 100000:
        score += 10

    # Engagement Points (placeholder for now)
    if engagement_metrics:
        score += engagement_metrics.get("calculator_complete", 0) * 10
        score += engagement_metrics.get("email_provided", 0) * 5
        
    return score

def get_lead_tier(score):
    if score >= 80:
        return "Platinum"
    elif score >= 60:
        return "Gold"
    elif score >= 40:
        return "Silver"
    elif score >= 25:
        return "Bronze"
    else:
        return "Unqualified"
