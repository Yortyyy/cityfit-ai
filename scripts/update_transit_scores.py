from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

from cityfit.lifestyle.transit_scoring import (
    TRANSIT_COMPONENTS,
    add_transit_scores,
)


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
LIFESTYLE_METRICS_PATH = Path("data/reference/lifestyle_metrics.csv")
TRANSIT_COUNTS_CACHE_PATH = Path("data/reference/osm_transit_counts.csv")
QUERY_RADIUS_METERS = 8_000

DIAGNOSTIC_COLUMNS = list(TRANSIT_COMPONENTS.keys())


def _count_from_overpass_element(element: dict) -> int:
    tags = element.get("tags", {})

    return int(tags.get("total", 0))


def post_overpass_query(
    query: str,
    session: requests.Session | None = None,
    max_attempts: int = 4,
) -> requests.Response:
    session = session or requests.Session()
    response = None

    for attempt in range(max_attempts):
        url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]

        try:
            response = session.post(
                url,
                data={"data": query},
                headers={"User-Agent": "CityFitAI/0.1 transit-score-updater"},
                timeout=75,
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "15"))
                time.sleep(retry_after + attempt * 5)
                continue

            response.raise_for_status()
            break
        except requests.RequestException:
            if attempt == max_attempts - 1:
                raise

            time.sleep(10 + attempt * 10)

    if response is None:
        raise RuntimeError("Overpass request did not return a response.")

    return response


def build_transit_query(latitude: float, longitude: float) -> str:
    return build_transit_batch_query([(latitude, longitude)])


def _transit_query_blocks(latitude: float, longitude: float) -> list[str]:
    radius = QUERY_RADIUS_METERS

    return [
        f"""(
  node(around:{radius},{latitude},{longitude})["highway"="bus_stop"];
  node(around:{radius},{latitude},{longitude})["public_transport"~"^(platform|stop_position)$"]["bus"];
);
out count;""",
        f"""(
  nwr(around:{radius},{latitude},{longitude})["railway"~"^(station|halt)$"];
  nwr(around:{radius},{latitude},{longitude})["station"~"^(train|railway)$"];
);
out count;""",
        f"""(
  nwr(around:{radius},{latitude},{longitude})["railway"~"^(subway_entrance|tram_stop|light_rail)$"];
  nwr(around:{radius},{latitude},{longitude})["station"~"^(subway|light_rail|tram)$"];
);
out count;""",
        f"""(
  nwr(around:{radius},{latitude},{longitude})["amenity"="ferry_terminal"];
  nwr(around:{radius},{latitude},{longitude})["aerialway"="station"];
);
out count;""",
        f"""(
  nwr(around:{radius},{latitude},{longitude})["amenity"="bus_station"];
  nwr(around:{radius},{latitude},{longitude})["public_transport"="station"];
);
out count;""",
    ]


def build_transit_batch_query(locations: list[tuple[float, float]]) -> str:
    blocks = ["[out:json][timeout:120];"]

    for latitude, longitude in locations:
        blocks.extend(_transit_query_blocks(latitude, longitude))

    return "\n".join(blocks)


def fetch_transit_counts(
    city: str,
    country: str,
    latitude: float,
    longitude: float,
    session: requests.Session | None = None,
) -> dict:
    query = build_transit_query(latitude, longitude)
    response = post_overpass_query(query, session=session)
    payload = response.json()
    count_elements = [
        element for element in payload.get("elements", []) if element.get("type") == "count"
    ]

    if len(count_elements) != len(TRANSIT_COMPONENTS):
        raise ValueError(
            "Unexpected Overpass response: expected "
            f"{len(TRANSIT_COMPONENTS)} count elements, got {len(count_elements)}"
        )

    counts = {
        "city": city,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
        "query_radius_meters": QUERY_RADIUS_METERS,
        "source": response.url,
    }

    for column, element in zip(TRANSIT_COMPONENTS, count_elements):
        counts[column] = _count_from_overpass_element(element)

    return counts


def fetch_transit_counts_batch(
    city_rows: list,
    session: requests.Session | None = None,
) -> list[dict]:
    locations = [
        (float(city_row.latitude), float(city_row.longitude)) for city_row in city_rows
    ]
    query = build_transit_batch_query(locations)
    response = post_overpass_query(query, session=session)
    payload = response.json()
    count_elements = [
        element for element in payload.get("elements", []) if element.get("type") == "count"
    ]
    expected_count = len(city_rows) * len(TRANSIT_COMPONENTS)

    if len(count_elements) != expected_count:
        raise ValueError(
            "Unexpected Overpass response: expected "
            f"{expected_count} count elements, got {len(count_elements)}"
        )

    rows = []
    category_count = len(TRANSIT_COMPONENTS)

    for row_index, city_row in enumerate(city_rows):
        row_counts = count_elements[
            row_index * category_count : (row_index + 1) * category_count
        ]
        counts = {
            "city": city_row.city,
            "country": city_row.country,
            "latitude": float(city_row.latitude),
            "longitude": float(city_row.longitude),
            "query_radius_meters": QUERY_RADIUS_METERS,
            "source": response.url,
        }

        for column, element in zip(TRANSIT_COMPONENTS, row_counts):
            counts[column] = _count_from_overpass_element(element)

        rows.append(counts)

    return rows


def load_cached_counts(cache_path: Path = TRANSIT_COUNTS_CACHE_PATH) -> pd.DataFrame:
    if not cache_path.exists():
        return pd.DataFrame()

    return pd.read_csv(cache_path)


def save_cached_counts(
    counts_df: pd.DataFrame,
    cache_path: Path = TRANSIT_COUNTS_CACHE_PATH,
) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    counts_df.sort_values(["country", "city"]).to_csv(cache_path, index=False)


def collect_transit_counts(
    lifestyle_df: pd.DataFrame,
    cache_path: Path = TRANSIT_COUNTS_CACHE_PATH,
    limit: int | None = None,
    sleep_seconds: float = 1.0,
    batch_size: int = 5,
) -> pd.DataFrame:
    cached_counts = load_cached_counts(cache_path)
    collected_rows = (
        cached_counts.to_dict(orient="records") if not cached_counts.empty else []
    )
    completed_keys = {
        (row["city"], row["country"])
        for row in collected_rows
        if "city" in row and "country" in row
    }
    remaining_df = lifestyle_df[
        ~lifestyle_df[["city", "country"]].apply(tuple, axis=1).isin(completed_keys)
    ].copy()

    if limit is not None:
        remaining_df = remaining_df.head(limit)

    session = requests.Session()
    city_rows = list(remaining_df.itertuples(index=False))

    for batch_start in range(0, len(city_rows), batch_size):
        batch_rows = city_rows[batch_start : batch_start + batch_size]

        try:
            batch_counts = fetch_transit_counts_batch(
                batch_rows,
                session=session,
            )
        except Exception as error:
            print(
                "Batch failed; falling back to one-city requests: "
                f"{type(error).__name__}: {error}"
            )
            batch_counts = [
                fetch_transit_counts(
                    city=city_row.city,
                    country=city_row.country,
                    latitude=float(city_row.latitude),
                    longitude=float(city_row.longitude),
                    session=session,
                )
                for city_row in batch_rows
            ]

        collected_rows.extend(batch_counts)
        save_cached_counts(pd.DataFrame(collected_rows), cache_path)

        print(
            f"{min(batch_start + batch_size, len(city_rows))}/"
            f"{len(city_rows)} transit rows cached"
        )

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return pd.DataFrame(collected_rows)


def update_lifestyle_transit_scores(
    lifestyle_path: Path = LIFESTYLE_METRICS_PATH,
    cache_path: Path = TRANSIT_COUNTS_CACHE_PATH,
    limit: int | None = None,
    sleep_seconds: float = 1.0,
    batch_size: int = 5,
) -> pd.DataFrame:
    lifestyle_df = pd.read_csv(lifestyle_path)
    counts_df = collect_transit_counts(
        lifestyle_df,
        cache_path=cache_path,
        limit=limit,
        sleep_seconds=sleep_seconds,
        batch_size=batch_size,
    )
    scored_df = add_transit_scores(lifestyle_df, counts_df)

    completed_count = counts_df.drop_duplicates(subset=["city", "country"]).shape[0]
    total_count = lifestyle_df.drop_duplicates(subset=["city", "country"]).shape[0]

    if completed_count < total_count:
        print(
            f"Cached transit counts for {completed_count}/{total_count} cities. "
            "Leaving lifestyle_metrics.csv unchanged until all cities are cached."
        )

        return scored_df

    scored_df["data_quality"] = scored_df["data_quality"].replace(
        {
            "not_started": "partial_transit",
            "partial_airport": "partial_transit_airport",
            "partial_daily_life_food_culture_airport": (
                "partial_daily_life_food_culture_transit_airport"
            ),
        }
    )
    scored_df["method_version"] = scored_df["method_version"].fillna("free_proxy_v1")

    output_columns = [
        column for column in scored_df.columns if column not in DIAGNOSTIC_COLUMNS
    ]

    scored_df[output_columns].to_csv(lifestyle_path, index=False)

    return scored_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update transit scores using OpenStreetMap transit counts."
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=5)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scored_df = update_lifestyle_transit_scores(
        limit=args.limit,
        sleep_seconds=args.sleep_seconds,
        batch_size=args.batch_size,
    )
    cached_count = load_cached_counts().drop_duplicates(
        subset=["city", "country"]
    ).shape[0]
    total_count = pd.read_csv(LIFESTYLE_METRICS_PATH).drop_duplicates(
        subset=["city", "country"]
    ).shape[0]

    if cached_count < total_count:
        print(
            f"Preview only: {cached_count}/{total_count} cities cached. "
            "lifestyle_metrics.csv was not rewritten."
        )
    else:
        print(
            "Updated transit scores for "
            f"{scored_df['transit_score'].notna().sum()} cities in "
            f"{LIFESTYLE_METRICS_PATH}."
        )

    print(
        scored_df[["city", "country", "transit_score"]]
        .sort_values("transit_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
