import streamlit as st


def render_hero():
    st.markdown(
        """
        <div class="hero-title">
            <div class="eyebrow">CITYFIT</div>
            <h1><span class="hero-bold">Hello</span>, this is our <span class="hero-bold">World</span>.</h1>
            <p>Find out where <span class="hero-bold">you</span> fit in.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )