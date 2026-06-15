import pandas as pd
import plotly.express as px

import streamlit as st

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