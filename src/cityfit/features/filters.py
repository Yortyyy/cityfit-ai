import pandas as pd


def filter_by_column_value(
    df: pd.DataFrame,
    column: str,
    value: str | None,
) -> pd.DataFrame:
    """Filter a DataFrame by a case-insensitive column value."""
    if not value or value == "All":
        return df

    return df[df[column].fillna("").str.lower() == value.lower()]


def filter_by_region(df: pd.DataFrame, region: str | None) -> pd.DataFrame:
    """Filter cities by region."""
    return filter_by_column_value(df, column="region", value=region)


def filter_by_country(df: pd.DataFrame, country: str | None) -> pd.DataFrame:
    """Filter cities by country."""
    return filter_by_column_value(df, column="country", value=country)