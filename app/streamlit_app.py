import streamlit as st
import requests

import pandas as pd

from cityfit.frontend.pages.dashboard import render_dashboard_page
from cityfit.frontend.pages.globe import render_globe_page


API_URL = "http://api:8000"


def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]

st.set_page_config(
    page_title="CityFit AI",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def normalize_priority(value: int) -> float:
    return value / 5


st.sidebar.title("🌎 CityFit AI")

selected_page = st.sidebar.radio(
    "Page",
    ["Globe", "Dashboard"],
)

st.sidebar.header("Your priorities")

priority_purchasing_power_ui = st.sidebar.slider("Purchasing power", 0, 10, 7)
priority_low_cost_ui = st.sidebar.slider("Low cost of living", 0, 10, 3)

priority_safety_ui = st.sidebar.slider("Safety", 0, 10, 8)
priority_healthcare_ui = st.sidebar.slider("Healthcare", 0, 10, 5)

priority_housing_ui = st.sidebar.slider("Housing affordability", 0, 10, 5)

priority_climate_ui = st.sidebar.slider("Climate", 0, 10, 8)
priority_low_pollution_ui = st.sidebar.slider("Low pollution", 0, 10, 7)

remote_worker = st.sidebar.checkbox("I work remotely", value=False)

base_payload = {
    "priority_purchasing_power": normalize_priority(priority_purchasing_power_ui),
    "priority_low_cost": normalize_priority(priority_low_cost_ui),
    "priority_safety": normalize_priority(priority_safety_ui),
    "priority_healthcare": normalize_priority(priority_healthcare_ui),
    "priority_housing": normalize_priority(priority_housing_ui),
    "priority_climate": normalize_priority(priority_climate_ui),
    "priority_low_pollution": normalize_priority(priority_low_pollution_ui),
    "remote_worker": remote_worker,
}

metadata_payload = {
    **base_payload,
    "top_n": 500,
    "region": None,
    "country": None,
}

try:
    all_recommendations = get_recommendations_from_api(metadata_payload)
    all_df = pd.DataFrame(all_recommendations)
except requests.RequestException as exc:
    st.error(f"Could not reach CityFit API: {exc}")
    st.stop()

st.sidebar.header("Filters")

region_options = ["All"] + sorted(all_df["region"].dropna().unique())

selected_region = st.sidebar.selectbox(
    "Region",
    region_options,
)

country_options_df = all_df.copy()

if selected_region != "All":
    country_options_df = country_options_df[
        country_options_df["region"] == selected_region
    ]

country_options = ["All"] + sorted(country_options_df["country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "Country",
    country_options,
)

filtered_payload = {
    **base_payload,
    "region": None if selected_region == "All" else selected_region,
    "country": None if selected_country == "All" else selected_country,
}

if selected_page == "Globe":
    render_globe_page(filtered_payload, all_df)
else:
    render_dashboard_page(filtered_payload, all_df)