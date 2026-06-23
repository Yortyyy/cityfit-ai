import requests
import streamlit as st

from cityfit.frontend.api import query_agent_from_api
from cityfit.frontend.components.agent_prompt_cards import render_agent_prompt_cards
from cityfit.frontend.styles.loader import load_css


def submit_agent_question(input_key: str) -> None:
    question = st.session_state.get(input_key, "").strip()

    if not question:
        return

    if st.session_state.get("pending_question"):
        return

    st.session_state.agent_messages.append(
        {"role": "user", "content": question}
    )

    st.session_state.pending_question = question
    st.session_state[input_key] = ""


def render_agent_input(
    container_key: str,
    input_key: str,
    button_key: str,
) -> None:
    with st.container(key=container_key):
        st.text_input(
            "Ask CityFit AI",
            placeholder="Ask about city rankings, tradeoffs, methodology, or limitations...",
            label_visibility="collapsed",
            key=input_key,
            on_change=submit_agent_question,
            args=(input_key,),
        )

        st.button(
            "↑",
            key=button_key,
            on_click=submit_agent_question,
            args=(input_key,),
        )

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

    is_loading = st.session_state.pending_question is not None

    # Empty state
    if not st.session_state.agent_messages and not is_loading:
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

            render_agent_input(
                container_key="agent_centered_input",
                input_key="agent_centered_question",
                button_key="agent_centered_send_button",
            )
            render_agent_prompt_cards()

    # Render chat history
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

    # Answer pending question before rendering the input again
    if st.session_state.pending_question:
        question_to_answer = st.session_state.pending_question
        st.session_state.pending_question = None

        agent_payload = {
            **recommendation_payload,
            "question": question_to_answer,
            "top_k_context": 4,
        }

        with st.chat_message("assistant", avatar="🌎"):
            with st.spinner("CityFit is thinking..."):
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

        return

    # Active chat input
    # TODO: Make permanent hover
    if st.session_state.agent_messages and not st.session_state.pending_question:
        with st.container(key="agent_clear_chat_row"):
            if st.button("Clear chat", key="agent_clear_chat_button"):
                st.session_state.agent_messages = []
                st.session_state.pending_question = None
                st.rerun()

        render_agent_input(
            container_key="agent_active_input",
            input_key="agent_active_question",
            button_key="agent_active_send_button",
        )