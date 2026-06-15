import streamlit as st


def render_methodology_card() -> None:
    st.html(
        """
        <div class="methodology-card">
            <h3>How CityFit works</h3>
            <p>
                CityFit ranks cities based on your selected lifestyle priorities. Each city receives a personalized
                score based on the factors below.
            </p>
            
            <div class="methodology-pill-row">
                <span class="methodology-pill">Affordability</span>
                <span class="methodology-pill">Housing</span>
                <span class="methodology-pill">Safety</span>
                <span class="methodology-pill">Healthcare</span>
                <span class="methodology-pill">Climate</span>
                <span class="methodology-pill">Pollution</span>
                <span class="methodology-pill">Traffic</span>
                <span class="methodology-pill">Purchasing Power</span>
            </div>
        </div>
        """
    )