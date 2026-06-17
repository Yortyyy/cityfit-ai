import requests
import streamlit as st

from cityfit.frontend.api import query_agent_from_api


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
    

def render_agent_page(recommendation_payload: dict) -> None:
    render_chat_styles()
    
    st.title("🌎 Ask CityFit AI")
    st.write(
        "Ask about city rankings, tradeoffs, methodology, or limitations."
    )

    show_dev_details = st.sidebar.checkbox("Show developer details", value=False)
    # top_n = st.sidebar.slider("Agent recommendation count", 5, 306, 15)

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
        st.session_state.messages.append({"role": "user", "content": question})

        agent_payload = {
            **recommendation_payload,
            "question": question,
            # "top_n": top_n,
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
            st.error(f"Could not reach CityFit Agent API: {exc}")

    if st.session_state.messages:
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()