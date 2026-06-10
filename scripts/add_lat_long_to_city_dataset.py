import pandas as pd

from cityfit.config import CITY_METRICS_RAW_PATH, CITY_COORDINATES_PATH
from cityfit.features.geo import add_city_coordinates


def main() -> None:
    city_df = pd.read_csv(CITY_METRICS_RAW_PATH)
    coordinates_df = pd.read_csv(CITY_COORDINATES_PATH)

    city_df_with_coordinates = add_city_coordinates(
        city_df=city_df,
        coordinates_df=coordinates_df,
    )

    columns = list(city_df_with_coordinates.columns)

    columns.remove("latitude")
    columns.remove("longitude")

    region_index = columns.index("region")

    columns = (
        columns[: region_index + 1]
        + ["latitude", "longitude"]
        + columns[region_index + 1 :]
    )

    city_df_with_coordinates = city_df_with_coordinates[columns]

    city_df_with_coordinates.to_csv(CITY_METRICS_RAW_PATH, index=False)

    print(f"Added latitude and longitude to {CITY_METRICS_RAW_PATH}")
    print(f"Updated rows: {len(city_df_with_coordinates)}")


if __name__ == "__main__":
    main()