from pathlib import Path
from html import unescape
import re

import pandas as pd
import requests

from cityfit.lifestyle.airport_scoring import add_airport_scores, build_route_connectivity


OURAIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
OPENFLIGHTS_ROUTES_URL = (
    "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
)
BUSIEST_AIRPORTS_URL = (
    "https://en.wikipedia.org/wiki/List_of_busiest_airports_by_passenger_traffic"
)
AIRPORTS_CACHE_PATH = Path("data/reference/ourairports_airports.csv")
OPENFLIGHTS_ROUTES_CACHE_PATH = Path("data/reference/openflights_routes.dat")
PASSENGER_VOLUME_CACHE_PATH = Path("data/reference/airport_passenger_volume.csv")
LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")

DIAGNOSTIC_COLUMNS = [
    "nearest_airport_name",
    "nearest_airport_type",
    "nearest_airport_distance_km",
    "airport_distance_score",
    "airport_connectivity_score",
    "airport_passenger_score",
    "airport_direct_destination_count",
    "airport_route_count",
    "airport_annual_passengers",
]


def download_airports(output_path: Path = AIRPORTS_CACHE_PATH) -> None:
    download_url(OURAIRPORTS_URL, output_path)


def download_url(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def load_airports(cache_path: Path = AIRPORTS_CACHE_PATH) -> pd.DataFrame:
    if not cache_path.exists():
        download_airports(cache_path)

    return pd.read_csv(cache_path)


def load_route_connectivity(
    cache_path: Path = OPENFLIGHTS_ROUTES_CACHE_PATH,
) -> pd.DataFrame:
    if not cache_path.exists():
        download_url(OPENFLIGHTS_ROUTES_URL, cache_path)

    routes_df = pd.read_csv(cache_path, header=None)

    return build_route_connectivity(routes_df)


def _clean_number(value: object) -> int | None:
    if pd.isna(value):
        return None

    matches = re.findall(r"[\d,]+", str(value))

    if not matches:
        return None

    return max(int(match.replace(",", "")) for match in matches)


def _extract_airport_codes(value: object) -> tuple[str | None, str | None]:
    if pd.isna(value):
        return None, None

    match = re.search(r"\b([A-Z]{3})/([A-Z]{4})\b", str(value))

    if not match:
        return None, None

    return match.group(1), match.group(2)


def download_passenger_volume(
    output_path: Path = PASSENGER_VOLUME_CACHE_PATH,
) -> None:
    response = requests.get(
        BUSIEST_AIRPORTS_URL,
        headers={"User-Agent": "CityFitAI/0.1 airport-score-updater"},
        timeout=30,
    )
    response.raise_for_status()
    tables = _extract_html_tables(response.text)
    passenger_rows = []

    for table in tables:
        if table.empty:
            continue

        code_column = next(
            (column for column in table.columns if "iata" in column.lower()),
            None,
        )
        passengers_column = next(
            (
                column
                for column in table.columns
                if "passenger" in column.lower()
                and "change" not in column.lower()
                and "rank" not in column.lower()
            ),
            None,
        )

        if code_column is None or passengers_column is None:
            continue

        for _, row in table.iterrows():
            iata_code, gps_code = _extract_airport_codes(row[code_column])
            annual_passengers = _clean_number(row[passengers_column])

            if iata_code and annual_passengers:
                passenger_rows.append(
                    {
                        "airport_code": iata_code,
                        "annual_passengers": annual_passengers,
                        "source": BUSIEST_AIRPORTS_URL,
                    }
                )

            if gps_code and annual_passengers:
                passenger_rows.append(
                    {
                        "airport_code": gps_code,
                        "annual_passengers": annual_passengers,
                        "source": BUSIEST_AIRPORTS_URL,
                    }
                )

        if passenger_rows:
            break

    passenger_volume_df = pd.DataFrame(passenger_rows).drop_duplicates(
        subset=["airport_code"]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    passenger_volume_df.to_csv(output_path, index=False)


def _strip_html(value: str) -> str:
    value = re.sub(r"<sup\b.*?</sup>", "", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<style\b.*?</style>", "", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<.*?>", " ", value, flags=re.DOTALL)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _extract_html_tables(html: str) -> list[pd.DataFrame]:
    tables = []

    for table_match in re.finditer(
        r"<table\b.*?</table>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        table_html = table_match.group(0)

        if "wikitable" not in table_html:
            continue

        rows = []

        for row_match in re.finditer(
            r"<tr\b.*?</tr>",
            table_html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            row_html = row_match.group(0)
            cells = [
                _strip_html(cell_match.group(1))
                for cell_match in re.finditer(
                    r"<t[dh]\b[^>]*>(.*?)</t[dh]>",
                    row_html,
                    flags=re.IGNORECASE | re.DOTALL,
                )
            ]

            if cells:
                rows.append(cells)

        if len(rows) < 2:
            continue

        max_width = max(len(row) for row in rows)
        normalized_rows = [
            row + [""] * (max_width - len(row))
            for row in rows
        ]
        header = normalized_rows[0]
        body = normalized_rows[1:]

        tables.append(pd.DataFrame(body, columns=header))

    return tables


def load_passenger_volume(
    cache_path: Path = PASSENGER_VOLUME_CACHE_PATH,
) -> pd.DataFrame:
    if not cache_path.exists():
        download_passenger_volume(cache_path)

    passenger_volume_df = pd.read_csv(cache_path)

    if len(passenger_volume_df) < 50:
        download_passenger_volume(cache_path)
        passenger_volume_df = pd.read_csv(cache_path)

    return passenger_volume_df


def update_lifestyle_airport_scores(
    lifestyle_path: Path = LIFESTYLE_METRICS_PATH,
    airports_cache_path: Path = AIRPORTS_CACHE_PATH,
    routes_cache_path: Path = OPENFLIGHTS_ROUTES_CACHE_PATH,
    passenger_volume_cache_path: Path = PASSENGER_VOLUME_CACHE_PATH,
) -> pd.DataFrame:
    lifestyle_df = pd.read_csv(lifestyle_path)
    airports_df = load_airports(airports_cache_path)
    route_connectivity_df = load_route_connectivity(routes_cache_path)
    passenger_volume_df = load_passenger_volume(passenger_volume_cache_path)

    scored_df = add_airport_scores(
        lifestyle_df,
        airports_df,
        route_connectivity_df=route_connectivity_df,
        passenger_volume_df=passenger_volume_df,
    )
    scored_df["data_quality"] = scored_df["data_quality"].replace(
        {"not_started": "partial_airport"}
    )
    scored_df["method_version"] = scored_df["method_version"].fillna("free_proxy_v1")

    output_columns = [
        column for column in scored_df.columns if column not in DIAGNOSTIC_COLUMNS
    ]

    scored_df[output_columns].to_csv(lifestyle_path, index=False)

    return scored_df


def main() -> None:
    scored_df = update_lifestyle_airport_scores()

    print(
        "Updated airport scores for "
        f"{len(scored_df)} cities in {LIFESTYLE_METRICS_PATH}."
    )
    print(
        scored_df[
            [
                "city",
                "country",
                "airport_score",
                "nearest_airport_name",
                "nearest_airport_type",
                "nearest_airport_distance_km",
                "airport_direct_destination_count",
                "airport_route_count",
                "airport_annual_passengers",
            ]
        ]
        .sort_values("airport_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
