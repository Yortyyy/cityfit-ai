import pandas as pd
import streamlit as st

from cityfit.frontend.api import get_recommendations_from_api

@st.cache_data(ttl=300)
def load_globe_data_cached(payload_key: tuple) -> pd.DataFrame:
    payload = dict(payload_key)

    recommendations = get_recommendations_from_api(
        {
            **payload,
            "top_n": 500,
        }
    )

    df = pd.DataFrame(recommendations)

    return df.dropna(subset=["latitude", "longitude"])


def load_globe_data(payload: dict) -> pd.DataFrame:
    payload_key = tuple(sorted(payload.items()))
    return load_globe_data_cached(payload_key)
