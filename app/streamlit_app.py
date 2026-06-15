import streamlit as st
import requests

import pandas as pd

from cityfit.frontend.api import get_recommendations_from_api
from cityfit.frontend.components.sidebar import (
    render_filter_sidebar,
    render_priority_sidebar,
)
from cityfit.frontend.pages.dashboard import render_dashboard_page
from cityfit.frontend.pages.globe import render_globe_page


st.set_page_config(
    page_title="CityFit AI",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def normalize_priority(value: int) -> float:
    return value / 5


st.sidebar.title("🌎 CityFit AI")

selected_page = st.sidebar.radio(
    "Page",
    ["Globe", "Dashboard"],
)

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
else:
    render_dashboard_page(filtered_payload, all_df)