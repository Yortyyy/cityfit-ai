import pandas as pd


def explain_city_rank(row: pd.Series) -> str:
    city = row["city"]

    moved_direction = "higher" if row["rank_difference"] > 0 else "lower"

    strengths = []
    weaknesses = []

    if row["safety_index"] >= 70:
        strengths.append("strong safety")
    elif row["safety_index"] < 50:
        weaknesses.append("lower safety")

    if row["healthcare_index"] >= 70:
        strengths.append("strong healthcare")
    elif row["healthcare_index"] < 60:
        weaknesses.append("weaker healthcare")

    if row["climate_index"] >= 80:
        strengths.append("favorable climate")

    if row["cost_of_living_index"] >= 80:
        weaknesses.append("high cost of living")
    elif row["cost_of_living_index"] < 65:
        strengths.append("moderate cost of living")

    if row["pollution_index"] >= 50:
        weaknesses.append("higher pollution")
    elif row["pollution_index"] < 35:
        strengths.append("lower pollution")

    strengths_text = ", ".join(strengths) if strengths else "balanced overall metrics"
    weaknesses_text = ", ".join(weaknesses) if weaknesses else "few major downside signals"

    return (
        f"{city} ranks {moved_direction} in CityFit than its Numbeo baseline because it has "
        f"{strengths_text}. For weaknesses, it has {weaknesses_text}."
    )