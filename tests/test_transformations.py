import pandas as pd

from cityfit.features.transformations import add_affordability_features


def test_add_affordability_features_adds_expected_columns():
    df = pd.DataFrame(
        {
            "numbeo_quality_of_life_index": [180.0],
            "cost_of_living_index": [60.0],
            "purchasing_power_index": [100.0],
            "safety_index": [80.0],
            "healthcare_index": [70.0],
            "pollution_index": [25.0],
            "traffic_commute_index": [30.0],
        }
    )

    result = add_affordability_features(df)

    expected_columns = {
        "quality_per_cost",
        "low_pollution_score",
        "low_traffic_score",
    }

    assert expected_columns.issubset(result.columns)


def test_add_affordability_features_calculates_values_correctly():
    df = pd.DataFrame(
        {
            "numbeo_quality_of_life_index": [180.0],
            "cost_of_living_index": [60.0],
            "purchasing_power_index": [100.0],
            "safety_index": [80.0],
            "healthcare_index": [70.0],
            "pollution_index": [25.0],
            "traffic_commute_index": [30.0],
        }
    )

    result = add_affordability_features(df)

    assert result.loc[0, "quality_per_cost"] == 3.0
    assert result.loc[0, "low_pollution_score"] == 75.0
    assert result.loc[0, "low_traffic_score"] == 70.0