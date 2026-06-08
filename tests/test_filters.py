import pandas as pd

from cityfit.features.filters import (
    filter_by_column_value,
    filter_by_country,
    filter_by_region,
)


def make_city_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["Tampa", "Madrid", "Tokyo"],
            "country": ["United States", "Spain", "Japan"],
            "region": ["North America", "Europe", "Asia"],
        }
    )


def test_filter_by_region_filters_case_insensitively():
    df = make_city_filter_df()

    result = filter_by_region(df, "europe")

    assert len(result) == 1
    assert result.iloc[0]["city"] == "Madrid"


def test_filter_by_country_filters_case_insensitively():
    df = make_city_filter_df()

    result = filter_by_country(df, "japan")

    assert len(result) == 1
    assert result.iloc[0]["city"] == "Tokyo"


def test_filter_by_column_value_returns_original_df_when_value_is_none():
    df = make_city_filter_df()

    result = filter_by_column_value(df, "region", None)

    assert len(result) == 3


def test_filter_by_column_value_returns_original_df_when_value_is_all():
    df = make_city_filter_df()

    result = filter_by_column_value(df, "region", "All")

    assert len(result) == 3