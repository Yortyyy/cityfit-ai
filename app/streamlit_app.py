import pandas as pd
import streamlit as st

import plotly.express as px

import requests


API_URL = "http://api:8000"

st.set_page_config(
    page_title="CityFit AI",
    page_icon="🌎",
    layout="wide",
)

# Chat emoji align with headers
st.markdown(
    """
    <style>
    div[data-testid="stChatMessage"] {
        align-items: flex-start;
    }

    div[data-testid="stChatMessage"] div[data-testid="stAvatar"] {
        margin-top: 0.55rem;
    }

    div[data-testid="stChatMessage"] h2 {
        margin-top: 0;
        padding-top: 0;
        line-height: 1.15;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌎 CityFit AI")
st.write(
    "Compare Numbeo's baseline Quality of Life ranking against a personalized "
    "CityFit ranking based on your priorities."
)

st.sidebar.header("Your priorities")

priority_safety_ui = st.sidebar.slider("Safety", 0, 10, 5)
priority_healthcare_ui = st.sidebar.slider("Healthcare", 0, 10, 5)
priority_climate_ui = st.sidebar.slider("Climate", 0, 10, 5)
priority_purchasing_power_ui = st.sidebar.slider("Purchasing power", 0, 10, 5)

priority_low_cost_ui = st.sidebar.slider("Low cost of living", 0, 10, 5)
priority_housing_ui = st.sidebar.slider("Housing affordability", 0, 10, 5)
priority_low_pollution_ui = st.sidebar.slider("Low pollution", 0, 10, 5)

remote_worker = st.sidebar.checkbox("I work remotely", value=False)

show_dev_details = st.sidebar.checkbox("Show developer details", value=False)

st.subheader("Top CityFit recommendations")

top_n = st.slider("Number of cities to show", 5, 50, 15)

def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]

def query_agent_from_api(payload: dict) -> dict:
    response = requests.post(f"{API_URL}/agent/query", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()

def normalize_priority(value: int) -> float:
    return value / 5

base_payload = {
    "priority_safety": normalize_priority(priority_safety_ui),
    "priority_healthcare": normalize_priority(priority_healthcare_ui),
    "priority_climate": normalize_priority(priority_climate_ui),
    "priority_purchasing_power": normalize_priority(priority_purchasing_power_ui),
    "priority_low_cost": normalize_priority(priority_low_cost_ui),
    "priority_housing": normalize_priority(priority_housing_ui),
    "priority_low_pollution": normalize_priority(priority_low_pollution_ui),
    "remote_worker": remote_worker,
}

recommendation_payload = {
    **base_payload,
    "top_n": 50,
}


try:
    recommendations = get_recommendations_from_api(recommendation_payload)
    df = pd.DataFrame(recommendations)
except requests.RequestException as exc:
    st.error(f"Could not reach CityFit API: {exc}")
    st.stop()

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
    width="stretch",
    hide_index=True,
)

st.subheader("Rank movement")

moved_ranks_n = 10

st.write(
    "Positive rank difference means the city ranks better in your personalized "
    "CityFit score than in Numbeo's baseline Quality of Life ranking."
)

rank_movers = (
    df[display_cols]
    .sort_values("rank_difference", ascending=False)
    .head(moved_ranks_n)
)

st.dataframe(rank_movers, width="stretch", hide_index=True)

st.subheader("Biggest ranking changes")

movement_chart_df = (
    df[["city", "rank_difference"]]
    .sort_values("rank_difference", ascending=False)
    .head(moved_ranks_n)
)

min_rank_val = movement_chart_df["rank_difference"].min()
max_rank_val = movement_chart_df["rank_difference"].max()
padding = 1

fig = px.bar(
    movement_chart_df,
    x="city",
    y="rank_difference",
    title="Cities that moved up most after personalization",
    color="rank_difference",
    color_continuous_scale="speed",
    range_color=[min_rank_val - padding, max_rank_val + padding],
)

fig.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Rank movement: %{y:+.0f}<br>"
        "<extra></extra>"
    )
)

fig.update_layout(
    xaxis_title="City",
    yaxis_title="Rank Difference",
    coloraxis_showscale=False,
)

fig.update_xaxes(
    categoryorder="array",
    categoryarray=movement_chart_df["city"].tolist(),
)

st.plotly_chart(fig, width="stretch")

st.subheader("Compare specific cities")

city_options = sorted(df["city"].unique())
selected_cities = st.multiselect(
    "Choose cities to compare",
    options=city_options,
    default=[city for city in ["Tampa", "Miami", "New York", "Tokyo", "Madrid"] if city in city_options],
)

if selected_cities:
    comparison_cols = display_cols + ["explanation"]

    comparison_df = (
        df[df["city"].isin(selected_cities)][comparison_cols]
        .sort_values("cityfit_rank")
    )

    st.dataframe(
        comparison_df[display_cols],
        width="stretch",
        hide_index=True,
    )

    st.subheader("City explanations")

    for _, row in comparison_df.iterrows():
        st.write(f"**{row['city']}**")
        st.write(row["explanation"])


st.subheader("Ask CityFit AI")

if st.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑" if message["role"] == "user" else "🌎"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about city rankings, tradeoffs, methodology, or limitations..."
)

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    agent_payload = {
        **base_payload,
        "question": question,
        "top_n": top_n,
        "top_k_context": 4,
    }

    try:
        agent_response = query_agent_from_api(agent_payload)
        assistant_response = agent_response["answer"]

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response}
        )

        with st.chat_message("assistant", avatar="🌎"):
            st.markdown(assistant_response)

            if show_dev_details:
                with st.expander("Sources"):
                    st.write(", ".join(agent_response["sources"]))

                with st.expander("Governance metadata"):
                    st.json(agent_response["metadata"])

                with st.expander("Retrieved context"):
                    for chunk in agent_response["retrieved_context"]:
                        st.markdown(
                            f"**{chunk['source']} — chunk {chunk['chunk_index']}**"
                        )
                        st.write(chunk["text"])

    except requests.RequestException as exc:
        error_message = f"Could not reach CityFit Agent API: {exc}"

        st.session_state.messages.append(
            {"role": "assistant", "content": error_message}
        )

        with st.chat_message("assistant", avatar="🌎"):
            st.error(error_message)

st.caption(
    "Data note: This app uses a small educational sample derived from Numbeo city ranking pages. "
    "Numbeo data is credited to Numbeo.com and is not covered by this repository's code license."
)