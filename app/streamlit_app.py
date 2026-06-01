import pandas as pd
import streamlit as st

from cityfit.config import CITYFIT_SCORES_PATH, CITY_FEATURES_PATH
from cityfit.data.load_data import load_city_metrics
from cityfit.data.validation import validate_city_metrics
from cityfit.features.scoring import calculate_cityfit_score, add_cityfit_rank
from cityfit.features.transformations import add_affordability_features


st.set_page_config(
    page_title="CityFit AI",
    page_icon="🌎",
    layout="wide",
)

st.title("🌎 CityFit AI")
st.write(
    "Compare Numbeo's baseline Quality of Life ranking against a personalized "
    "CityFit ranking based on your priorities."
)

st.sidebar.header("Your priorities")

priority_safety = st.sidebar.slider("Safety", 0.0, 2.0, 1.0, 0.1)
priority_healthcare = st.sidebar.slider("Healthcare", 0.0, 2.0, 1.0, 0.1)
priority_climate = st.sidebar.slider("Climate", 0.0, 2.0, 0.8, 0.1)
priority_purchasing_power = st.sidebar.slider("Purchasing power", 0.0, 2.0, 1.0, 0.1)

priority_low_cost = st.sidebar.slider("Low cost of living", 0.0, 2.0, 1.0, 0.1)
priority_housing = st.sidebar.slider("Housing affordability", 0.0, 2.0, 1.0, 0.1)
priority_low_pollution = st.sidebar.slider("Low pollution", 0.0, 2.0, 0.7, 0.1)

remote_worker = st.sidebar.checkbox("I work remotely", value=True)

traffic_weight = 0.03 if remote_worker else 0.10

weights = {
    "numbeo_quality_of_life": 0.15,
    "purchasing_power": 0.20 * priority_purchasing_power,
    "safety": 0.20 * priority_safety,
    "healthcare": 0.10 * priority_healthcare,
    "climate": 0.10 * priority_climate,
    "cost_penalty": 0.20 * priority_low_cost,
    "housing_penalty": 0.15 * priority_housing,
    "pollution_penalty": 0.07 * priority_low_pollution,
    "traffic_penalty": traffic_weight,
}


@st.cache_data
def load_and_score_data(weights: dict) -> pd.DataFrame:
    raw_df = load_city_metrics()
    validate_city_metrics(raw_df)

    features_df = add_affordability_features(raw_df)
    scored_df = calculate_cityfit_score(features_df, weights)
    ranked_df = add_cityfit_rank(scored_df)

    return ranked_df


df = load_and_score_data(weights)

st.subheader("Top CityFit recommendations")

top_n = st.slider("Number of cities to show", 5, 50, 15)

display_cols = [
    "city",
    "country",
    "numbeo_qol_rank",
    "cityfit_rank",
    "rank_difference",
    "numbeo_quality_of_life_index",
    "cityfit_score",
    "cost_of_living_index",
    "purchasing_power_index",
    "safety_index",
    "healthcare_index",
    "pollution_index",
    "climate_index",
]

st.dataframe(
    df[display_cols].head(top_n),
    use_container_width=True,
)

st.subheader("Rank movement")

st.write(
    "Positive rank difference means the city ranks better in your personalized "
    "CityFit score than in Numbeo's baseline Quality of Life ranking."
)

rank_movers = (
    df[display_cols]
    .sort_values("rank_difference", ascending=False)
    .head(10)
)

st.dataframe(rank_movers, use_container_width=True)

st.subheader("Compare specific cities")

city_options = sorted(df["city"].unique())
selected_cities = st.multiselect(
    "Choose cities to compare",
    options=city_options,
    default=[city for city in ["Tampa", "Miami", "New York", "Tokyo", "Madrid"] if city in city_options],
)

if selected_cities:
    comparison_df = df[df["city"].isin(selected_cities)][display_cols].sort_values("cityfit_rank")
    st.dataframe(comparison_df, use_container_width=True)

st.caption(
    "Data note: This app uses a small educational sample derived from Numbeo city ranking pages. "
    "Numbeo data is credited to Numbeo.com and is not covered by this repository's code license."
)