import streamlit as st


def render_agent_prompt_cards() -> None:
    st.markdown("#### Try asking")

    prompt_cards = [
        {
            "label": "What is CityFit's methodology?",
            "prompt": "What is CityFit's methodology?",
        },
        {
            "label": "How does CityFit calculate rank movement?",
            "prompt": "How does CityFit calculate rank movement?",
        },
        {
            "label": "Compare cities...",
            "prompt": "Compare Tampa and Rome.",
        },
    ]

    cols = st.columns(3)

    for index, card in enumerate(prompt_cards):
        with cols[index % 3]:
            if st.button(
                card["label"],
                key=f"agent_prompt_card_{index}",
                use_container_width=True,
            ):
                st.session_state.agent_messages.append(
                    {"role": "user", "content": card["prompt"]}
                )
                st.session_state.pending_question = card["prompt"]
                st.rerun()