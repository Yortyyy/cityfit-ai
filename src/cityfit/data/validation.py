import pandas as pd

from cityfit.data.schemas import REQUIRED_CITY_COLUMNS


def validate_city_metrics(df: pd.DataFrame) -> None:
    """Validate required columns and basic data quality rules."""
    missing_columns = [col for col in REQUIRED_CITY_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df[["city", "country", "region"]].isna().any().any():
        raise ValueError("City, country, and region cannot contain null values.")

    numeric_columns = [
        "numbeo_quality_of_life_index",
        "purchasing_power_index",
        "safety_index",
        "healthcare_index",
        "cost_of_living_index",
        "property_price_to_income_ratio",
        "traffic_commute_index",
        "pollution_index",
        "climate_index",
    ]

    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column must be numeric: {col}")