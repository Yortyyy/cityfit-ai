import streamlit as st

def render_globe_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 20% 10%, rgba(255,255,255,0.85), transparent 28%),
                radial-gradient(circle at 80% 30%, rgba(90,90,180,0.28), transparent 30%),
                linear-gradient(135deg, #eef0fa 0%, #c8c6eb 45%, #9ea4d9 100%);
        }

        .block-container {
            padding-top: 2rem;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.08) 50%, rgba(0,0,0,0.035) 50%);
            background-size: 100% 4px;
            mix-blend-mode: soft-light;
            opacity: 0.35;
            z-index: 999999;
        }

        /* ========================= */
        /* SIDEBAR */
        /* ========================= */

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 20% 10%, rgba(255,255,255,0.16), transparent 28%),
                linear-gradient(180deg, rgba(105, 108, 176, 0.94), rgba(64, 68, 132, 0.94)) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.28) !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: rgba(245, 246, 255, 0.96) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: rgba(245, 246, 255, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.38) !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
            color: rgba(245, 246, 255, 0.96) !important;
            background-color: transparent !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span {
            color: rgba(245, 246, 255, 0.96) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {
            fill: rgba(245, 246, 255, 0.96) !important;
            color: rgba(245, 246, 255, 0.96) !important;
        }

        /* ========================= */
        /* CITY SEARCH SELECTBOX ONLY */
        /* ========================= */

        /* Widget wrapper generated from key="city_search_selectbox" */
        .st-key-city_search_selectbox {
            position: relative !important;
            max-width: 100% !important;
            margin-top: 1.25rem !important;
            margin-bottom: 1.25rem !important;
        }

        /* Actual visible selectbox surface */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div {
            min-height: 44px !important;
            height: 44px !important;
            border-radius: 999px !important;
            padding-left: 3rem !important;

            background:
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%231f254f' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'%3E%3C/circle%3E%3Cline x1='16.5' y1='16.5' x2='21' y2='21'%3E%3C/line%3E%3C/svg%3E") 1.05rem center / 18px 18px no-repeat,
                linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.85) 18%,
                    rgba(255, 255, 255, 0.28) 38%,
                    transparent 58%
                ) 3rem 0.35rem / calc(100% - 5.8rem) 10px no-repeat,
                linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.88) 0%,
                    rgba(238, 241, 255, 0.58) 45%,
                    rgba(178, 185, 235, 0.42) 100%
                ) !important;

            border: 1px solid rgba(255, 255, 255, 0.95) !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -16px 28px rgba(85, 95, 175, 0.24),
                0 18px 42px rgba(35, 40, 100, 0.24),
                0 0 0 1px rgba(90, 105, 190, 0.16) !important;

            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
        }

        /* Force BaseWeb inner layers transparent */
        .st-key-city_search_selectbox div[data-baseweb="select"],
        .st-key-city_search_selectbox div[data-baseweb="select"] > div > div,
        .st-key-city_search_selectbox div[data-baseweb="select"] input {
            background-color: transparent !important;
        }

        /* Placeholder / selected text */
        .st-key-city_search_selectbox div[data-baseweb="select"] div,
        .st-key-city_search_selectbox div[data-baseweb="select"] span,
        .st-key-city_search_selectbox div[data-baseweb="select"] input {
            color: #1f254f !important;
            font-weight: 750 !important;
            font-size: 0.95rem !important;
        }

        /* Hover glow */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div:hover {
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -16px 28px rgba(85, 95, 175, 0.28),
                0 22px 52px rgba(35, 40, 100, 0.30),
                0 0 0 3px rgba(120, 140, 255, 0.20) !important;
        }

        /* Dropdown arrow */
        .st-key-city_search_selectbox svg {
            color: #1f254f !important;
            fill: #1f254f !important;
        }

        /* ========================= */
        /* HERO TITLE */
        /* ========================= */

        .hero-title .eyebrow {
            font-size: 0.78rem;
            letter-spacing: 0.22rem;
            color: rgba(30, 40, 80, 0.7);
            font-weight: 700;
        }

        .hero-title h1 {
            font-size: 3rem;
            margin-bottom: 0.25rem;
            color: #1f254f;
            text-shadow: 2px 2px 0 rgba(255,255,255,0.7);
        }

        .hero-title p {
            color: rgba(20, 25, 55, 0.75);
            font-size: 1.05rem;
        }

        .city-profile-title {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: 2rem;
            font-weight: 500;
            color: #0f2354;
            margin-top: 1.25rem;
            margin-bottom: 1.25rem;
        }

        .city-profile-title-text {
            font-size: 34px;
            font-weight: 600;
            color: #08285a;
            line-height: 1.15;
            white-space: nowrap;
        }

        .city-profile-title-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin: 12px 0 28px 0;
        }

        .city-profile-flag-box {
            width: 60px;
            height: 40px;

            display: flex;
            align-items: center;
            justify-content: center;

            flex: 0 0 60px;
        }

        .city-profile-flag-img {
            width: 60px !important;
            height: 40px !important;

            display: block !important;
            object-fit: cover !important;

            border-radius: 4px;
            box-shadow: 0 3px 8px rgba(20, 30, 60, 0.18);
        }

        /* ========================= */
        /* METRIC TABLE */
        /* ========================= */

        .metric-table-card {
            margin-top: 1rem !important;
            border-radius: 18px !important;
            overflow: hidden !important;
            background: rgba(245, 246, 255, 0.45) !important;
            border: 1px solid rgba(255, 255, 255, 0.65) !important;
            box-shadow: 0 18px 45px rgba(40, 40, 90, 0.18) !important;
            backdrop-filter: blur(8px) !important;
        }

        .metric-table-card table,
        .metric-table {
            width: 100% !important;
            border-collapse: collapse !important;
            background: transparent !important;
            color: #1f254f !important;
        }

        .metric-table-card thead,
        .metric-table thead {
            background: rgba(255, 255, 255, 0.45) !important;
        }

        .metric-table-card th,
        .metric-table th {
            text-align: left !important;
            padding: 0.9rem 1rem !important;
            font-weight: 800 !important;
            color: rgba(31, 37, 79, 0.82) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.65) !important;
            background: rgba(255, 255, 255, 0.35) !important;
        }

        .metric-table-card td,
        .metric-table td {
            padding: 0.85rem 1rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.38) !important;
            font-weight: 650 !important;
            color: #1f254f !important;
        }

        .metric-table-card td.metric-value-cell,
        .metric-table td.metric-value-cell {
            color: var(--metric-color) !important;
            background: rgba(245, 246, 255, 0.20) !important;
            font-size: 1.05rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.02em !important;
            font-variant-numeric: tabular-nums !important;
            text-shadow:
                1px 1px 0 color-mix(in srgb, var(--metric-color) 55%, #1f254f),
                2px 2px 1px rgba(31, 37, 79, 0.22) !important;
        }

        .metric-table-card td:last-child,
        .metric-table-card th:last-child,
        .metric-table td:last-child,
        .metric-table th:last-child {
            text-align: right !important;
        }

        .metric-table-card tbody tr,
        .metric-table tbody tr {
            background: rgba(245, 246, 255, 0.20) !important;
        }

        .metric-table-card tbody tr:hover td:not(.metric-value-cell),
        .metric-table tbody tr:hover td:not(.metric-value-cell) {
            background: rgba(255, 255, 255, 0.35) !important;
        }

        .metric-table-card tbody tr:hover td.metric-value-cell,
        .metric-table tbody tr:hover td.metric-value-cell {
            color: var(--metric-color) !important;
            background: rgba(255, 255, 255, 0.35) !important;
        }

        /* ========================= */
        /* GLOBAL TEXT / METRICS */
        /* ========================= */

        .hero-title,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMetric"],
        [data-testid="stMetric"] * {
            color: #1f254f !important;
        }

        [data-testid="stMetricLabel"] {
            color: rgba(31, 37, 79, 0.72) !important;
        }

        [data-testid="stMetricValue"] {
            color: #1f254f !important;
        }

        /* Make the search placeholder text softer */
        .st-key-city_search_selectbox div[data-baseweb="select"] input::placeholder {
            color: rgba(31, 37, 79, 0.45) !important;
            opacity: 1 !important;
            font-weight: 600 !important;
        }

        /* Sometimes Streamlit/BaseWeb renders the placeholder as a div/span instead */
        .st-key-city_search_selectbox div[data-baseweb="select"] div,
        .st-key-city_search_selectbox div[data-baseweb="select"] span {
            color: rgba(31, 37, 79, 0.50) !important;
        }

        /* Vertically center selected city text inside the search bar */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div {
            display: flex !important;
            align-items: center !important;
        }

        /* Center the selected value / placeholder container */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div > div {
            display: flex !important;
            align-items: center !important;
            min-height: 100% !important;
        }

        /* Center the actual text input/value */
        .st-key-city_search_selectbox div[data-baseweb="select"] input,
        .st-key-city_search_selectbox div[data-baseweb="select"] span,
        .st-key-city_search_selectbox div[data-baseweb="select"] div {
            line-height: 1.1 !important;
        }

        /* Nudge the value down slightly if it still sits high */
        .st-key-city_search_selectbox div[data-baseweb="select"] div[role="combobox"] {
            transform: translateY(1px) !important;
        }

        /* Remove leftover top spacing */
        .block-container {
            padding-top: 1rem !important;
        }

        /* ========================= */
        /* SIMILAR CITY LINKS */
        /* ========================= */

        .similar-city-section {
            margin-top: 1.75rem;
            margin-bottom: 0.65rem;
        }

        .similar-city-section h4 {
            margin-bottom: 0.25rem;
            color: #1f254f;
            font-size: 1.35rem;
            font-weight: 850;
        }

        .similar-city-section p {
            margin-top: 0;
            margin-bottom: 0.75rem;
            color: rgba(31, 37, 79, 0.62);
            font-size: 0.95rem;
        }

        .similar-city-link {
            display: block !important;
            width: 100% !important;
            box-sizing: border-box !important;
            text-decoration: none !important;

            margin-bottom: 0.55rem !important;
            border-radius: 16px !important;
            border: 1px solid rgba(55, 65, 130, 0.22) !important;
            border-left: 5px solid rgba(70, 95, 190, 0.72) !important;

            background:
                linear-gradient(
                    90deg,
                    rgba(224, 230, 255, 0.96) 0%,
                    rgba(246, 248, 255, 0.90) 42%,
                    rgba(238, 242, 255, 0.76) 100%
                ) !important;

            color: #1f254f !important;
            min-height: 3.15rem !important;
            padding: 0.85rem 1rem !important;
            font-weight: 750 !important;
            letter-spacing: 0.005em !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.92),
                0 8px 18px rgba(35, 40, 100, 0.12) !important;

            transition:
                transform 0.16s ease,
                box-shadow 0.16s ease,
                border-color 0.16s ease,
                background 0.16s ease !important;
        }

        .similar-city-link:hover {
            border-color: rgba(55, 65, 130, 0.34) !important;
            border-left-color: rgba(31, 37, 79, 0.95) !important;

            background:
                linear-gradient(
                    90deg,
                    rgba(213, 222, 255, 1) 0%,
                    rgba(250, 251, 255, 0.98) 45%,
                    rgba(236, 241, 255, 0.92) 100%
                ) !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                0 14px 30px rgba(35, 40, 100, 0.18),
                0 0 0 3px rgba(90, 110, 210, 0.12) !important;

            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )