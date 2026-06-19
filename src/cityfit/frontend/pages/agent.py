import requests
import streamlit as st

from cityfit.frontend.api import query_agent_from_api
from cityfit.frontend.components.agent_prompt_cards import render_agent_prompt_cards
from cityfit.frontend.styles.loader import load_css


def submit_centered_agent_question() -> None:
    question = st.session_state.get("agent_centered_question", "").strip()

    if not question:
        return

    st.session_state.agent_messages.append(
        {"role": "user", "content": question}
    )
    st.session_state.pending_question = question
    st.session_state.agent_centered_question = ""


def render_centered_agent_input() -> None:
    with st.container(key="agent_centered_input"):
        st.text_input(
            "Ask CityFit AI",
            placeholder="Ask about rankings, tradeoffs, methodology, or limitations...",
            label_visibility="collapsed",
            key="agent_centered_question",
            on_change=submit_centered_agent_question,
        )

        if st.button(
            "↑",
            key="agent_centered_send_button",
        ):
            submit_centered_agent_question()
            st.rerun()

def render_agent_page(recommendation_payload: dict) -> None:
    load_css(
        "base.css",
        "sidebar.css",
        "agent.css",
    )

    show_dev_details = st.sidebar.checkbox("Show developer details", value=False)

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    if not st.session_state.agent_messages:
        st.markdown('<div class="agent-empty-spacer"></div>', unsafe_allow_html=True)
        
        with st.container(key="agent_empty_state"):
            st.markdown(
                """
                <div class="agent-empty-question">
                    How can CityFit help you today?
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            render_centered_agent_input()
            render_agent_prompt_cards()

    for message in st.session_state.agent_messages:
        avatar = "🧑" if message["role"] == "user" else "🌎"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            if message["role"] == "assistant" and show_dev_details:
                agent_response = message.get("metadata_response")

                if agent_response:
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

    question = None

    if st.session_state.agent_messages:
        question = st.chat_input(
            "Ask about city rankings, tradeoffs, methodology, or limitations..."
        )

    if question:
        st.session_state.agent_messages.append(
            {"role": "user", "content": question}
        )
        st.session_state.pending_question = question
        st.rerun()


    if st.session_state.pending_question:
        question_to_answer = st.session_state.pending_question
        st.session_state.pending_question = None

        agent_payload = {
            **recommendation_payload,
            "question": question_to_answer,
            "top_k_context": 4,
        }

        try:
            agent_response = query_agent_from_api(agent_payload)
            assistant_response = agent_response["answer"]

            st.session_state.agent_messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response,
                    "metadata_response": agent_response,
                }
            )

            st.rerun()

        except requests.RequestException as exc:
            st.session_state.agent_messages.append(
                {
                    "role": "assistant",
                    "content": f"Could not reach CityFit Agent API: {exc}",
                }
            )
            st.rerun()

    if st.session_state.agent_messages:
        if st.button("Clear chat"):
            st.session_state.agent_messages = []
            st.session_state.pending_question = None
            st.rerun()