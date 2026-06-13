import pandas as pd


def explain_city_rank(row: pd.Series) -> str:
    city = row["city"]

    rank_difference = row["rank_difference"]


    # TODO: This needs to be redone to not be a comparison to the base rank, just explanations.
    #       ALso rank by selected cities not the ranking of them???
    if rank_difference > 0:
        movement = (
            f"{city} moves up compared to the base CityFit rank because the personalized "
            "CityFit profile rewards its strengths more than the baseline ranking does."
        )
    elif rank_difference < 0:
        movement = (
            f"{city} moves down compared to the base CityFit rank because some of its tradeoffs "
            "matter more under the selected CityFit priorities."
        )
    else:
        movement = (
            f"{city} ranks about the same in CityFit as it does in the CityFit baseline, "
            "which suggests the personalized priorities broadly agree with the baseline ranking."
        )

    strengths = []
    tradeoffs = []

    if row["climate_index"] >= 80:
        strengths.append(f"strong climate fit ({row['climate_index']:.1f})")

    if row["safety_index"] >= 70:
        strengths.append(f"strong safety ({row['safety_index']:.1f})")
    elif row["safety_index"] < 55:
        tradeoffs.append(f"weaker safety ({row['safety_index']:.1f})")

    if row["healthcare_index"] >= 70:
        strengths.append(f"strong healthcare ({row['healthcare_index']:.1f})")
    elif row["healthcare_index"] < 60:
        tradeoffs.append(f"weaker healthcare ({row['healthcare_index']:.1f})")

    if row["cost_of_living_index"] < 65:
        strengths.append(f"moderate cost of living ({row['cost_of_living_index']:.1f})")
    elif row["cost_of_living_index"] >= 85:
        tradeoffs.append(f"high cost of living ({row['cost_of_living_index']:.1f})")

    if row["traffic_commute_index"] < 35:
        strengths.append(f"less traffic ({row['cost_of_living_index']:.1f})")
    elif row["cost_of_living_index"] >= 85:
        tradeoffs.append(f"more traffic ({row['cost_of_living_index']:.1f})")

    if row["pollution_index"] < 35:
        strengths.append(f"low pollution ({row['pollution_index']:.1f})")
    elif row["pollution_index"] >= 55:
        tradeoffs.append(f"higher pollution ({row['pollution_index']:.1f})")

    if row["purchasing_power_index"] >= 100:
        strengths.append(f"strong purchasing power ({row['purchasing_power_index']:.1f})")
    elif row["purchasing_power_index"] < 70:
        tradeoffs.append(f"lower purchasing power ({row['purchasing_power_index']:.1f})")

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