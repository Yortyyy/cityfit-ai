import time
from urllib.parse import quote

import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_similar_cities_by_metrics_cached(
    globe_df: pd.DataFrame,
    selected_city: str,
    selected_country: str,
    top_n: int = 5,
) -> pd.DataFrame:
    return get_similar_cities_by_metrics_uncached(
        globe_df=globe_df,
        selected_city=selected_city,
        selected_country=selected_country,
        top_n=top_n,
    )


def get_similar_cities_by_metrics_uncached(
    globe_df: pd.DataFrame,
    selected_city: str,
    selected_country: str,
    top_n: int = 5,
) -> pd.DataFrame:
    similarity_columns = [
        "purchasing_power_index",
        "cost_of_living_index",
        "safety_index",
        "healthcare_index",
        "property_price_to_income_ratio",
        "traffic_commute_index",
        "climate_index",
        "pollution_index",
    ]

    available_columns = [
        column
        for column in similarity_columns
        if column in globe_df.columns
    ]

    if not available_columns:
        return pd.DataFrame()

    city_mask = (
        (globe_df["city"] == selected_city)
        & (globe_df["country"] == selected_country)
    )

    comparison_df = globe_df.copy()

    for column in available_columns:
        comparison_df[column] = pd.to_numeric(
            comparison_df[column],
            errors="coerce",
        )

    comparison_df = comparison_df.dropna(subset=available_columns).copy()
    selected_df = comparison_df[city_mask]

    if selected_df.empty:
        return pd.DataFrame()

    mins = comparison_df[available_columns].min()
    maxs = comparison_df[available_columns].max()
    ranges = (maxs - mins).replace(0, 1)

    normalized_df = (comparison_df[available_columns] - mins) / ranges
    normalized_selected = (
        selected_df.iloc[0][available_columns] - mins
    ) / ranges

    comparison_df["similarity_distance"] = (
        (normalized_df - normalized_selected) ** 2
    ).sum(axis=1) ** 0.5

    max_distance = comparison_df["similarity_distance"].max()

    if max_distance == 0:
        comparison_df["similarity_score"] = 100.0
    else:
        comparison_df["similarity_score"] = (
            100 * (1 - comparison_df["similarity_distance"] / max_distance)
        )

    comparison_df["similarity_score"] = pd.to_numeric(
        comparison_df["similarity_score"],
        errors="coerce",
    )

    similar_df = (
        comparison_df[~city_mask]
        .sort_values("similarity_distance")
        .head(top_n)
        .copy()
    )

    similar_df["similarity_score"] = similar_df["similarity_score"].round(0)

    return similar_df


def get_similar_cities_by_metrics(
    globe_df: pd.DataFrame,
    selected_city: str,
    selected_country: str,
    top_n: int = 5,
) -> pd.DataFrame:
    return get_similar_cities_by_metrics_cached(
        globe_df=globe_df,
        selected_city=selected_city,
        selected_country=selected_country,
        top_n=top_n,
    )


def build_similar_city_href(city: str, country: str) -> str:
    nav_token = f"{city}-{country}-{time.time_ns()}".replace(" ", "-")

    return (
        f"?similar_city={quote(str(city), safe='')}"
        f"&similar_country={quote(str(country), safe='')}"
        f"&nav={quote(nav_token, safe='')}"
    )


def render_similar_cities_by_metrics(
    globe_df: pd.DataFrame,
    selected_city: str,
    selected_country: str,
) -> None:
    similar_df = get_similar_cities_by_metrics(
        globe_df=globe_df,
        selected_city=selected_city,
        selected_country=selected_country,
        top_n=5,
    )

    if similar_df.empty:
        return

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="similar-city-section">
            <div class="similar-city-eyebrow">RELATED FITS</div>
            <h4>Similar Cities by Metrics</h4>
            <p>
                These cities have the closest overall metric profile to the
                selected city. Click any match to load its profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    for _, row in similar_df.iterrows():
        city = row["city"]
        country = row["country"]
        rank = int(row["cityfit_rank"])
        score = round(float(row["cityfit_score"]), 1)
        similarity = int(row["similarity_score"])

        city_label = f"{city}, {country}"

        button_label = (
            f"↗ {city_label} · {similarity}% match · #{rank} CityFit · {score} Score"
        )

        href = build_similar_city_href(city, country)

        st.markdown(
            f"""
            <a class="similar-city-link" href="{href}" target="_self">
                {button_label}
            </a>
            """,
            unsafe_allow_html=True,
        )
