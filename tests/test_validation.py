import pandas as pd
import pytest

from cityfit.data.validation import validate_city_metrics


def make_valid_city_metrics_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source_rank": [1, 2],
            "city": ["Tampa", "Madrid"],
            "country": ["United States", "Spain"],
            "numbeo_quality_of_life_index": [175.0, 180.0],
            "purchasing_power_index": [105.0, 72.0],
            "safety_index": [60.0, 72.0],
            "healthcare_index": [68.0, 78.0],
            "cost_of_living_index": [72.0, 61.0],
            "property_price_to_income_ratio": [5.2, 9.8],
            "traffic_commute_index": [34.0, 36.0],
            "pollution_index": [35.0, 32.0],
            "climate_index": [85.0, 91.0],
            "source_url": ["https://example.com", "https://example.com"],
            "source_note": ["sample", "sample"],
        }
    )


def test_validate_city_metrics_accepts_valid_dataframe():
    df = make_valid_city_metrics_df()

    result = validate_city_metrics(df)

    assert result is None


def test_validate_city_metrics_rejects_missing_required_column():
    df = make_valid_city_metrics_df().drop(columns=["city"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_city_metrics(df)


def test_validate_city_metrics_rejects_null_city_or_country():
    df = make_valid_city_metrics_df()
    df.loc[0, "city"] = None

    with pytest.raises(ValueError, match="City and country cannot contain null values"):
        validate_city_metrics(df)


def test_validate_city_metrics_rejects_non_numeric_metric_column():
    df = make_valid_city_metrics_df()
    df["safety_index"] = ["high", "medium"]

    with pytest.raises(ValueError, match="Column must be numeric"):
        validate_city_metrics(df)