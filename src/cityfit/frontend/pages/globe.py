import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from cityfit.utils.countries import get_country_flag_url


API_URL = "http://api:8000"


def render_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 20% 10%, rgba(255,255,255,0.85), transparent 28%),
                radial-gradient(circle at 80% 30%, rgba(90,90,180,0.28), transparent 30%),
                linear-gradient(135deg, #eef0fa 0%, #c8c6eb 45%, #9ea4d9 100%);
        }

        .block-container {
            padding-top: 2rem;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.08) 50%, rgba(0,0,0,0.035) 50%);
            background-size: 100% 4px;
            mix-blend-mode: soft-light;
            opacity: 0.35;
            z-index: 999999;
        }

        /* ========================= */
        /* SIDEBAR */
        /* ========================= */

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 20% 10%, rgba(255,255,255,0.16), transparent 28%),
                linear-gradient(180deg, rgba(105, 108, 176, 0.94), rgba(64, 68, 132, 0.94)) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.28) !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: rgba(245, 246, 255, 0.96) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: rgba(245, 246, 255, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.38) !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
            color: rgba(245, 246, 255, 0.96) !important;
            background-color: transparent !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span {
            color: rgba(245, 246, 255, 0.96) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {
            fill: rgba(245, 246, 255, 0.96) !important;
            color: rgba(245, 246, 255, 0.96) !important;
        }

        /* ========================= */
        /* CITY SEARCH SELECTBOX ONLY */
        /* ========================= */

        /* Widget wrapper generated from key="city_search_selectbox" */
        .st-key-city_search_selectbox {
            position: relative !important;
            max-width: 100% !important;
            margin-top: 1.25rem !important;
            margin-bottom: 1.25rem !important;
        }

        /* Actual visible selectbox surface */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div {
            min-height: 44px !important;
            height: 44px !important;
            border-radius: 999px !important;
            padding-left: 3rem !important;

            background:
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%231f254f' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'%3E%3C/circle%3E%3Cline x1='16.5' y1='16.5' x2='21' y2='21'%3E%3C/line%3E%3C/svg%3E") 1.05rem center / 18px 18px no-repeat,
                linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.85) 18%,
                    rgba(255, 255, 255, 0.28) 38%,
                    transparent 58%
                ) 3rem 0.35rem / calc(100% - 5.8rem) 10px no-repeat,
                linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.88) 0%,
                    rgba(238, 241, 255, 0.58) 45%,
                    rgba(178, 185, 235, 0.42) 100%
                ) !important;

            border: 1px solid rgba(255, 255, 255, 0.95) !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -16px 28px rgba(85, 95, 175, 0.24),
                0 18px 42px rgba(35, 40, 100, 0.24),
                0 0 0 1px rgba(90, 105, 190, 0.16) !important;

            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
        }

        /* Force BaseWeb inner layers transparent */
        .st-key-city_search_selectbox div[data-baseweb="select"],
        .st-key-city_search_selectbox div[data-baseweb="select"] > div > div,
        .st-key-city_search_selectbox div[data-baseweb="select"] input {
            background-color: transparent !important;
        }

        /* Placeholder / selected text */
        .st-key-city_search_selectbox div[data-baseweb="select"] div,
        .st-key-city_search_selectbox div[data-baseweb="select"] span,
        .st-key-city_search_selectbox div[data-baseweb="select"] input {
            color: #1f254f !important;
            font-weight: 750 !important;
            font-size: 0.95rem !important;
        }

        /* Hover glow */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div:hover {
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -16px 28px rgba(85, 95, 175, 0.28),
                0 22px 52px rgba(35, 40, 100, 0.30),
                0 0 0 3px rgba(120, 140, 255, 0.20) !important;
        }

        /* Dropdown arrow */
        .st-key-city_search_selectbox svg {
            color: #1f254f !important;
            fill: #1f254f !important;
        }

        /* ========================= */
        /* HERO TITLE */
        /* ========================= */

        .hero-title .eyebrow {
            font-size: 0.78rem;
            letter-spacing: 0.22rem;
            color: rgba(30, 40, 80, 0.7);
            font-weight: 700;
        }

        .hero-title h1 {
            font-size: 3rem;
            margin-bottom: 0.25rem;
            color: #1f254f;
            text-shadow: 2px 2px 0 rgba(255,255,255,0.7);
        }

        .hero-title p {
            color: rgba(20, 25, 55, 0.75);
            font-size: 1.05rem;
        }

        .city-profile-title {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: 2rem;
            font-weight: 500;
            color: #0f2354;
            margin-top: 1.25rem;
            margin-bottom: 1.25rem;
        }

        .city-profile-flag {
            width: 45px;
            height: auto;
            box-shadow: 0 2px 2px rgba(15, 35, 84, 0.16);
            transform: translateY(2px);
        }

        /* ========================= */
        /* METRIC TABLE */
        /* ========================= */

        .metric-table-card {
            margin-top: 1rem !important;
            border-radius: 18px !important;
            overflow: hidden !important;
            background: rgba(245, 246, 255, 0.45) !important;
            border: 1px solid rgba(255, 255, 255, 0.65) !important;
            box-shadow: 0 18px 45px rgba(40, 40, 90, 0.18) !important;
            backdrop-filter: blur(8px) !important;
        }

        .metric-table-card table,
        .metric-table {
            width: 100% !important;
            border-collapse: collapse !important;
            background: transparent !important;
            color: #1f254f !important;
        }

        .metric-table-card thead,
        .metric-table thead {
            background: rgba(255, 255, 255, 0.45) !important;
        }

        .metric-table-card th,
        .metric-table th {
            text-align: left !important;
            padding: 0.9rem 1rem !important;
            font-weight: 800 !important;
            color: rgba(31, 37, 79, 0.82) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.65) !important;
            background: rgba(255, 255, 255, 0.35) !important;
        }

        .metric-table-card td,
        .metric-table td {
            padding: 0.85rem 1rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.38) !important;
            font-weight: 650 !important;
            color: #1f254f !important;
        }

        .metric-table-card td.metric-value-cell,
        .metric-table td.metric-value-cell {
            color: var(--metric-color) !important;
            background: rgba(245, 246, 255, 0.20) !important;
            font-size: 1.05rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.02em !important;
            font-variant-numeric: tabular-nums !important;
            text-shadow:
                1px 1px 0 color-mix(in srgb, var(--metric-color) 55%, #1f254f),
                2px 2px 1px rgba(31, 37, 79, 0.22) !important;
        }

        .metric-table-card td:last-child,
        .metric-table-card th:last-child,
        .metric-table td:last-child,
        .metric-table th:last-child {
            text-align: right !important;
        }

        .metric-table-card tbody tr,
        .metric-table tbody tr {
            background: rgba(245, 246, 255, 0.20) !important;
        }

        .metric-table-card tbody tr:hover td:not(.metric-value-cell),
        .metric-table tbody tr:hover td:not(.metric-value-cell) {
            background: rgba(255, 255, 255, 0.35) !important;
        }

        .metric-table-card tbody tr:hover td.metric-value-cell,
        .metric-table tbody tr:hover td.metric-value-cell {
            color: var(--metric-color) !important;
            background: rgba(255, 255, 255, 0.35) !important;
        }

        /* ========================= */
        /* GLOBAL TEXT / METRICS */
        /* ========================= */

        .hero-title,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMetric"],
        [data-testid="stMetric"] * {
            color: #1f254f !important;
        }

        [data-testid="stMetricLabel"] {
            color: rgba(31, 37, 79, 0.72) !important;
        }

        [data-testid="stMetricValue"] {
            color: #1f254f !important;
        }

        /* Make the search placeholder text softer */
        .st-key-city_search_selectbox div[data-baseweb="select"] input::placeholder {
            color: rgba(31, 37, 79, 0.45) !important;
            opacity: 1 !important;
            font-weight: 600 !important;
        }

        /* Sometimes Streamlit/BaseWeb renders the placeholder as a div/span instead */
        .st-key-city_search_selectbox div[data-baseweb="select"] div,
        .st-key-city_search_selectbox div[data-baseweb="select"] span {
            color: rgba(31, 37, 79, 0.50) !important;
        }

        /* Vertically center selected city text inside the search bar */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div {
            display: flex !important;
            align-items: center !important;
        }

        /* Center the selected value / placeholder container */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div > div {
            display: flex !important;
            align-items: center !important;
            min-height: 100% !important;
        }

        /* Center the actual text input/value */
        .st-key-city_search_selectbox div[data-baseweb="select"] input,
        .st-key-city_search_selectbox div[data-baseweb="select"] span,
        .st-key-city_search_selectbox div[data-baseweb="select"] div {
            line-height: 1.1 !important;
        }

        /* Nudge the value down slightly if it still sits high */
        .st-key-city_search_selectbox div[data-baseweb="select"] div[role="combobox"] {
            transform: translateY(1px) !important;
        }

        /* Remove leftover top spacing */
        .block-container {
            padding-top: 1rem !important;
        }

        /* ========================= */
        /* SIMILAR CITY CARDS */
        /* ========================= */

        .similar-city-section {
            margin-top: 1.75rem;
            margin-bottom: 0.65rem;
        }

        .similar-city-section h4 {
            margin-bottom: 0.25rem;
            color: #1f254f;
            font-size: 1.35rem;
            font-weight: 850;
        }

        .similar-city-section p {
            margin-top: 0;
            margin-bottom: 0.75rem;
            color: rgba(31, 37, 79, 0.62);
            font-size: 0.95rem;
        }

        div[data-testid="stButton"] {
            margin-bottom: 0.55rem !important;
        }

        div[data-testid="stButton"] > button {
            position: relative !important;
            border-radius: 16px !important;
            border: 1px solid rgba(55, 65, 130, 0.22) !important;
            border-left: 5px solid rgba(70, 95, 190, 0.72) !important;

            background:
                linear-gradient(
                    90deg,
                    rgba(224, 230, 255, 0.96) 0%,
                    rgba(246, 248, 255, 0.90) 42%,
                    rgba(238, 242, 255, 0.76) 100%
                ) !important;

            color: #1f254f !important;
            min-height: 3.15rem !important;
            padding: 0.55rem 1rem !important;
            font-weight: 750 !important;
            letter-spacing: 0.005em !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.92),
                0 8px 18px rgba(35, 40, 100, 0.12) !important;

            transition:
                transform 0.16s ease,
                box-shadow 0.16s ease,
                border-color 0.16s ease,
                background 0.16s ease !important;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: rgba(55, 65, 130, 0.34) !important;
            border-left-color: rgba(31, 37, 79, 0.95) !important;

            background:
                linear-gradient(
                    90deg,
                    rgba(213, 222, 255, 1) 0%,
                    rgba(250, 251, 255, 0.98) 45%,
                    rgba(236, 241, 255, 0.92) 100%
                ) !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                0 14px 30px rgba(35, 40, 100, 0.18),
                0 0 0 3px rgba(90, 110, 210, 0.12) !important;

            transform: translateY(-1px);
        }

        div[data-testid="stButton"] > button:active {
            transform: translateY(0);
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                0 7px 16px rgba(35, 40, 100, 0.13) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]

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

def load_globe_data(payload: dict) -> pd.DataFrame:
    recommendations = get_recommendations_from_api(
        {
            **payload,
            "top_n": 500,
        }
    )

    df = pd.DataFrame(recommendations)

    return df.dropna(subset=["latitude", "longitude"])

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
        return dict(lon=0, lat=20, roll=0)

    selected_row = selected_city_df.iloc[0]

    return dict(
        lon=float(selected_row["longitude"]),
        lat=float(selected_row["latitude"]),
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

def get_similar_cities_by_metrics(
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

        if st.button(
            button_label,
            key=f"similar_city_{city}_{country}",
            use_container_width=True,
        ):
            set_active_city(
                city=city,
                country=country,
                source="similar_city",
            )

            set_focused_city(
                city=city,
                country=country,
            )

            bump_globe_chart_version()

            st.rerun()

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

    city = city_matches.iloc[0]

    country = city['country']

    flag_url = get_country_flag_url(country)

    flag_html = ""
    if flag_url:
        flag_html = (
            f'<img class="city-profile-flag" '
            f'src="{flag_url}" '
            f'alt="{country} flag">'
        )

    st.markdown(
        f"""
        <div class="city-profile-title">
            <span>{city['city']}, {country}</span>
            {flag_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    col1.metric("CityFit Score", round(city["cityfit_score"], 1))
    col2.metric("CityFit Rank", f"#{int(city['cityfit_rank'])}")

    st.write(f"**Region:** {city['region']}")

    st.markdown("#### Metric Breakdown")

    metric_df = build_city_metric_table(city, all_df)

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
    render_css()

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

        if active_source == "globe":
            restore_focused_city_as_active()
            bump_globe_chart_version()
            st.rerun()

    profile_city = st.session_state.get("active_city")
    profile_country = st.session_state.get("active_country")

    render_city_profile(globe_df, all_df, profile_city, profile_country)