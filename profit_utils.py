# profit_utils.py

def estimate_revenue(lead_score):
    score_str = str(lead_score)
    if "🔥" in score_str:
        return 20000
    elif "🟠" in score_str:
        return 10000
    elif "❄️" in score_str:
        return 2000
    else:
        return 0
