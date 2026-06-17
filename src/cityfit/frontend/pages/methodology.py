import streamlit as st


def render_methodology_page() -> None:
    st.markdown(
        """
        <div class="hero-title">
            <div class="eyebrow">CITYFIT METHODOLOGY</div>
            <h1><span class="hero-bold">How</span> CityFit works.</h1>
            <p>Understand the scoring, baseline rank, and personalization logic.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### CityFit Score")
    st.write(
        """
        CityFit combines a quality-of-life baseline with a personalized lifestyle adjustment.
        The adjustment is based on priorities such as affordability, housing, safety,
        healthcare, climate, pollution, traffic, and purchasing power.
        """
    )

    st.markdown("### Priority sliders")
    st.write(
        """
        The Streamlit app shows 0–10 sliders because that scale is easier to understand.
        Internally, those values are converted to 0–2 priority multipliers before being
        sent to the API.
        """
    )

    st.markdown(
        """
        - `0` means the priority is ignored
        - `5` means default importance
        - `10` means double importance
        """
    )

    st.markdown("### Baseline CityFit rank")
    st.write(
        """
        CityFit calculates a neutral baseline ranking where every priority is set to default
        importance. Personalized rankings are compared against this baseline CityFit ranking.
        """
    )

    st.markdown("### Rank movement")
    st.code("rank_difference = baseline_cityfit_rank - personalized_cityfit_rank")

    st.write(
        """
        A positive value means the city moved up for the selected priorities.
        A negative value means it moved down compared with the neutral baseline.
        """
    )

    st.markdown("### Limitations")
    st.write(
        """
        CityFit is intended for educational and portfolio use. The dataset may not reflect
        every city or the latest real-world conditions. Recommendations should not be treated
        as financial, legal, immigration, medical, or relocation advice.
        """
    )
    
    st.markdown("### How the CityFit Score is calculated")

    st.write(
        """
        CityFit combines a source quality-of-life baseline with a personalized
        lifestyle adjustment. The baseline comes from the `numbeo_quality_of_life_index`,
        while the personalized adjustment is calculated from the user's selected
        lifestyle priorities.
        """
    )

    st.markdown(
        """
        The personalized adjustment uses these priority features:

        - Purchasing power
        - Affordability
        - Safety
        - Healthcare
        - Housing affordability
        - Low traffic
        - Climate
        - Low pollution
        """
    )

    st.write(
        """
        Each priority feature is multiplied by its selected weight. The weighted
        values are then divided by the total weight so scores remain comparable
        even when users choose different priority settings.
        """
    )

    st.code(
        """
    weighted_priority_score =
        sum(priority_feature_score * priority_weight) / total_priority_weight
        """.strip()
    )

    st.write(
        """
        The final CityFit Score blends the original quality-of-life index with the
        personalized priority score. In the current MVP, personalization has more
        influence than the source baseline.
        """
    )

    st.code(
        """
    cityfit_score =
        quality_of_life_index * 0.3
        + weighted_priority_score * 0.7
        """.strip()
    )

    st.write(
        """
        The result is then scaled and rounded to one decimal place for display.
        """
    )