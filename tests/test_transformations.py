import pandas as pd

from cityfit.features.transformations import add_cityfit_features


def test_add_cityfit_features_adds_expected_columns():
    df = pd.DataFrame(
        {
            "cost_of_living_index": [60.0],
            "purchasing_power_index": [100.0],
            "property_price_to_income_ratio": [8.0],
            "safety_index": [80.0],
            "healthcare_index": [70.0],
            "pollution_index": [25.0],
            "climate_index": [85.0],
            "traffic_commute_index": [30.0],
        }
    )

    result = add_cityfit_features(df)

    expected_columns = {
        "purchasing_power_score",
        "safety_score",
        "healthcare_score",
        "climate_score",
        "affordability_score",
        "housing_affordability_score",
        "low_pollution_score",
        "low_traffic_score",
    }

    assert expected_columns.issubset(result.columns)
    assert "qol_score" not in result.columns
    assert "cityfit_score" not in result.columns


def test_add_cityfit_features_calculates_values_correctly():
    df = pd.DataFrame(
        {
            "cost_of_living_index": [60.0, 90.0],
            "purchasing_power_index": [100.0, 50.0],
            "property_price_to_income_ratio": [8.0, 16.0],
            "safety_index": [80.0, 40.0],
            "healthcare_index": [70.0, 50.0],
            "pollution_index": [25.0, 75.0],
            "climate_index": [85.0, 65.0],
            "traffic_commute_index": [30.0, 60.0],
        }
    )

    result = add_cityfit_features(df)

    assert result.loc[0, "purchasing_power_score"] == 100
    assert result.loc[1, "purchasing_power_score"] == 0

    assert result.loc[0, "safety_score"] == 100
    assert result.loc[1, "safety_score"] == 0

    assert result.loc[0, "healthcare_score"] == 100
    assert result.loc[1, "healthcare_score"] == 0

    assert result.loc[0, "climate_score"] == 100
    assert result.loc[1, "climate_score"] == 0

    assert result.loc[0, "affordability_score"] == 100
    assert result.loc[1, "affordability_score"] == 0

    assert result.loc[0, "housing_affordability_score"] == 100
    assert result.loc[1, "housing_affordability_score"] == 0

    assert result.loc[0, "low_pollution_score"] == 100
    assert result.loc[1, "low_pollution_score"] == 0

    assert result.loc[0, "low_traffic_score"] == 100
    assert result.loc[1, "low_traffic_score"] == 0