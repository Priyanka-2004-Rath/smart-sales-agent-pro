import pandas as pd
from datetime import datetime

def get_lead_warmth_score(mood_category: str, intensity: str) -> str:
    """Determine warmth score based on mood and intensity."""
    if mood_category in ["excited", "happy"] and intensity in ["medium", "high"]:
        return "🔥 Hot"
    elif mood_category in ["happy", "neutral"] and intensity in ["medium", "low"]:
        return "🟠 Warm"
    elif mood_category in ["sad", "frustrated", "angry"]:
        return "❄️ Cold"
    else:
        return "🟡 Medium"

def generate_lead_summary(user_input: str) -> str:
    """Generate a brief summary based on common keywords in user input."""
    lowered = user_input.lower()
    summary_parts = []

    # Check for intent phrases
    if any(word in lowered for word in ["price", "cost", "charge", "plan", "pricing"]):
        summary_parts.append("Inquired about pricing.")
    if any(word in lowered for word in ["demo", "schedule", "book", "meeting"]):
        summary_parts.append("Requested a demo.")
    if any(word in lowered for word in [
        "problem", "issue", "not working", "support", "crash", "crashing", "bug",
        "glitch", "reinstall", "freeze", "lag", "slow", "error", "fail"
    ]):
        summary_parts.append("Reported a problem.")
    if any(word in lowered for word in [
        "disappointed", "upset", "bad experience", "angry", "frustrated", "unhappy", "unsatisfied"
    ]):
        summary_parts.append("Expressed dissatisfaction.")

    return " ".join(summary_parts) if summary_parts else "General inquiry."

def suggest_next_action(summary: str) -> str:
    """Suggest next action based on keywords in summary."""
    summary = summary.lower()
    if "pricing" in summary:
        return "Send pricing details"
    elif "demo" in summary:
        return "Schedule a demo"
    elif "problem" in summary or "issue" in summary:
        return "Assign to support team"
    elif "dissatisfaction" in summary:
        return "Escalate to customer success team"
    else:
        return "No action needed"

def save_lead_to_csv(data: dict, filename: str = "lead_data.csv") -> None:
    """Append the lead data to CSV for storage."""
    df = pd.DataFrame([data])
    try:
        existing = pd.read_csv(filename)
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ Warning: Error reading {filename}: {e}")
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
