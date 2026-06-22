import pandas as pd


def get_city_strengths_and_tradeoffs(row: pd.Series) -> dict:
    strengths = []
    tradeoffs = []

    if row["climate_index"] >= 80:
        strengths.append("strong climate fit")
    elif row["climate_index"] <= 40:
        tradeoffs.append("harsher climate")

    if row["safety_index"] >= 70:
        strengths.append("strong safety")
    elif row["safety_index"] < 55:
        tradeoffs.append("weaker safety")

    if row["healthcare_index"] >= 70:
        strengths.append("strong healthcare")
    elif row["healthcare_index"] < 60:
        tradeoffs.append("weaker healthcare")

    if row["cost_of_living_index"] < 65:
        strengths.append("moderate cost of living")
    elif row["cost_of_living_index"] >= 85:
        tradeoffs.append("high cost of living")

    if row["traffic_commute_index"] < 35:
        strengths.append("less traffic")
    elif row["traffic_commute_index"] >= 65:
        tradeoffs.append("more traffic")

    if row["pollution_index"] < 35:
        strengths.append("low pollution")
    elif row["pollution_index"] >= 55:
        tradeoffs.append("higher pollution")

    if row["purchasing_power_index"] >= 100:
        strengths.append("strong purchasing power")
    elif row["purchasing_power_index"] < 70:
        tradeoffs.append("lower purchasing power")

    return {
        "strengths": strengths,
        "tradeoffs": tradeoffs,
    }


def explain_city_rank(row: pd.Series) -> str:
    city = row["city"]
    rank_difference = row["rank_difference"]

    if rank_difference > 0:
        movement = (
            f"{city} moves up compared to the neutral CityFit baseline because the personalized "
            "CityFit profile rewards its strengths more than the baseline ranking does."
        )
    elif rank_difference < 0:
        movement = (
            f"{city} moves down compared to the neutral CityFit baseline because some of its tradeoffs "
            "matter more under the selected CityFit priorities."
        )
    else:
        movement = (
            f"{city} ranks about the same as the neutral CityFit baseline, "
            "which suggests the personalized priorities broadly agree with the baseline ranking."
        )

    fit_factors = get_city_strengths_and_tradeoffs(row)
    strengths = fit_factors["strengths"]
    tradeoffs = fit_factors["tradeoffs"]

    strengths_text = _format_list(strengths)
    tradeoffs_text = _format_list(tradeoffs)

    if strengths and tradeoffs:
        return (
            f"{movement} Its strongest factors are {strengths_text}. "
            f"The main tradeoffs are {tradeoffs_text}."
        )

    if strengths:
        return (
            f"{movement} Its strongest factors are {strengths_text}. "
            "No major downside stands out from the currently available metrics, but the dataset is limited."
        )

    if tradeoffs:
        return (
            f"{movement} The main tradeoffs are {tradeoffs_text}. "
            "It may still be a good fit depending on the user's priorities."
        )

    return (
        f"{movement} Its metrics are relatively balanced, with no single factor dominating the recommendation."
    )


def _format_list(items: list[str]) -> str:
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"