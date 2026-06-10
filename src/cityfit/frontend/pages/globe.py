import pandas as pd
import plotly.express as px
import requests
import streamlit as st


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

        .block-container {
            padding-top: 2rem;
        }

        .globe-panel {
            border: 1px solid rgba(255, 255, 255, 0.45);
            border-radius: 18px;
            padding: 0.75rem;
            background: rgba(245, 246, 255, 0.30);
            box-shadow: 0 20px 60px rgba(40, 40, 90, 0.22);
            backdrop-filter: blur(8px);
        }

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
            background: rgba(245, 246, 255, 0.20) !important;
        }

        .metric-table-card td:last-child,
        .metric-table-card th:last-child,
        .metric-table td:last-child,
        .metric-table th:last-child {
            text-align: right !important;
        }

        .metric-table-card tbody tr:last-child td,
        .metric-table tbody tr:last-child td {
            border-bottom: none !important;
        }

        .metric-table-card tbody tr:hover td,
        .metric-table tbody tr:hover td {
            background: rgba(255, 255, 255, 0.35) !important;
        }

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
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]

def load_globe_data(payload: dict) -> pd.DataFrame:
    recommendations = get_recommendations_from_api(
        {
            **payload,
            "top_n": 500,
        }
    )

    df = pd.DataFrame(recommendations)

    return df.dropna(subset=["latitude", "longitude"])

def build_globe_figure(globe_df: pd.DataFrame, all_df: pd.DataFrame):
    global_min_score = all_df["cityfit_score"].min()
    global_max_score = all_df["cityfit_score"].max()

    max_marker_size = 10
    sizeref = 2.0 * global_max_score / (max_marker_size**2)

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
            "numbeo_qol_rank",
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
            "CityFit score: %{customdata[3]:.1f}<br>"
            "CityFit rank: #%{customdata[4]:.0f}<br>"
            "Numbeo rank: #%{customdata[5]:.0f}"
            "<extra></extra>"
        ),
        marker=dict(
            sizeref=sizeref,
            sizemode="area",
            line=dict(width=1, color="white"),
            opacity=0.90,
        ),
    )

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
        projection_rotation=dict(lon=0, lat=20, roll=0),
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
    st.markdown('<div class="globe-panel">', unsafe_allow_html=True)

    selected_event = st.plotly_chart(
        fig,
        width="stretch",
        key="cityfit_globe_chart",
        on_select="rerun",
        selection_mode="points",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    selected_points = selected_event.get("selection", {}).get("points", [])

    if not selected_points:
        return None, None

    selected_custom_data = selected_points[0].get("customdata", [])

    if len(selected_custom_data) < 2:
        return None, None

    return selected_custom_data[0], selected_custom_data[1]

def build_city_metric_table(city: pd.Series) -> pd.DataFrame:
    metric_labels = {
        "cityfit_score": "City Score",
        "purchasing_power_index": "Purchasing power",
        "safety_index": "Safety",
        "healthcare_index": "Healthcare",
        "cost_of_living_index": "Cost of living",
        "property_price_to_income_ratio": "Housing price to income",
        "traffic_commute_index": "Traffic commute",
        "pollution_index": "Pollution",
        "climate_index": "Climate",
    }

    rows = []

    for column, label in metric_labels.items():
        if column in city.index and pd.notna(city[column]):
            rows.append(
                {
                    "Metric": label,
                    "Value": round(float(city[column]), 1),
                }
            )

    return pd.DataFrame(rows)

def render_metric_table(metric_df: pd.DataFrame) -> None:
    rows_html = "".join(
        [
            f"<tr><td>{row['Metric']}</td><td>{row['Value']}</td></tr>"
            for _, row in metric_df.iterrows()
        ]
    )

    table_html = f"""
<div class="metric-table-card">
<table class="metric-table">
<thead>
<tr>
<th>Metric</th>
<th>Value</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>
"""

    st.markdown(table_html, unsafe_allow_html=True)

def render_city_profile(
    globe_df: pd.DataFrame,
    selected_city: str | None,
    selected_country: str | None,
) -> None:
    st.divider()
    st.subheader("City profile")

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

    st.markdown(f"### {city['city']}, {city['country']}")

    col1, col2 = st.columns(2)

    col1.metric("CityFit Score", round(city["cityfit_score"], 1))
    col2.metric("CityFit Rank", f"#{int(city['cityfit_rank'])}")

    st.write(f"**Region:** {city['region']}")

    st.markdown("#### Metric breakdown")

    metric_df = build_city_metric_table(city)

    render_metric_table(metric_df)

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

    fig = build_globe_figure(globe_df, all_df)
    selected_city, selected_country = render_selectable_globe(fig)
    render_city_profile(globe_df, selected_city, selected_country)