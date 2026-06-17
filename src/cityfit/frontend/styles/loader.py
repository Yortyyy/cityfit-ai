from pathlib import Path

import streamlit as st


STYLES_DIR = Path(__file__).parent


def load_css(*filenames: str) -> None:
    css_parts = []

    for filename in filenames:
        path = STYLES_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"CSS file not found: {path}")

        css_parts.append(path.read_text(encoding="utf-8"))

    combined_css = "\n\n".join(css_parts)

    st.markdown(
        f"<style>{combined_css}</style>",
        unsafe_allow_html=True,
    )