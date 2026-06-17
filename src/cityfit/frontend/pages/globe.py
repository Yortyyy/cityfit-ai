import pandas as pd
import requests
import streamlit as st

from cityfit.frontend.api import get_recommendations_from_api
from cityfit.frontend.components.city_comparison import (
    COMPARISON_TRACE_KEY,
    get_comparison_trace_labels,
    render_city_comparison,
)
from cityfit.frontend.components.city_profile import render_city_profile
from cityfit.frontend.components.city_search import render_city_search
from cityfit.frontend.components.globe_chart import (
    build_globe_figure,
    render_selectable_globe,
)
from cityfit.frontend.components.globe_data import load_globe_data
from cityfit.frontend.components.globe_navigation import (
    apply_similar_city_query_navigation,
    bump_globe_chart_version,
    clear_active_city,
    clear_focused_city,
    restore_focused_city_as_active,
    set_active_city,
    set_focused_city,
)
from cityfit.frontend.components.hero import render_hero
from cityfit.frontend.components.methodology import render_methodology_card
from cityfit.frontend.styles.loader import load_css



def render_globe_page(payload: dict, all_df: pd.DataFrame) -> None:
    load_css(
        "base.css",
        "sidebar.css",
        "methodology.css",
        "search.css",
        "hero.css",
        "city_profile.css",
        "metric_table.css",
        "comparison.css",
        "similar_cities.css",
    )

    render_hero()
    render_methodology_card()
    apply_similar_city_query_navigation()

    try:
        globe_df = load_globe_data(payload)
    except requests.RequestException as exc:
        st.error(f"Could not reach CityFit API: {exc}")
        st.stop()

    if globe_df.empty:
        st.warning("No cities found for the selected filters.")
        return

    previous_search_label = st.session_state.get("last_city_search_label")

    searched_city, searched_country = render_city_search(globe_df)

    current_search_label = None
    if searched_city is not None and searched_country is not None:
        current_search_label = f"{searched_city}, {searched_country}"

    skip_search_once = st.session_state.pop("skip_search_once", False)

    if not skip_search_once:
        search_changed = (
            current_search_label is not None
            and current_search_label != previous_search_label
        )

        search_cleared = (
            current_search_label is None
            and previous_search_label is not None
        )

        if search_changed:
            set_active_city(
                city=searched_city,
                country=searched_country,
                source="search",
            )

            set_focused_city(
                city=searched_city,
                country=searched_country,
            )

            bump_globe_chart_version()

        elif search_cleared:
            clear_active_city()
            clear_focused_city()

            st.session_state.pop("ignore_next_empty_globe_selection", None)
            st.session_state.pop("ignore_next_globe_click", None)

            bump_globe_chart_version()

    st.session_state["last_city_search_label"] = current_search_label

    focused_city = st.session_state.get("focused_city")
    focused_country = st.session_state.get("focused_country")
    comparison_city_labels = get_comparison_trace_labels()
    st.session_state[COMPARISON_TRACE_KEY] = comparison_city_labels

    fig = build_globe_figure(
        globe_df,
        all_df,
        focused_city,
        focused_country,
        comparison_city_labels=comparison_city_labels,
    )

    clicked_city, clicked_country = render_selectable_globe(fig)

    skip_globe_selection_once = st.session_state.pop(
        "skip_globe_selection_once",
        False,
    )

    if skip_globe_selection_once:
        clicked_city = None
        clicked_country = None

    if clicked_city is not None and clicked_country is not None:
        clicked_label = f"{clicked_city}, {clicked_country}"

        active_city = st.session_state.get("active_city")
        active_country = st.session_state.get("active_country")
        active_source = st.session_state.get("active_city_source")

        active_label = None
        if active_city is not None and active_country is not None:
            active_label = f"{active_city}, {active_country}"

        # Re-selecting the same globe city is a no-op; clearing the selection
        # is handled by the empty-selection branch below.
        if clicked_label != active_label:
            set_active_city(
                city=clicked_city,
                country=clicked_country,
                source="globe",
            )

            # Do not set focused city here.
            # Do not rerun here.

    else:
        active_source = st.session_state.get("active_city_source")

        if active_source == "globe" and not skip_globe_selection_once:
            restore_focused_city_as_active()
            bump_globe_chart_version()
            st.rerun()

    profile_city = st.session_state.get("active_city")
    profile_country = st.session_state.get("active_country")

    render_city_profile(globe_df, all_df, profile_city, profile_country)
    render_city_comparison(globe_df, all_df)
