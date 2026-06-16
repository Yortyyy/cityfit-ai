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
        /* METHODOLOGY EXPANDER BOX  */
        /* ========================= */

        .methodology-card {
            margin-top: 1.1rem;
            margin-bottom: 0.25rem;
            padding: 0.9rem 1.15rem;

            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.58);

            background:
                linear-gradient(
                    135deg,
                    rgba(245, 246, 255, 0.58) 0%,
                    rgba(230, 235, 255, 0.30) 100%
                );

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.78),
                0 12px 28px rgba(35, 40, 100, 0.10);

            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }

        .methodology-card h3 {
            margin-top: 0;
            margin-bottom: 0.45rem;
            color: #1f254f;
            font-size: 1.05rem;
            font-weight: 850;
        }

        .methodology-card p {
            margin: 0;
            color: rgba(31, 37, 79, 0.68);
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .methodology-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.65rem;
        }

        .methodology-pill {
            display: inline-flex;
            align-items: center;

            padding: 0.22rem 0.52rem;
            border-radius: 999px;

            background: rgba(255, 255, 255, 0.30);
            border: 1px solid rgba(31, 37, 79, 0.08);

            color: rgba(31, 37, 79, 0.68);
            font-size: 0.74rem;
            font-weight: 700;
            line-height: 1.1;

            box-shadow: none;
        }

        /* ========================= */
        /* CITY SEARCH SELECTBOX ONLY */
        /* ========================= */

        .city-search-panel {
            margin-top: 1.15rem !important;
            margin-bottom: 0.45rem !important;
            padding-left: 0.8rem !important;
        }

        .city-search-panel .city-search-eyebrow {
            margin-bottom: 0.25rem !important;
            color: rgba(70, 75, 150, 0.74) !important;
            font-size: 0.70rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.18rem !important;
        }

        .city-search-panel h3 {
            margin: 0 !important;
            color: #1f254f !important;
            font-size: 1.45rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.05 !important;
        }

        .city-search-panel p {
            margin: 0.45rem 0 0 0 !important;
            max-width: 56rem !important;
            color: rgba(31, 37, 79, 0.68) !important;
            font-size: 0.95rem !important;
            font-weight: 620 !important;
            line-height: 1.45 !important;
        }

        /* Widget wrapper generated from key="city_search_selectbox" */
        .st-key-city_search_selectbox {
            position: relative !important;
            max-width: 100% !important;
            margin-top: 0.75rem !important;
            margin-bottom: 1.25rem !important;
        }

        /* Actual visible selectbox surface */
        .st-key-city_search_selectbox div[data-baseweb="select"] > div {
            min-height: 48px !important;
            border-radius: 16px !important;
            padding-left: 3rem !important;

            background:
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%231f254f' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'%3E%3C/circle%3E%3Cline x1='16.5' y1='16.5' x2='21' y2='21'%3E%3C/line%3E%3C/svg%3E") 1.05rem center / 18px 18px no-repeat,
                linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.88) 0%,
                    rgba(242, 245, 255, 0.66) 48%,
                    rgba(205, 214, 250, 0.46) 100%
                ) !important;

            border: 1px solid rgba(255, 255, 255, 0.95) !important;

            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -14px 24px rgba(85, 95, 175, 0.18),
                0 16px 34px rgba(35, 40, 100, 0.18),
                0 0 0 1px rgba(90, 105, 190, 0.16) !important;

            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
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
                inset 0 -14px 24px rgba(85, 95, 175, 0.24),
                0 20px 44px rgba(35, 40, 100, 0.23),
                0 0 0 3px rgba(92, 92, 255, 0.14) !important;
        }

        /* Dropdown arrow */
        .st-key-city_search_selectbox svg {
            color: #1f254f !important;
            fill: #1f254f !important;
        }

        /* ========================= */
        /* HERO TITLE */
        /* ========================= */

        .hero-title {
            margin-top: 0.25rem;
            margin-bottom: 0.65rem;
        }

        .hero-title .eyebrow {
            font-size: 0.72rem;
            letter-spacing: 0.22rem;
            color: rgba(30, 40, 80, 0.58);
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .hero-title h1 {
            font-size: 3.25rem;
            margin-top: 0;
            margin-bottom: 0.15rem;
            color: #1f254f;
            font-weight: 760;
            line-height: 1.02;
            letter-spacing: -0.045em;

            font-style: italic;
            transform: skewX(1deg);
            transform-origin: left center;

            text-shadow: 2px 2px 0 rgba(255,255,255,0.68);
        }

        .hero-title p {
            margin-top: 0.15rem;
            margin-bottom: 0;
            color: rgba(31, 37, 79, 0.78);
            font-size: 1.35rem;
            font-weight: 500;
            line-height: 1.2;
            letter-spacing: -0.015em;
        }
        
        .hero-bold {
            font-weight: 950;
        }

        .city-profile-section-heading {
            margin-top: 1.85rem !important;
            margin-bottom: 0.5rem !important;
            padding-left: 0.8rem !important;
        }

        .city-profile-section-heading .city-profile-eyebrow {
            margin-bottom: 0.25rem !important;
            color: rgba(70, 75, 150, 0.74) !important;
            font-size: 0.70rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.18rem !important;
            text-transform: uppercase !important;
        }

        .city-profile-section-heading h2 {
            margin: 0 !important;
            color: #1f254f !important;
            font-size: 1.85rem !important;
            font-weight: 950 !important;
            letter-spacing: -0.04em !important;
            line-height: 1.05 !important;
        }

        .city-profile-hero-card {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 1rem !important;
            margin-top: 0.6rem !important;
            margin-bottom: 1rem !important;
            padding: 0.76rem 1rem !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255, 255, 255, 0.64) !important;
            background:
                linear-gradient(
                    90deg,
                    rgba(245, 247, 255, 0.88) 0%,
                    rgba(226, 232, 255, 0.62) 55%,
                    rgba(239, 242, 255, 0.74) 100%
                ) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.82),
                0 10px 24px rgba(40, 40, 95, 0.12) !important;
            backdrop-filter: blur(8px) !important;
        }

        .city-profile-title-text {
            font-size: 30px;
            font-weight: 700;
            color: #08285a;
            line-height: 1.15;
            letter-spacing: -0.04em;
        }

        .city-profile-title-row {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            margin: 0;
            min-width: 0;
        }

        .city-profile-flag-box {
            width: 50px;
            height: 32px;

            display: flex;
            align-items: center;
            justify-content: center;

            flex: 0 0 50px;
        }

        .city-profile-flag-img {
            width: 50px !important;
            height: 32px !important;

            display: block !important;
            object-fit: cover !important;

            border-radius: 4px;
            box-shadow: 0 3px 8px rgba(20, 30, 60, 0.18);
        }

        .city-profile-summary-row {
            display: flex;
            justify-content: flex-end;
            flex-wrap: wrap;
            gap: 0.5rem;
            max-width: 46%;
        }

        .city-profile-summary-badge {
            min-width: 6.8rem;
            padding: 0.4rem 0.65rem;
            border-radius: 13px;
            border: 1px solid rgba(55, 65, 130, 0.14);
            background:
                linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.64) 0%,
                    rgba(232, 237, 255, 0.56) 100%
                );
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.78),
                0 5px 12px rgba(35, 40, 100, 0.08);
        }

        .city-profile-summary-badge span {
            display: block;
            margin-bottom: 0.12rem;
            color: rgba(31, 37, 79, 0.62);
            font-size: 0.66rem;
            font-weight: 850;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .city-profile-summary-badge strong {
            display: block;
            color: #1f254f;
            font-size: 1.18rem;
            font-weight: 950;
            line-height: 1.1;
            letter-spacing: -0.035em;
        }

        @media (max-width: 760px) {
            .city-profile-hero-card {
                align-items: stretch !important;
                flex-direction: column !important;
            }

            .city-profile-summary-row {
                justify-content: flex-start;
                max-width: none;
            }
        }

        .city-profile-summary-spacer {
            height: 0.65rem;
        }

        .city-profile-subsection-heading {
            margin: 0.7rem 0 0.45rem 0.8rem !important;
            color: #1f254f !important;
            font-size: 1.42rem !important;
            font-weight: 850 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.15 !important;
        }

        .city-profile-summary-copy {
            margin-left: 0.8rem;
            max-width: 58rem;
            color: #1f254f;
            font-size: 1rem;
            font-weight: 500;
            line-height: 1.55;
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

        .comparison-table {
            table-layout: fixed !important;
        }

        .comparison-metric-col {
            width: 22% !important;
        }

        .comparison-city-col {
            width: 31% !important;
        }

        .comparison-difference-col {
            width: 16% !important;
        }

        .comparison-city-header {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.55rem !important;
        }

        .comparison-flag-img {
            width: 30px !important;
            height: 20px !important;
            object-fit: cover !important;
            border-radius: 3px !important;
            box-shadow: 0 2px 5px rgba(20, 30, 60, 0.20) !important;
            flex: 0 0 30px !important;
        }

        .comparison-difference-header {
            font-size: 0.92rem !important;
            line-height: 1.15 !important;
        }

        .comparison-section-heading {
            margin-top: 2rem !important;
            margin-bottom: 0.45rem !important;
            padding-left: 0.8rem !important;
        }

        .comparison-section-heading .comparison-eyebrow {
            margin-bottom: 0.25rem !important;
            color: rgba(70, 75, 150, 0.74) !important;
            font-size: 0.70rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.18rem !important;
        }

        .comparison-section-heading h3 {
            margin: 0 !important;
            color: #1f254f !important;
            font-size: 1.45rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.05 !important;
        }

        .comparison-section-heading p {
            margin: 0.45rem 0 0 0 !important;
            max-width: 56rem !important;
            color: rgba(31, 37, 79, 0.68) !important;
            font-size: 0.95rem !important;
            font-weight: 620 !important;
            line-height: 1.45 !important;
        }

        .st-key-globe_city_comparison {
            position: relative !important;
            margin-top: 0.75rem !important;
            margin-bottom: 1.15rem !important;
        }

        .st-key-globe_city_comparison div[data-baseweb="select"] > div {
            min-height: 48px !important;
            border-radius: 16px !important;
            background:
                linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.88) 0%,
                    rgba(242, 245, 255, 0.66) 48%,
                    rgba(205, 214, 250, 0.46) 100%
                ) !important;
            border: 1px solid rgba(255, 255, 255, 0.96) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -14px 24px rgba(85, 95, 175, 0.18),
                0 16px 34px rgba(35, 40, 100, 0.18),
                0 0 0 1px rgba(90, 105, 190, 0.16) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
        }

        .st-key-globe_city_comparison div[data-baseweb="select"] > div:hover {
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 1),
                inset 0 -14px 24px rgba(85, 95, 175, 0.24),
                0 20px 44px rgba(35, 40, 100, 0.23),
                0 0 0 3px rgba(92, 92, 255, 0.14) !important;
        }

        .st-key-globe_city_comparison div[data-baseweb="select"],
        .st-key-globe_city_comparison div[data-baseweb="select"] > div > div,
        .st-key-globe_city_comparison div[data-baseweb="select"] input {
            background-color: transparent !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] {
            overflow: hidden !important;
            border-radius: 14px !important;
            background:
                linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.42) 0%,
                    rgba(225, 232, 255, 0.30) 100%
                ) !important;
            border: 1px solid rgba(255, 255, 255, 0.62) !important;
            color: #1f254f !important;
            min-height: 1.95rem !important;
            margin-top: 0.1rem !important;
            margin-bottom: 0.1rem !important;
            padding: 0.2rem 0.24rem 0.2rem 0.76rem !important;
            font-weight: 820 !important;
            letter-spacing: -0.01em !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.62),
                0 5px 12px rgba(35, 40, 100, 0.10) !important;
            backdrop-filter: blur(12px) saturate(1.2) !important;
            -webkit-backdrop-filter: blur(12px) saturate(1.2) !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"],
        .st-key-globe_city_comparison [data-baseweb="tag"] * {
            border-radius: 14px !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] > div,
        .st-key-globe_city_comparison [data-baseweb="tag"] > span {
            background-color: transparent !important;
            background-image: none !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] span {
            color: #1f254f !important;
            line-height: 1.05 !important;
            background: transparent !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] button,
        .st-key-globe_city_comparison [data-baseweb="tag"] div[role="button"],
        .st-key-globe_city_comparison [data-baseweb="tag"] [aria-label*="emove"],
        .st-key-globe_city_comparison [data-baseweb="tag"] [title*="emove"] {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 1.12rem !important;
            height: 1.12rem !important;
            min-width: 1.12rem !important;
            border-radius: 10px !important;
            margin-left: 0.32rem !important;
            border: 1px solid rgba(255, 255, 255, 0.38) !important;
            background: rgba(255, 255, 255, 0.22) !important;
            color: rgba(31, 37, 79, 0.58) !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.40) !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] button:hover,
        .st-key-globe_city_comparison [data-baseweb="tag"] div[role="button"]:hover,
        .st-key-globe_city_comparison [data-baseweb="tag"] [aria-label*="emove"]:hover,
        .st-key-globe_city_comparison [data-baseweb="tag"] [title*="emove"]:hover {
            background: rgba(255, 255, 255, 0.44) !important;
            color: rgba(31, 37, 79, 0.74) !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] svg,
        .st-key-globe_city_comparison [data-baseweb="tag"] button svg,
        .st-key-globe_city_comparison [data-baseweb="tag"] [role="button"] svg,
        .st-key-globe_city_comparison [data-baseweb="tag"] [aria-label*="emove"] svg {
            width: 0.66rem !important;
            height: 0.66rem !important;
            color: currentColor !important;
            fill: currentColor !important;
            stroke: currentColor !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] :is(button, div, span):has(svg) {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 1.12rem !important;
            height: 1.12rem !important;
            min-width: 1.12rem !important;
            margin-left: 0.32rem !important;
            border-radius: 10px !important;
            background: rgba(255, 255, 255, 0.24) !important;
            color: rgba(31, 37, 79, 0.58) !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] :is(button, div, span):has(svg):hover {
            background: rgba(255, 255, 255, 0.46) !important;
            color: rgba(31, 37, 79, 0.76) !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] svg path {
            fill: currentColor !important;
            stroke: currentColor !important;
        }

        .st-key-globe_city_comparison [data-baseweb="tag"] button svg,
        .st-key-globe_city_comparison [data-baseweb="tag"] div[role="button"] svg {
            transform: scale(0.78) !important;
            opacity: 0.72 !important;
        }

        .st-key-globe_city_comparison div[data-baseweb="select"] div,
        .st-key-globe_city_comparison div[data-baseweb="select"] span,
        .st-key-globe_city_comparison div[data-baseweb="select"] input {
            color: #1f254f !important;
            font-weight: 720 !important;
        }

        .st-key-globe_city_comparison div[data-baseweb="select"] input {
            min-height: 1.4rem !important;
            line-height: 1.4rem !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            transform: translateY(2px) !important;
        }

        .st-key-globe_city_comparison_swap {
            margin-top: -0.65rem !important;
            margin-bottom: 0.15rem !important;
        }

        .st-key-globe_city_comparison_swap button {
            min-height: 2.35rem !important;
            border-radius: 999px !important;
            border: 1px solid rgba(92, 92, 255, 0.24) !important;
            background:
                linear-gradient(
                    90deg,
                    rgba(232, 237, 255, 0.90) 0%,
                    rgba(246, 248, 255, 0.82) 100%
                ) !important;
            color: #1f254f !important;
            font-size: 0.9rem !important;
            font-weight: 820 !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.88),
                0 7px 16px rgba(35, 40, 100, 0.10) !important;
        }

        .st-key-globe_city_comparison_swap button:hover {
            border-color: rgba(92, 92, 255, 0.42) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.95),
                0 10px 22px rgba(35, 40, 100, 0.15),
                0 0 0 3px rgba(92, 92, 255, 0.12) !important;
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
            margin-bottom: 0.75rem;
            padding-left: 0.8rem;
        }

        .similar-city-section .similar-city-eyebrow {
            margin-bottom: 0.25rem;
            color: rgba(70, 75, 150, 0.74);
            font-size: 0.70rem;
            font-weight: 900;
            letter-spacing: 0.18rem;
            text-transform: uppercase;
        }

        .similar-city-section h4 {
            margin: 0;
            color: #1f254f;
            font-size: 1.45rem;
            font-weight: 900;
            letter-spacing: -0.035rem;
        }

        .similar-city-section p {
            max-width: 56rem;
            margin: 0.42rem 0 0 0;
            color: rgba(31, 37, 79, 0.68);
            font-size: 0.95rem;
            font-weight: 620;
            line-height: 1.45;
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
