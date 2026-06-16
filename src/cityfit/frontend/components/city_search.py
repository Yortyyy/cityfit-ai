import pandas as pd
import streamlit as st



def render_city_search(globe_df: pd.DataFrame) -> tuple[str | None, str | None]:
    st.markdown(
        """
        <div class="city-search-panel">
            <div class="city-search-eyebrow">FIND YOUR FIT</div>
            <h3>Search the Globe</h3>
            <p>
                Filter by region and country, search directly for a city, or select a marker
                on the globe to open its profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    """Render city search selectbox and return selected city/country."""
    city_options_df = (
        globe_df[["city", "country"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["city", "country"])
    )

    city_options = [
        f"{row.city}, {row.country}"
        for row in city_options_df.itertuples(index=False)
    ]

    pending_city_label = st.session_state.pop(
        "pending_city_search_label",
        None,
    )

    if pending_city_label in city_options:
        st.session_state["city_search_selectbox"] = pending_city_label

    selected_city_label = st.selectbox(
        "Search for a city",
        city_options,
        index=None,
        placeholder="Search for a city...",
        key="city_search_selectbox",
        label_visibility="collapsed",
    )

    if selected_city_label is None:
        return None, None

    selected_city, selected_country = selected_city_label.rsplit(", ", 1)

    return selected_city, selected_country
