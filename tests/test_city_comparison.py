import pandas as pd

from cityfit.frontend.components.city_comparison import (
    DIFFERENCE_COLUMN,
    build_city_comparison_table,
    calculate_percent_difference,
    format_difference,
)


def make_comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["Tampa", "Tokyo"],
            "country": ["United States", "Japan"],
            "cityfit_score": [133.3, 132.1],
            "cityfit_rank": [57, 69],
            "purchasing_power_index": [110.0, 95.0],
            "cost_of_living_index": [70.0, 60.0],
            "safety_index": [55.0, 80.0],
            "healthcare_index": [70.0, 85.0],
            "property_price_to_income_ratio": [5.0, 12.0],
            "traffic_commute_index": [35.0, 45.0],
            "climate_index": [90.0, 85.0],
            "pollution_index": [25.0, 20.0],
        }
    )


def test_build_city_comparison_table_includes_percent_difference_from_first_city():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    score_row = comparison[comparison["Metric"] == "CityFit Score"].iloc[0]

    assert score_row[DIFFERENCE_COLUMN] == "-0.9%"


def test_build_city_comparison_table_displays_rank_first_with_hashmark():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    rank_row = comparison.iloc[0]

    assert rank_row["Metric"] == "CityFit Rank"
    assert rank_row["Tampa, United States"] == "#57"
    assert rank_row["Tokyo, Japan"] == "#69"
    assert rank_row[DIFFERENCE_COLUMN] == "+12"


def test_build_city_comparison_table_omits_stronger_fit_column():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    assert "Stronger Fit" not in comparison.columns


def test_build_city_comparison_table_colors_values_from_global_scale():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    cost_row = comparison[comparison["Metric"] == "Cost of Living"].iloc[0]

    assert cost_row["First Color"] != cost_row["Second Color"]


def test_calculate_percent_difference_uses_first_city_as_baseline():
    assert calculate_percent_difference(first_value=50, second_value=75) == 50


def test_format_difference_uses_raw_rank_difference_for_rank():
    assert format_difference(column="cityfit_rank", first_value=57, second_value=69) == "+12"
