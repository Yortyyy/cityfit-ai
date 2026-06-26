import streamlit as st

from cityfit.frontend.styles.loader import load_css


def render_methodology_page() -> None:
    load_css(
        "base.css",
        "sidebar.css",
    )

    st.markdown(
        """
        <div class="hero-title">
            <div class="eyebrow">CITYFIT METHODOLOGY</div>
            <h1><span class="hero-bold">How</span> CityFit works.</h1>
            <p>Understand the practical score, lifestyle score, category weights, and rank movement.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### CityFit Score")
    st.write(
        """
        CityFit Score is the blended recommendation score. It can include Practical Fit,
        Lifestyle Fit, or both depending on the two overall influence sliders in the
        sidebar. This lets users view practical-only results, lifestyle-only results,
        or a mixed ranking.
        """
    )

    st.markdown("### Priority sliders")
    st.write(
        """
        The app shows 0-10 sliders because that scale is easier to understand.
        Internally, those values are converted to 0-2 priority multipliers before
        being sent to the API.
        """
    )

    st.markdown(
        """
        - `0` means the priority is ignored
        - `5` means default importance
        - `10` means double importance
        """
    )

    st.markdown("### Practical Fit")
    st.write(
        """
        Practical Fit starts with the source quality-of-life index, then blends in
        practical priority features. Higher-is-better metrics are scaled upward,
        while cost, housing price pressure, traffic, and pollution are inverted so
        lower real-world values become better feature scores.
        """
    )

    st.code(
        """
    practical_priority_score =
            0.15 * purchasing_power_score,
            0.10 * affordability_score,
            0.15 * safety_score,
            0.10 * healthcare_score,
            0.15 * housing_affordability_score,
            0.10 * low_traffic_score,
            0.15 * climate_score,
            0.10 * low_pollution_score
        """.strip()
    )

    st.write(
        """
        The remote-work checkbox reduces the low-traffic weight by half because
        commuting matters less for remote workers.
        """
    )

    st.code(
        """
    practical_score =
        (
            0.30 * numbeo_quality_of_life_index
            + 0.70 * practical_priority_score
        )
        * 1.75
        """.strip()
    )

    st.markdown("### Lifestyle Fit")
    st.write(
        """
        Lifestyle Fit combines day-to-day preference scores. Friendliness is blank
        until there is a legally usable newcomer-integration source, and pace of life
        remains a categorical label rather than a higher-is-better score.
        """
    )

    st.code(
        """
    lifestyle_score =
        0.20 * daily_life_score
        + 0.15 * food_scene_score
        + 0.15 * culture_score
        + 0.15 * outdoors_score
        + 0.15 * transit_score
        + 0.10 * airport_score
        + 0.10 * nightlife_score
        """.strip()
    )

    st.write(
        """
        The raw Lifestyle Score is a 0-100 lifestyle metric average. Before it is
        blended into CityFit Score, it is mapped onto the original CityFit scale:
        around 100 is broadly livable, 200+ is exceptional, and near 0 is a poor fit.
        """
    )

    st.markdown("### Overall Category Weights")
    st.write(
        """
        Practical Fit and Lifestyle Fit each have an overall influence slider in the
        sidebar. Set Practical Fit influence to zero for lifestyle-only results, or
        set Lifestyle Fit influence to zero for practical-only results.
        """
    )

    st.code(
        """
    cityfit_score =
        (
            practical_fit_weight * practical_score
            + lifestyle_fit_weight * lifestyle_fit_score
        )
        / total_fit_weight
        """.strip()
    )

    st.write(
        """
        If both overall category weights are set to zero, CityFit falls back to
        Practical Fit so the ranking remains usable.
        """
    )

    st.markdown("### Baseline CityFit Rank")
    st.write(
        """
        CityFit calculates a neutral baseline ranking where every priority is set to
        default importance. Personalized rankings are compared against this baseline
        ranking.
        """
    )

    st.markdown("### Rank Movement")
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
        CityFit is intended for educational and portfolio use. The dataset may not
        reflect every city or the latest real-world conditions. Lifestyle metrics are
        proxy scores based mostly on public availability signals, not full quality or
        neighborhood-level measures. Recommendations should not be treated as
        financial, legal, immigration, medical, or relocation advice.
        """
    )
