import pandas as pd
import streamlit as st


def normalize_priority(value: int) -> float:
    return value / 5


def render_priority_sidebar() -> dict:
    st.sidebar.header("Your Priorities")

    with st.sidebar.expander("Practical Fit", expanded=True):
        priority_practical_fit_ui = st.slider(
            "Overall influence",
            0,
            10,
            5,
            help="Controls how much this whole category affects CityFit Score.",
            key="priority_practical_fit_overall",
        )
        st.markdown("<div class='priority-section-rule'></div>", unsafe_allow_html=True)

        priority_purchasing_power_ui = st.slider("Purchasing Power", 0, 10, 5)
        priority_low_cost_ui = st.slider("Low Cost of Living", 0, 10, 5)

        priority_safety_ui = st.slider("Safety", 0, 10, 5)
        priority_healthcare_ui = st.slider("Healthcare", 0, 10, 5)

        priority_housing_ui = st.slider("Housing Affordability", 0, 10, 5)

        priority_low_traffic_ui = st.slider("Low Traffic", 0, 10, 5)
        priority_climate_ui = st.slider("Climate", 0, 10, 5)
        priority_low_pollution_ui = st.slider("Low Pollution", 0, 10, 5)

        remote_worker = st.checkbox("I work remotely", value=False)

    with st.sidebar.expander("Lifestyle Fit", expanded=False):
        priority_lifestyle_fit_ui = st.slider(
            "Overall influence",
            0,
            10,
            5,
            help="Controls how much this whole category affects CityFit Score.",
            key="priority_lifestyle_fit_overall",
        )
        st.markdown("<div class='priority-section-rule'></div>", unsafe_allow_html=True)

        priority_daily_life_ui = st.slider("Daily Life", 0, 10, 5)
        priority_food_scene_ui = st.slider("Food Scene", 0, 10, 5)
        priority_culture_ui = st.slider("Culture", 0, 10, 5)
        priority_outdoors_ui = st.slider("Outdoors", 0, 10, 5)
        priority_transit_ui = st.slider("Transit", 0, 10, 5)
        priority_airport_ui = st.slider("Airport Access", 0, 10, 5)
        priority_nightlife_ui = st.slider("Nightlife", 0, 10, 5)

    return {
        "priority_purchasing_power": normalize_priority(priority_purchasing_power_ui),
        "priority_low_cost": normalize_priority(priority_low_cost_ui),
        "priority_safety": normalize_priority(priority_safety_ui),
        "priority_healthcare": normalize_priority(priority_healthcare_ui),
        "priority_housing": normalize_priority(priority_housing_ui),
        "priority_low_traffic": normalize_priority(priority_low_traffic_ui),
        "priority_climate": normalize_priority(priority_climate_ui),
        "priority_low_pollution": normalize_priority(priority_low_pollution_ui),
        "priority_daily_life": normalize_priority(priority_daily_life_ui),
        "priority_food_scene": normalize_priority(priority_food_scene_ui),
        "priority_culture": normalize_priority(priority_culture_ui),
        "priority_outdoors": normalize_priority(priority_outdoors_ui),
        "priority_transit": normalize_priority(priority_transit_ui),
        "priority_airport": normalize_priority(priority_airport_ui),
        "priority_nightlife": normalize_priority(priority_nightlife_ui),
        "priority_practical_fit": normalize_priority(priority_practical_fit_ui),
        "priority_lifestyle_fit": normalize_priority(priority_lifestyle_fit_ui),
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
