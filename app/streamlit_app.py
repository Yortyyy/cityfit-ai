import streamlit as st

from cityfit.frontend.pages.dashboard import render_dashboard_page
from cityfit.frontend.pages.globe import render_globe_page


st.set_page_config(
    page_title="CityFit AI",
    page_icon="🌎",
    layout="wide",
)

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


def normalize_priority(value: int) -> float:
    return value / 5


st.sidebar.title("🌎 CityFit AI")

selected_page = st.sidebar.radio(
    "Page",
    ["Globe", "Dashboard"],
)

st.sidebar.header("Your priorities")

priority_safety_ui = st.sidebar.slider("Safety", 0, 10, 8)
priority_healthcare_ui = st.sidebar.slider("Healthcare", 0, 10, 5)
priority_climate_ui = st.sidebar.slider("Climate", 0, 10, 8)
priority_purchasing_power_ui = st.sidebar.slider("Purchasing power", 0, 10, 7)

priority_low_cost_ui = st.sidebar.slider("Low cost of living", 0, 10, 3)
priority_housing_ui = st.sidebar.slider("Housing affordability", 0, 10, 5)
priority_low_pollution_ui = st.sidebar.slider("Low pollution", 0, 10, 7)

remote_worker = st.sidebar.checkbox("I work remotely", value=False)

base_payload = {
    "priority_safety": normalize_priority(priority_safety_ui),
    "priority_healthcare": normalize_priority(priority_healthcare_ui),
    "priority_climate": normalize_priority(priority_climate_ui),
    "priority_purchasing_power": normalize_priority(priority_purchasing_power_ui),
    "priority_low_cost": normalize_priority(priority_low_cost_ui),
    "priority_housing": normalize_priority(priority_housing_ui),
    "priority_low_pollution": normalize_priority(priority_low_pollution_ui),
    "remote_worker": remote_worker,
}

if selected_page == "Globe":
    render_globe_page(base_payload)
else:
    render_dashboard_page(base_payload)