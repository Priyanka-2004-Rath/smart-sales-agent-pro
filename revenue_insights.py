import pandas as pd

def compute_revenue_summary(csv_path: str = "lead_data.csv",
                            hot_value: int = 10000,
                            warm_value: int = 5000,) -> dict:
    """
    Reads lead data and computes summary statistics including lead counts
    and estimated revenue. Revenue values for hot/warm leads are adjustable.

    Args:
        csv_path (str): Path to the CSV file.
        hot_value (int): Revenue per hot lead.
        warm_value (int): Revenue per warm lead.

    Returns:
        dict: Summary with counts and total revenue.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {
            "hot_count": 0,
            "warm_count": 0,
            "cold_count": 0,
            "total_revenue": 0,
            "dataframe": pd.DataFrame()
        }

    # Categorize lead warmth from emojis in 'Lead Score'
    df["lead_type"] = df["Lead Score"].apply(
        lambda score: "hot" if isinstance(score, str) and "🔥" in score
        else "warm" if isinstance(score, str) and "🟠" in score
        else "cold"
    )

    # Estimate revenue using editable values
    def estimate_custom_revenue(lead_type):
        if lead_type == "hot":
            return hot_value
        elif lead_type == "warm":
            return warm_value
        else:
            return 0

    df["estimated_revenue"] = df["lead_type"].apply(estimate_custom_revenue)

    # Count leads
    hot_count = (df["lead_type"] == "hot").sum()
    warm_count = (df["lead_type"] == "warm").sum()
    cold_count = (df["lead_type"] == "cold").sum()
    total_revenue = df["estimated_revenue"].sum()

    return {
        "hot_count": hot_count,
        "warm_count": warm_count,
        "cold_count": cold_count,
        "total_revenue": total_revenue,
        "actual_revenue": df["estimated_revenue"].sum(),     # same as total
        "projected_revenue": hot_count * hot_value + warm_count * warm_value,
        "dataframe": df
    }
