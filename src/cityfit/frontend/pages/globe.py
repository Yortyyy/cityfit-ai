import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_URL = "http://api:8000"


def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]


def render_globe_page(payload: dict) -> None:
    st.title("🌎 CityFit Globe")
    st.write("Explore CityFit recommendations across the world.")

    try:
        recommendations = get_recommendations_from_api(
            {
                **payload,
                "top_n": 500,
                "region": None,
                "country": None,
            }
        )
        df = pd.DataFrame(recommendations)
    except requests.RequestException as exc:
        st.error(f"Could not reach CityFit API: {exc}")
        st.stop()

    required_cols = {
        "city",
        "country",
        "region",
        "latitude",
        "longitude",
        "cityfit_score",
    }

    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        st.error(f"Missing columns for globe: {missing_cols}")
        st.stop()

    globe_df = df.dropna(subset=["latitude", "longitude"]).copy()

    fig = px.scatter_geo(
        globe_df,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        hover_data={
            "country": True,
            "region": True,
            "cityfit_score": ":.1f",
            "cityfit_rank": True,
            "latitude": False,
            "longitude": False,
        },
        size="cityfit_score",
        color="cityfit_score",
        projection="orthographic",
        title="CityFit Globe",
    )

    fig.update_geos(
        showland=True,
        showcountries=True,
        showocean=True,
        projection_rotation=dict(lon=0, lat=20, roll=0),
    )

    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, width="stretch")