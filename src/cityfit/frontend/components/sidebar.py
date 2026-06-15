import pandas as pd
import streamlit as st


def normalize_priority(value: int) -> float:
    return value / 5


def render_priority_sidebar() -> dict:
    st.sidebar.header("Your Priorities")

    priority_purchasing_power_ui = st.sidebar.slider("Purchasing Power", 0, 10, 5)
    priority_low_cost_ui = st.sidebar.slider("Low Cost of Living", 0, 10, 5)

    priority_safety_ui = st.sidebar.slider("Safety", 0, 10, 5)
    priority_healthcare_ui = st.sidebar.slider("Healthcare", 0, 10, 5)

    priority_housing_ui = st.sidebar.slider("Housing Affordability", 0, 10, 5)

    priority_low_traffic_ui = st.sidebar.slider("Low Traffic", 0, 10, 5)
    priority_climate_ui = st.sidebar.slider("Climate", 0, 10, 5)
    priority_low_pollution_ui = st.sidebar.slider("Low Pollution", 0, 10, 5)

    remote_worker = st.sidebar.checkbox("I work remotely", value=False)

    return {
        "priority_purchasing_power": normalize_priority(priority_purchasing_power_ui),
        "priority_low_cost": normalize_priority(priority_low_cost_ui),
        "priority_safety": normalize_priority(priority_safety_ui),
        "priority_healthcare": normalize_priority(priority_healthcare_ui),
        "priority_housing": normalize_priority(priority_housing_ui),
        "priority_low_traffic": normalize_priority(priority_low_traffic_ui),
        "priority_climate": normalize_priority(priority_climate_ui),
        "priority_low_pollution": normalize_priority(priority_low_pollution_ui),
        "remote_worker": remote_worker,
    }


def render_filter_sidebar(all_df: pd.DataFrame) -> dict:
    st.sidebar.header("Filters")

    region_options = ["All"] + sorted(all_df["region"].dropna().unique())

    selected_region = st.sidebar.selectbox("Region", region_options)

    country_options_df = all_df.copy()

    if selected_region != "All":
        country_options_df = country_options_df[
            country_options_df["region"] == selected_region
        ]

    country_options = ["All"] + sorted(country_options_df["country"].dropna().unique())

    selected_country = st.sidebar.selectbox("Country", country_options)

    return {
        "region": None if selected_region == "All" else selected_region,
        "country": None if selected_country == "All" else selected_country,
    }