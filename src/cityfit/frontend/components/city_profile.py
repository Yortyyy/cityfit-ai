from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from cityfit.frontend.components.similar_cities import render_similar_cities_by_metrics
from cityfit.utils.countries import get_country_flag_url


def get_metric_color(
    value: float,
    min_value: float,
    max_value: float,
    lower_is_better: bool = False,
) -> str:
    if pd.isna(value) or pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return "rgb(31, 37, 79)"

    normalized = (value - min_value) / (max_value - min_value)
    normalized = max(0.0, min(1.0, normalized))

    if lower_is_better:
        normalized = 1.0 - normalized

    return px.colors.sample_colorscale("RdYlGn", normalized)[0]


def get_housing_to_income_color(value: float) -> str:
    if pd.isna(value):
        return "rgb(31, 37, 79)"

    anchors = [
        (1.0, 1.0),
        (5.0, 0.78),
        (10.0, 0.46),
        (15.0, 0.12),
        (30.0, 0.0),
    ]

    if value <= anchors[0][0]:
        normalized = anchors[0][1]
    elif value >= anchors[-1][0]:
        normalized = anchors[-1][1]
    else:
        normalized = anchors[-1][1]
        for (low_ratio, low_color), (high_ratio, high_color) in zip(
            anchors,
            anchors[1:],
        ):
            if low_ratio <= value <= high_ratio:
                ratio_position = (value - low_ratio) / (high_ratio - low_ratio)
                normalized = low_color + ratio_position * (high_color - low_color)
                break

    return px.colors.sample_colorscale("RdYlGn", normalized)[0]


def get_metric_color_for_column(
    column: str,
    value: float,
    min_value: float,
    max_value: float,
    lower_is_better: bool = False,
) -> str:
    if column == "property_price_to_income_ratio":
        return get_housing_to_income_color(value)

    return get_metric_color(
        value=value,
        min_value=min_value,
        max_value=max_value,
        lower_is_better=lower_is_better,
    )


def build_city_metric_table(city: pd.Series, all_df: pd.DataFrame) -> pd.DataFrame:
    return build_metric_rows(
        city=city,
        all_df=all_df,
        metric_labels={
            "cityfit_rank": "CityFit Rank",
            "cityfit_score": "CityFit Score",
            "practical_score": "Practical Fit",
            "lifestyle_fit_score": "Lifestyle Fit",
        },
        lower_is_better_metrics={"cityfit_rank"},
    )


def build_practical_metric_table(city: pd.Series, all_df: pd.DataFrame) -> pd.DataFrame:
    return build_metric_rows(
        city=city,
        all_df=all_df,
        metric_labels={
            "purchasing_power_index": "Purchasing Power",
            "cost_of_living_index": "Cost of Living",
            "safety_index": "Safety",
            "healthcare_index": "Healthcare",
            "property_price_to_income_ratio": "Housing to Income Ratio",
            "traffic_commute_index": "Traffic",
            "climate_index": "Climate",
            "pollution_index": "Pollution",
        },
        lower_is_better_metrics={
            "cost_of_living_index",
            "property_price_to_income_ratio",
            "traffic_commute_index",
            "pollution_index",
        },
    )


def build_lifestyle_metric_table(city: pd.Series, all_df: pd.DataFrame) -> pd.DataFrame:
    return build_metric_rows(
        city=city,
        all_df=all_df,
        metric_labels={
            "daily_life_score": "Daily Life",
            "food_scene_score": "Food Scene",
            "culture_score": "Culture",
            "outdoors_score": "Outdoors",
            "transit_score": "Transit",
            "airport_score": "Airport Access",
            "nightlife_score": "Nightlife",
        },
    )


def build_metric_rows(
    city: pd.Series,
    all_df: pd.DataFrame,
    metric_labels: dict[str, str],
    lower_is_better_metrics: set[str] | None = None,
) -> pd.DataFrame:
    lower_is_better_metrics = lower_is_better_metrics or set()

    rows = []

    for column, label in metric_labels.items():
        if column not in city.index or column not in all_df.columns:
            continue

        if pd.isna(city[column]):
            continue

        value = float(city[column])
        min_value = float(all_df[column].min())
        max_value = float(all_df[column].max())

        rows.append(
            {
                "Metric": label,
                "Value": (
                    f"#{int(value)}"
                    if column == "cityfit_rank"
                    else round(value, 1)
                ),
                "Color": get_metric_color_for_column(
                    column=column,
                    value=value,
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=column in lower_is_better_metrics,
                ),
            }
        )

    return pd.DataFrame(rows)

def render_metric_table(metric_df: pd.DataFrame) -> None:
    rows_html = ""

    for _, row in metric_df.iterrows():
        rows_html += (
            "<tr>"
            f"<td>{row['Metric']}</td>"
            f"<td class='metric-value-cell' style='--metric-color: {row['Color']};'>"
            f"{row['Value']}"
            "</td>"
            "</tr>"
        )

    table_html = (
        "<div class='metric-table-card'>"
        "<table class='metric-table'>"
        "<thead>"
        "<tr>"
        "<th>Metric</th>"
        "<th>Value</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        f"{rows_html}"
        "</tbody>"
        "</table>"
        "</div>"
    )

    st.markdown(table_html, unsafe_allow_html=True)

def render_city_profile(
    globe_df: pd.DataFrame,
    all_df: pd.DataFrame,
    selected_city: str | None,
    selected_country: str | None,
) -> None:
    st.markdown(
        """
        <div class="city-profile-section-heading">
            <div class="city-profile-eyebrow">SELECTED CITY</div>
            <h2>City Profile</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected_city is None or selected_country is None:
        st.info("Select a city dot on the globe to view its profile.")
        return

    city_matches = globe_df[
        (globe_df["city"] == selected_city)
        & (globe_df["country"] == selected_country)
    ]

    if city_matches.empty:
        st.warning("Selected city was not found in the filtered data.")
        return

    city_row = city_matches.iloc[0]

    city_name = city_row["city"]
    country = city_row["country"]

    flag_url = get_country_flag_url(country, size=160)
    cityfit_score = round(float(city_row["cityfit_score"]), 1)
    cityfit_rank = int(city_row["cityfit_rank"])
    region = city_row["region"]
    city_name_display = escape(str(city_name))
    country_display = escape(str(country))
    region_display = escape(str(region))
    flag_url_display = escape(str(flag_url), quote=True)

    st.markdown(
        f"""
        <div class="city-profile-hero-card">
            <div class="city-profile-title-row">
                <span class="city-profile-title-text">
                    {city_name_display}, {country_display}
                </span>
                <span class="city-profile-flag-box">
                    <img
                        src="{flag_url_display}"
                        class="city-profile-flag-img"
                        alt="{country_display} flag"
                    />
                </span>
            </div>
            <div class="city-profile-summary-row">
                <div class="city-profile-summary-badge">
                    <span>Rank</span>
                    <strong>#{cityfit_rank}</strong>
                </div>
                <div class="city-profile-summary-badge">
                    <span>Score</span>
                    <strong>{cityfit_score}</strong>
                </div>
                <div class="city-profile-summary-badge">
                    <span>Region</span>
                    <strong>{region_display}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        "<h4 class='city-profile-subsection-heading'>Metric Breakdown</h4>",
        unsafe_allow_html=True,
    )

    render_metric_table(build_city_metric_table(city_row, all_df))

    practical_column, lifestyle_column = st.columns(2)

    with practical_column:
        st.markdown(
            "<h4 class='city-profile-subsection-heading city-profile-priority-heading'>Practical Priorities</h4>",
            unsafe_allow_html=True,
        )
        render_metric_table(build_practical_metric_table(city_row, all_df))

    with lifestyle_column:
        st.markdown(
            "<h4 class='city-profile-subsection-heading city-profile-priority-heading'>Lifestyle Priorities</h4>",
            unsafe_allow_html=True,
        )
        render_metric_table(build_lifestyle_metric_table(city_row, all_df))

    if "explanation" in city_row.index and pd.notna(city_row["explanation"]):
        st.markdown(
            "<div class='city-profile-summary-spacer'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h4 class='city-profile-subsection-heading'>CityFit Summary</h4>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="city-profile-summary-copy">
                {escape(str(city_row["explanation"]))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_similar_cities_by_metrics(
        globe_df=globe_df,
        selected_city=selected_city,
        selected_country=selected_country,
    )
