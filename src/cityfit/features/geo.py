import pandas as pd


def add_city_coordinates(
    city_df: pd.DataFrame,
    coordinates_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add latitude and longitude to city records.

    Joins on city, state, and country when state exists in both datasets.
    Otherwise joins on city and country.
    """
    coordinates_df = coordinates_df.copy()
    city_df = city_df.copy()

    # Support alternate coordinate column names
    coordinates_df = coordinates_df.rename(
        columns={
            "lat": "latitude",
            "lng": "longitude",
            "lon": "longitude",
        }
    )

    required_city_columns = {"city", "country"}
    required_coordinate_columns = {"city", "country", "latitude", "longitude"}

    missing_city_columns = required_city_columns - set(city_df.columns)
    missing_coordinate_columns = required_coordinate_columns - set(coordinates_df.columns)

    if missing_city_columns:
        raise ValueError(f"City dataset is missing columns: {missing_city_columns}")

    if missing_coordinate_columns:
        raise ValueError(
            f"Coordinates dataset is missing columns: {missing_coordinate_columns}"
        )

    # If the main city file already has old lat/long columns, remove them before merging
    city_df = city_df.drop(columns=["latitude", "longitude"], errors="ignore")

    join_columns = ["city", "country"]

    if "state" in city_df.columns and "state" in coordinates_df.columns:
        join_columns = ["city", "state", "country"]

    merged = city_df.merge(
        coordinates_df[join_columns + ["latitude", "longitude"]],
        on=join_columns,
        how="left",
    )

    missing_coordinates = merged[
        merged["latitude"].isna() | merged["longitude"].isna()
    ]

    if not missing_coordinates.empty:
        missing = missing_coordinates[join_columns].drop_duplicates()
        raise ValueError(
            "Missing coordinates for cities:\n"
            + missing.to_string(index=False)
        )

    return merged