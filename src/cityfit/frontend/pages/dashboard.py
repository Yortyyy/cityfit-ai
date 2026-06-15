import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from cityfit.frontend.api import (
    get_recommendations_from_api,
    query_agent_from_api
)

def render_chat_styles() -> None:
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
            line-height: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
def build_rank_comparison_df(
    personalized_recommendations: list[dict],
) -> pd.DataFrame:
    comparison_df = pd.DataFrame(personalized_recommendations).rename(
        columns={
            "cityfit_rank": "personalized_cityfit_rank",
            "cityfit_score": "personalized_cityfit_score",
            "rank_difference": "rank_movement",
        }
    )

    return comparison_df.sort_values(
        "personalized_cityfit_rank",
        ascending=True,
    )


def render_dashboard_page(base_payload: dict, all_df: pd.DataFrame) -> None:
    render_chat_styles()

    st.title("📊 CityFit Dashboard")
    st.write(
        "Compare a default CityFit ranking against your personalized CityFit ranking. "
        "The default ranking treats every priority as moderately important, while the "
        "personalized ranking uses your selected priorities."
    )

    personalized_payload = {
        **base_payload,
        "top_n": 500,
    }

    try:
        personalized_recommendations = get_recommendations_from_api(personalized_payload)
        recommendations_df = build_rank_comparison_df(
            personalized_recommendations,
        )
    except requests.RequestException as exc:
        st.error(f"Could not reach CityFit API: {exc}")
        st.stop()

    if recommendations_df.empty:
        st.warning("No cities match the selected filters. Try a broader region or country.")
        st.stop()

    show_dev_details = st.sidebar.checkbox("Show developer details", value=False)

    st.subheader("Top CityFit Recommendations")
    top_n = st.slider("Number of cities to show", 5, 306, 15)

    recommendation_payload = personalized_payload

    display_cols = [
        "city",
        "country",
        "region",
        "baseline_cityfit_rank",
        "personalized_cityfit_rank",
        "rank_movement",
        "baseline_cityfit_score",
        "personalized_cityfit_score",
        "purchasing_power_index",
        "cost_of_living_index",
        "safety_index",
        "healthcare_index",
        "traffic_commute_index",
        "climate_index",
        "pollution_index",
    ]

    top_recommendation_cols = [
        "city",
        "country",
        "region",
        "personalized_cityfit_rank",
        "personalized_cityfit_score",
        "baseline_cityfit_rank",
        "rank_movement",
        "purchasing_power_index",
        "cost_of_living_index",
        "safety_index",
        "healthcare_index",
        "traffic_commute_index",
        "pollution_index",
        "climate_index",
    ]

    column_labels = {
        "city": "City",
        "country": "Country",
        "region": "Region",
        "baseline_cityfit_rank": "Baseline CityFit Rank",
        "personalized_cityfit_rank": "Personalized CityFit Rank",
        "rank_movement": "Rank Movement",
        "baseline_cityfit_score": "Baseline CityFit Score",
        "personalized_cityfit_score": "Personalized CityFit Score",
        "purchasing_power_index": "Purchasing Power Index",
        "cost_of_living_index": "Cost of Living Index",
        "safety_index": "Safety Index",
        "healthcare_index": "Healthcare Index",
        "traffic_commute_index": "Traffic Index",
        "pollution_index": "Pollution Index",
        "climate_index": "Climate Index",
    }

    top_recommendations_df = recommendations_df.head(top_n)

    st.caption(
        f"Showing {len(top_recommendations_df)} of {len(recommendations_df)} matching cities."
    )

    st.dataframe(
        top_recommendations_df[top_recommendation_cols],
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.Column(label)
            for column, label in column_labels.items()
            if column in top_recommendation_cols
        },
    )

    display_bar_n = 10
    recommendations_bar_df = recommendations_df.head(display_bar_n)

    padding = 1

    global_min_cityfit_score = recommendations_df["personalized_cityfit_score"].min()
    global_max_cityfit_score = recommendations_df["personalized_cityfit_score"].max()

    cityscore_color_range = [
        global_min_cityfit_score - padding,
        global_max_cityfit_score + padding,
    ]

    fig = px.bar(
        recommendations_bar_df,
        x="city",
        y="personalized_cityfit_score",
        title="Top Personalized CityFit Scorers",
        color="personalized_cityfit_score",
        color_continuous_scale="speed",
        range_color=cityscore_color_range,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "CityFit Score: %{y:+.0f}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="City",
        yaxis_title="CityFit Score",
        coloraxis_showscale=False,
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=recommendations_bar_df["city"].tolist(),
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Rank Movement")

    # TODO: If priorities are all 10 - default - don't display rank movement/changes

    positive_movers_df = recommendations_df[
        recommendations_df["rank_movement"] > 0
    ].copy()

    positive_movers_df = positive_movers_df.sort_values(
        "rank_movement",
        ascending=False,
    )

    st.write(
        "Positive rank movement means the city ranks higher with your selected priorities "
        "than it does under the default CityFit ranking where every priority is set to 5."
    )

    rank_movers = positive_movers_df[display_cols].head(top_n)

    st.dataframe(
        rank_movers,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.Column(label)
            for column, label in column_labels.items()
            if column in display_cols
        },
    )

    st.subheader("Biggest Ranking Changes")

    movement_chart_df = positive_movers_df[
        ["city", "rank_movement"]
    ].head(display_bar_n)

    global_min_rank_movement = 0
    global_max_rank_movement = positive_movers_df["rank_movement"].max()

    cityrank_color_range = [
        global_min_rank_movement - padding,
        global_max_rank_movement + padding,
    ]
    
    if positive_movers_df.empty:
        st.info("No cities moved up with the current priority settings.")
    else:
        fig = px.bar(
            movement_chart_df,
            x="city",
            y="rank_movement",
            title="Cities that moved up most after personalization",
            color="rank_movement",
            color_continuous_scale="speed",
            range_color=cityrank_color_range,
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
            yaxis_title="Rank Movement",
            coloraxis_showscale=False,
        )

        fig.update_xaxes(
            categoryorder="array",
            categoryarray=movement_chart_df["city"].tolist(),
        )

        st.plotly_chart(fig, width="stretch")

    st.subheader("Compare Specific Cities")
    
    preselected_cities = ["Tampa", "Miami", "New York", "Rome", "Tokyo"]

    city_options = sorted(recommendations_df["city"].unique())
    selected_cities = st.multiselect(
        "Choose cities to compare",
        options=city_options,
        default=[
            city
            for city in preselected_cities
            if city in city_options
        ],
    )

    if selected_cities:
        comparison_cols = display_cols + ["explanation"]

        comparison_df = (
            recommendations_df[recommendations_df["city"].isin(selected_cities)][
                comparison_cols
            ]
            .sort_values("personalized_cityfit_rank")
        )

        st.dataframe(
            comparison_df[display_cols],
            width="stretch",
            hide_index=True,
        )

        st.subheader("City Explanations")

        for _, row in comparison_df.iterrows():
            st.write(f"**{row['city']} - #{round(row['personalized_cityfit_rank'])}**")
            st.write(row["explanation"])

    st.subheader("Ask CityFit AI")

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
            **recommendation_payload,
            "question": question,
            "top_n": top_n,
            "top_k_context": 4,
        }

        try:
            if show_dev_details:
                st.write("Agent payload", agent_payload)

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

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption(
        "Data note: This app uses a small educational city metrics sample. "
        "CityFit scores and rankings are generated by this project for demonstration purposes."
    )
