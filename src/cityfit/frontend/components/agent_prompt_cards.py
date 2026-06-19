import streamlit as st


PROMPT_CARDS = [
    {
        "key": "agent_prompt_methodology",
        "title": "What is CityFit's methodology?",
        "prompt": "What is CityFit's methodology?",
        "description": "Understand how CityFit scores and ranks cities.",
    },
    {
        "key": "agent_prompt_rank_movement",
        "title": "How does CityFit calculate rank movement?",
        "prompt": "How does CityFit calculate rank movement?",
        "description": "See how personalized ranks compare with baseline CityFit.",
    },
    {
        "key": "agent_prompt_compare_cities",
        "title": "Compare Multiple Cities.",
        "prompt": "Compare the top recommended cities for me.",
        "description": "View multiple city metrics using the current priority profile.",
    },
]


def render_agent_prompt_cards() -> None:
    cols = st.columns(3)

    for index, card in enumerate(PROMPT_CARDS):
        label = (
            f"**{card['title']}**\n\n"
            f"{card['description']}\n\n"
        )

        with cols[index]:
            if st.button(
                label,
                key=card["key"],
                use_container_width=True,
            ):
                st.session_state.agent_messages.append(
                    {"role": "user", "content": card["prompt"]}
                )
                st.session_state.pending_question = card["prompt"]
                st.rerun()