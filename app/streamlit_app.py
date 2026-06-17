import streamlit as st
import requests

import pandas as pd

from cityfit.frontend.api import get_recommendations_from_api
from cityfit.frontend.components.sidebar import (
    render_filter_sidebar,
    render_priority_sidebar,
)
from cityfit.frontend.pages.agent import render_agent_page
from cityfit.frontend.pages.dashboard import render_dashboard_page
from cityfit.frontend.pages.globe import render_globe_page
from cityfit.frontend.pages.methodology import render_methodology_page


st.set_page_config(
    page_title="CityFit",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def normalize_priority(value: int) -> float:
    return value / 5


st.sidebar.title("🌎 CityFit")

page_options = ["Globe", "Dashboard", "Methodology", "Ask CityFit AI"]

query_page = st.query_params.get("page", "Globe")

if "selected_page" not in st.session_state:
    st.session_state.selected_page = (
        query_page if query_page in page_options else "Globe"
    )


def sync_page_to_url() -> None:
    st.query_params["page"] = st.session_state.selected_page


selected_page = st.sidebar.radio(
    "Page:",
    page_options,
    key="selected_page",
    on_change=sync_page_to_url,
)

st.query_params["page"] = selected_page

if selected_page == "Methodology":
    render_methodology_page()
    st.stop()

base_payload = render_priority_sidebar()

metadata_payload = {
    **base_payload,
    "top_n": 500,
    "region": None,
    "country": None,
}

try:
    all_recommendations = get_recommendations_from_api(metadata_payload)
    all_df = pd.DataFrame(all_recommendations)
except requests.RequestException as exc:
    st.error(f"Could not reach CityFit API: {exc}")
    st.stop()

filter_payload = render_filter_sidebar(all_df)

filtered_payload = {
    **base_payload,
    **filter_payload,
}

if selected_page == "Globe":
    render_globe_page(filtered_payload, all_df)
elif selected_page == "Dashboard":
    render_dashboard_page(filtered_payload, all_df)
elif selected_page == "Ask CityFit AI":
    render_agent_page(filtered_payload)