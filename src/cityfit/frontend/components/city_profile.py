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

def build_city_metric_table(city: pd.Series, all_df: pd.DataFrame) -> pd.DataFrame:
    metric_labels = {
        "cityfit_score": "CityFit Score",
        "purchasing_power_index": "Purchasing Power",
        "cost_of_living_index": "Cost of Living",
        "safety_index": "Safety",
        "healthcare_index": "Healthcare",
        "property_price_to_income_ratio": "Housing price to income",
        "traffic_commute_index": "Traffic Commute",
        "climate_index": "Climate",
        "pollution_index": "Pollution",
    }

    lower_is_better_metrics = {
        "cost_of_living_index",
        "property_price_to_income_ratio",
        "traffic_commute_index",
        "pollution_index",
    }

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
                "Value": round(value, 1),
                "Color": get_metric_color(
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
    st.subheader("City Profile")

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

    st.markdown(
        f"""
        <div class="city-profile-title-row">
            <span class="city-profile-title-text">{city_name}, {country}</span>
            <span class="city-profile-flag-box">
                <img
                    src="{flag_url}"
                    class="city-profile-flag-img"
                    alt="{country} flag"
                />
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    col1.metric("CityFit Score", round(city_row["cityfit_score"], 1))
    col2.metric("CityFit Rank", f"#{int(city_row['cityfit_rank'])}")

    st.write(f"**Region:** {city_row['region']}")

    metric_df = build_city_metric_table(city_row, all_df)

    st.markdown("#### Metric Breakdown")

    metric_df = build_city_metric_table(city_row, all_df)

    render_metric_table(metric_df)

    render_similar_cities_by_metrics(
        globe_df=globe_df,
        selected_city=selected_city,
        selected_country=selected_country,
    )