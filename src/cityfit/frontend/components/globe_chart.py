import pandas as pd
import plotly.express as px

import streamlit as st
from cityfit.frontend.components.city_comparison import split_city_label

COMPARISON_BLUE = "rgb(92, 92, 255)"
COMPARISON_BLUE_TRANSLUCENT = "rgba(92, 92, 255, 0.86)"
COMPARISON_LINE_POINTS = 40

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

def get_comparison_cities_df(
    globe_df: pd.DataFrame,
    comparison_city_labels: list[str] | None,
) -> pd.DataFrame:
    if not comparison_city_labels:
        return pd.DataFrame()

    selected_pairs = [
        tuple(split_city_label(city_label))
        for city_label in comparison_city_labels[:2]
    ]

    selected_keys = set(selected_pairs)

    comparison_df = globe_df[
        globe_df.apply(
            lambda row: (row["city"], row["country"]) in selected_keys,
            axis=1,
        )
    ].copy()

    if comparison_df.empty:
        return comparison_df

    order_map = {
        city_country: index
        for index, city_country in enumerate(selected_pairs)
    }

    comparison_df["comparison_order"] = comparison_df.apply(
        lambda row: order_map[(row["city"], row["country"])],
        axis=1,
    )

    return comparison_df.sort_values("comparison_order")

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

def interpolate_lateral_path(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    points: int = COMPARISON_LINE_POINTS,
) -> tuple[list[float], list[float]]:
    lon_delta = end_lon - start_lon

    if lon_delta > 180:
        lon_delta -= 360
    elif lon_delta < -180:
        lon_delta += 360

    denominator = max(points - 1, 1)
    lats = []
    lons = []

    for index in range(points):
        progress = index / denominator
        lat = start_lat + ((end_lat - start_lat) * progress)
        lon = start_lon + (lon_delta * progress)

        if lon > 180:
            lon -= 360
        elif lon < -180:
            lon += 360

        lats.append(lat)
        lons.append(lon)

    return lats, lons


def get_comparison_line_path(comparison_city_df: pd.DataFrame) -> tuple[list[float], list[float]]:
    first_city = comparison_city_df.iloc[0]
    second_city = comparison_city_df.iloc[1]

    return interpolate_lateral_path(
        start_lat=float(first_city["latitude"]),
        start_lon=float(first_city["longitude"]),
        end_lat=float(second_city["latitude"]),
        end_lon=float(second_city["longitude"]),
    )

def add_comparison_city_markers(fig, comparison_city_df: pd.DataFrame):
    if comparison_city_df.empty:
        return fig

    if len(comparison_city_df) == 2:
        line_lats, line_lons = get_comparison_line_path(comparison_city_df)

        fig.add_scattergeo(
            lat=line_lats,
            lon=line_lons,
            mode="lines",
            hoverinfo="skip",
            line=dict(
                width=3,
                color=COMPARISON_BLUE_TRANSLUCENT,
                dash="dot",
            ),
            showlegend=False,
        )

    fig.add_scattergeo(
        lat=comparison_city_df["latitude"],
        lon=comparison_city_df["longitude"],
        mode="markers",
        hoverinfo="skip",
        marker=dict(
            size=20,
            color="rgba(255, 255, 255, 0.10)",
            line=dict(
                width=4,
                color=COMPARISON_BLUE_TRANSLUCENT,
            ),
            symbol="circle",
        ),
        showlegend=False,
    )

    fig.add_scattergeo(
        lat=comparison_city_df["latitude"],
        lon=comparison_city_df["longitude"],
        mode="markers",
        hoverinfo="skip",
        marker=dict(
            size=8,
            color=COMPARISON_BLUE_TRANSLUCENT,
            line=dict(
                width=2,
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
    comparison_city_labels: list[str] | None = None,
    projection_rotation_override: dict | None = None,
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

    comparison_city_df = get_comparison_cities_df(
        globe_df,
        comparison_city_labels,
    )

    if projection_rotation_override is not None:
        projection_rotation = projection_rotation_override
    else:
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

    fig = add_comparison_city_markers(fig, comparison_city_df)
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

def bump_globe_chart_version() -> None:
    st.session_state["globe_chart_version"] = (
        st.session_state.get("globe_chart_version", 0) + 1
    )
