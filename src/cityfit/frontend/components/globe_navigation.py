import streamlit as st


def bump_globe_chart_version() -> None:
    st.session_state["globe_chart_version"] = (
        st.session_state.get("globe_chart_version", 0) + 1
    )


def set_active_city(
    city: str | None,
    country: str | None,
    source: str,
) -> None:
    if city is None or country is None:
        return

    st.session_state["active_city"] = city
    st.session_state["active_country"] = country
    st.session_state["active_city_source"] = source


def set_focused_city(
    city: str | None,
    country: str | None,
) -> None:
    if city is None or country is None:
        return

    st.session_state["focused_city"] = city
    st.session_state["focused_country"] = country


def clear_active_city() -> None:
    st.session_state.pop("active_city", None)
    st.session_state.pop("active_country", None)
    st.session_state.pop("active_city_source", None)


def clear_focused_city() -> None:
    st.session_state.pop("focused_city", None)
    st.session_state.pop("focused_country", None)


def restore_focused_city_as_active() -> None:
    focused_city = st.session_state.get("focused_city")
    focused_country = st.session_state.get("focused_country")

    if focused_city is not None and focused_country is not None:
        set_active_city(
            city=focused_city,
            country=focused_country,
            source="focused",
        )
    else:
        clear_active_city()


def apply_similar_city_query_navigation() -> None:
    query_city = st.query_params.get("similar_city")
    query_country = st.query_params.get("similar_country")
    query_nav = st.query_params.get("nav")

    if not query_city or not query_country or not query_nav:
        return

    last_applied_nav = st.session_state.get("last_applied_query_nav")

    if query_nav == last_applied_nav:
        st.query_params.clear()
        return

    set_active_city(
        city=query_city,
        country=query_country,
        source="similar_city",
    )

    set_focused_city(
        city=query_city,
        country=query_country,
    )

    bump_globe_chart_version()

    city_label = f"{query_city}, {query_country}"

    st.session_state["pending_city_search_label"] = city_label
    st.session_state["skip_globe_selection_once"] = True
    st.session_state["skip_search_once"] = True
    st.session_state["last_applied_query_nav"] = query_nav
    st.session_state["last_city_search_label"] = city_label

    st.query_params.clear()