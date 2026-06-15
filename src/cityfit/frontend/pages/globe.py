import time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from urllib.parse import quote

from cityfit.frontend.api import get_recommendations_from_api
from cityfit.frontend.components.styles import render_globe_styles
from cityfit.utils.countries import get_country_flag_url

def apply_similar_city_query_navigation() -> None:
    query_city = st.query_params.get("similar_city")
    query_country = st.query_params.get("similar_country")
    query_nav = st.query_params.get("nav")

    if not query_city or not query_country or not query_nav:
        return

    last_applied_nav = st.session_state.get("last_applied_query_nav")

    if query_nav == last_applied_nav:
        st.query_params.clear()
        return

    set_active_city(
        city=query_city,
        country=query_country,
        source="similar_city",
    )

    set_focused_city(
        city=query_city,
        country=query_country,
    )

    bump_globe_chart_version()

    city_label = f"{query_city}, {query_country}"

    st.session_state["pending_city_search_label"] = city_label
    st.session_state["skip_globe_selection_once"] = True
    st.session_state["skip_search_once"] = True
    st.session_state["last_applied_query_nav"] = query_nav
    st.session_state["last_city_search_label"] = city_label

    st.query_params.clear()

def render_city_search(globe_df: pd.DataFrame) -> tuple[str | None, str | None]:
    city_options_df = (
        globe_df[["city", "country"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["city", "country"])
    )

    city_options = [
        f"{row.city}, {row.country}"
        for row in city_options_df.itertuples(index=False)
    ]

    pending_city_label = st.session_state.pop(
        "pending_city_search_label",
        None,
    )

    if pending_city_label in city_options:
        st.session_state["city_search_selectbox"] = pending_city_label

    selected_city_label = st.selectbox(
        "Search for a city",
        city_options,
        index=None,
        placeholder="Search for a city...",
        key="city_search_selectbox",
        label_visibility="collapsed",
    )

    if selected_city_label is None:
        return None, None

    selected_city, selected_country = selected_city_label.rsplit(", ", 1)

    return selected_city, selected_country

@st.cache_data(ttl=300)
def load_globe_data_cached(payload_key: tuple) -> pd.DataFrame:
    payload = dict(payload_key)

    recommendations = get_recommendations_from_api(
        {
            **payload,
            "top_n": 500,
        }
    )

    df = pd.DataFrame(recommendations)

    return df.dropna(subset=["latitude", "longitude"])


def load_globe_data(payload: dict) -> pd.DataFrame:
    payload_key = tuple(sorted(payload.items()))
    return load_globe_data_cached(payload_key)

def get_selected_city_df(
    globe_df: pd.DataFrame,
    selected_city: str | None,
    selected_country: str | None,
) -> pd.DataFrame:
    if selected_city is None or selected_country is None:
        return pd.DataFrame()

    return globe_df[
        (globe_df["city"] == selected_city)
        & (globe_df["country"] == selected_country)
    ]

def get_projection_rotation(selected_city_df: pd.DataFrame) -> dict:
    if selected_city_df.empty:
        return dict(lon=0, lat=15, roll=0)

    selected_row = selected_city_df.iloc[0]

    selected_lon = float(selected_row["longitude"])
    selected_lat = float(selected_row["latitude"])

    safe_lat = selected_lat

    if selected_lat > 30:
        safe_lat = 30 + (selected_lat - 30) * 0.25
    elif selected_lat < -30:
        safe_lat = -30 + (selected_lat + 30) * 0.25

    safe_lat = max(min(safe_lat, 38), -38)

    return dict(
        lon=selected_lon,
        lat=safe_lat,
        roll=0,
    )

def add_selected_city_marker(fig, selected_city_df: pd.DataFrame):
    if selected_city_df.empty:
        return fig

    # Outer highlight ring
    fig.add_scattergeo(
        lat=selected_city_df["latitude"],
        lon=selected_city_df["longitude"],
        mode="markers",
        hoverinfo="skip",
        marker=dict(
            size=24,
            color="rgba(255, 255, 255, 0.20)",
            line=dict(
                width=4,
                color="rgba(31, 37, 79, 0.95)",
            ),
            symbol="circle",
        ),
        showlegend=False,
    )

    # Inner selected dot
    fig.add_scattergeo(
        lat=selected_city_df["latitude"],
        lon=selected_city_df["longitude"],
        mode="markers",
        hoverinfo="skip",
        marker=dict(
            size=10,
            color="rgb(255, 255, 255)",
            line=dict(
                width=3,
                color="rgb(31, 37, 79)",
            ),
            symbol="circle",
        ),
        showlegend=False,
    )

    return fig

def build_globe_figure(
    globe_df: pd.DataFrame,
    all_df: pd.DataFrame,
    focused_city: str | None = None,
    focused_country: str | None = None,
):
    global_min_score = all_df["cityfit_score"].min()
    global_max_score = all_df["cityfit_score"].max()

    max_marker_size = 10
    sizeref = 2.0 * global_max_score / (max_marker_size**2)

    focused_city_df = get_selected_city_df(
        globe_df,
        focused_city,
        focused_country,
    )

    projection_rotation = get_projection_rotation(focused_city_df)

    fig = px.scatter_geo(
        globe_df,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        custom_data=[
            "city",
            "country",
            "region",
            "cityfit_score",
            "cityfit_rank",
        ],
        size="cityfit_score",
        size_max=max_marker_size,
        color="cityfit_score",
        range_color=(global_min_score, global_max_score),
        color_continuous_scale=[
            "rgb(190, 235, 190)",
            "rgb(70, 180, 105)",
            "rgb(0, 95, 65)",
        ],
        projection="orthographic",
        title="CityFit Globe",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]} · %{customdata[2]}<br><br>"
            "CityFit Score: %{customdata[3]:.1f}<br>"
            "CityFit Rank: #%{customdata[4]:.0f}<br>"
            "<extra></extra>"
        ),
        marker=dict(
            sizeref=sizeref,
            sizemode="area",
            line=dict(width=1, color="white"),
            opacity=0.90,
        ),
    )

    fig = add_selected_city_marker(fig, focused_city_df)

    fig.update_geos(
        showland=True,
        landcolor="rgb(215, 220, 230)",
        showcountries=True,
        countrycolor="rgba(40, 40, 80, 0.45)",
        showocean=True,
        oceancolor="rgb(188, 190, 230)",
        showlakes=True,
        lakecolor="rgb(188, 190, 230)",
        bgcolor="rgba(0,0,0,0)",
        projection_rotation=projection_rotation,
    )

    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="CityFit Globe",
            font=dict(
                color="#1f254f",
                size=18,
            ),
            x=0.01,
            xanchor="left",
        ),
        hoverlabel=dict(
            bgcolor="rgba(245, 246, 255, 0.95)",
            bordercolor="rgba(31, 37, 79, 0.35)",
            font=dict(color="#1f254f"),
        ),
    )

    return fig

def render_selectable_globe(fig) -> tuple[str | None, str | None]:
    selected_event = st.plotly_chart(
        fig,
        width="stretch",
        key=f"cityfit_globe_chart_{st.session_state.get('globe_chart_version', 0)}",
        on_select="rerun",
        selection_mode="points",
    )

    selected_points = selected_event.get("selection", {}).get("points", [])

    if not selected_points:
        return None, None

    selected_custom_data = selected_points[0].get("customdata", [])

    if len(selected_custom_data) < 2:
        return None, None

    return selected_custom_data[0], selected_custom_data[1]

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

# Wrapper
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
            <h4>Similar Cities by Metrics</h4>
            <p>Click a city to load its profile.</p>
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

def bump_globe_chart_version() -> None:
    st.session_state["globe_chart_version"] = (
        st.session_state.get("globe_chart_version", 0) + 1
    )


def restore_focused_city_as_active() -> None:
    focused_city = st.session_state.get("focused_city")
    focused_country = st.session_state.get("focused_country")

    if focused_city is not None and focused_country is not None:
        set_active_city(
            city=focused_city,
            country=focused_country,
            source="focused",
        )
    else:
        clear_active_city()

def set_active_city(
    city: str | None,
    country: str | None,
    source: str,
) -> None:
    if city is None or country is None:
        return

    st.session_state["active_city"] = city
    st.session_state["active_country"] = country
    st.session_state["active_city_source"] = source


def set_focused_city(
    city: str | None,
    country: str | None,
) -> None:
    if city is None or country is None:
        return

    st.session_state["focused_city"] = city
    st.session_state["focused_country"] = country


def clear_active_city() -> None:
    st.session_state.pop("active_city", None)
    st.session_state.pop("active_country", None)
    st.session_state.pop("active_city_source", None)


def clear_focused_city() -> None:
    st.session_state.pop("focused_city", None)
    st.session_state.pop("focused_country", None)

def render_globe_page(payload: dict, all_df: pd.DataFrame) -> None:
    render_globe_styles()

    st.markdown(
        """
        <div class="hero-title">
            <div class="eyebrow">CITYFIT AI</div>
            <h1>Explore your best-fit cities</h1>
            <p>Filter cities by region and country, then select a globe marker to inspect a city.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    apply_similar_city_query_navigation()

    try:
        globe_df = load_globe_data(payload)
    except requests.RequestException as exc:
        st.error(f"Could not reach CityFit API: {exc}")
        st.stop()

    if globe_df.empty:
        st.warning("No cities found for the selected filters.")
        return

    previous_search_label = st.session_state.get("last_city_search_label")

    searched_city, searched_country = render_city_search(globe_df)

    current_search_label = None
    if searched_city is not None and searched_country is not None:
        current_search_label = f"{searched_city}, {searched_country}"

    skip_search_once = st.session_state.pop("skip_search_once", False)

    if not skip_search_once:
        search_changed = (
            current_search_label is not None
            and current_search_label != previous_search_label
        )

        search_cleared = (
            current_search_label is None
            and previous_search_label is not None
        )

        if search_changed:
            set_active_city(
                city=searched_city,
                country=searched_country,
                source="search",
            )

            set_focused_city(
                city=searched_city,
                country=searched_country,
            )

            bump_globe_chart_version()

        elif search_cleared:
            clear_active_city()
            clear_focused_city()

            st.session_state.pop("ignore_next_empty_globe_selection", None)
            st.session_state.pop("ignore_next_globe_click", None)

            bump_globe_chart_version()

    st.session_state["last_city_search_label"] = current_search_label

    focused_city = st.session_state.get("focused_city")
    focused_country = st.session_state.get("focused_country")

    fig = build_globe_figure(
        globe_df,
        all_df,
        focused_city,
        focused_country,
    )

    clicked_city, clicked_country = render_selectable_globe(fig)

    skip_globe_selection_once = st.session_state.pop(
        "skip_globe_selection_once",
        False,
    )

    if skip_globe_selection_once:
        clicked_city = None
        clicked_country = None

    if clicked_city is not None and clicked_country is not None:
        clicked_label = f"{clicked_city}, {clicked_country}"

        active_city = st.session_state.get("active_city")
        active_country = st.session_state.get("active_country")
        active_source = st.session_state.get("active_city_source")

        active_label = None
        if active_city is not None and active_country is not None:
            active_label = f"{active_city}, {active_country}"

        if clicked_label == active_label and active_source == "globe":
            restore_focused_city_as_active()
            bump_globe_chart_version()
            st.rerun()

        elif clicked_label != active_label:
            set_active_city(
                city=clicked_city,
                country=clicked_country,
                source="globe",
            )

            # Do not set focused city here.
            # Do not rerun here.

    else:
        active_source = st.session_state.get("active_city_source")

        if active_source == "globe" and not skip_globe_selection_once:
            restore_focused_city_as_active()
            bump_globe_chart_version()
            st.rerun()

    profile_city = st.session_state.get("active_city")
    profile_country = st.session_state.get("active_country")

    render_city_profile(globe_df, all_df, profile_city, profile_country)
