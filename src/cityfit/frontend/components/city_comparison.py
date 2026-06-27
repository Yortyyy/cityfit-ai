import pandas as pd
import streamlit as st

from cityfit.frontend.components.city_profile import (
    get_metric_color,
    get_metric_color_for_column,
)
from cityfit.utils.countries import get_country_flag_url


COMPARISON_METRICS = {
    "cityfit_rank": ("CityFit Rank", True),
    "cityfit_score": ("CityFit Score", False),
    "practical_score": ("Practical Fit", False),
    "lifestyle_fit_score": ("Lifestyle Fit", False),
    "purchasing_power_index": ("Purchasing Power", False),
    "cost_of_living_index": ("Cost of Living", True),
    "safety_index": ("Safety", False),
    "healthcare_index": ("Healthcare", False),
    "property_price_to_income_ratio": ("Housing to Income Ratio", True),
    "traffic_commute_index": ("Traffic", True),
    "climate_index": ("Climate", False),
    "pollution_index": ("Pollution", True),
    "daily_life_score": ("Daily Life", False),
    "food_scene_score": ("Food Scene", False),
    "culture_score": ("Culture", False),
    "outdoors_score": ("Outdoors", False),
    "transit_score": ("Transit", False),
    "airport_score": ("Airport Access", False),
    "nightlife_score": ("Nightlife", False),
}

DIFFERENCE_COLUMN = "Difference From First City"
COMPARISON_WIDGET_KEY = "globe_city_comparison"
COMPARISON_TRACE_KEY = "globe_city_comparison_trace_labels"
COMPARISON_LAST_SELECTION_KEY = "globe_city_comparison_last_selection"
COMPARISON_SWAP_BUTTON_KEY = "globe_city_comparison_swap"


def format_city_label(city: str, country: str) -> str:
    return f"{city}, {country}"


def split_city_label(city_label: str) -> tuple[str, str]:
    return city_label.rsplit(", ", 1)


def render_city_header(city_label: str) -> str:
    city, country = split_city_label(city_label)
    flag_url = get_country_flag_url(country, size=80)

    if not flag_url:
        return city_label

    return (
        "<span class='comparison-city-header'>"
        f"<span>{city}, {country}</span>"
        f"<img src='{flag_url}' class='comparison-flag-img' alt='{country} flag' />"
        "</span>"
    )


def get_city_row(globe_df: pd.DataFrame, city_label: str) -> pd.Series | None:
    city, country = split_city_label(city_label)

    matches = globe_df[
        (globe_df["city"] == city)
        & (globe_df["country"] == country)
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


def calculate_percent_difference(
    first_value: float,
    second_value: float,
) -> float | None:
    if pd.isna(first_value) or pd.isna(second_value) or first_value == 0:
        return None

    return ((second_value - first_value) / abs(first_value)) * 100


def format_percent_difference(percent_difference: float | None) -> str:
    if percent_difference is None:
        return "N/A"

    return f"{percent_difference:+.1f}%"


def format_metric_value(column: str, value: float) -> str:
    if column == "cityfit_rank":
        return f"#{int(value)}"

    return f"{value:.1f}"


def format_difference(column: str, first_value: float, second_value: float) -> str:
    if column == "cityfit_rank":
        rank_change = int(-(second_value - first_value))

        if rank_change > 0:
            return f"↑ {abs(rank_change)}"

        if rank_change < 0:
            return f"↓ {abs(rank_change)}"

        return "→ 0"

    return format_percent_difference(
        calculate_percent_difference(
            first_value=first_value,
            second_value=second_value,
        )
    )


def get_rank_difference_color(
    first_rank: float,
    second_rank: float,
    min_rank: float,
    max_rank: float,
) -> str:
    if (
        pd.isna(first_rank)
        or pd.isna(second_rank)
        or pd.isna(min_rank)
        or pd.isna(max_rank)
        or max_rank == min_rank
    ):
        return get_metric_color(
            value=0.5,
            min_value=0,
            max_value=1,
        )

    rank_range = max_rank - min_rank
    rank_delta = second_rank - first_rank
    normalized_difference = 0.5 - (rank_delta / (2 * rank_range))
    normalized_difference = max(0.0, min(1.0, normalized_difference))

    return get_metric_color(
        value=normalized_difference,
        min_value=0,
        max_value=1,
    )


def get_percent_difference_color(
    first_value: float,
    second_value: float,
    min_value: float,
    max_value: float,
    lower_is_better: bool,
) -> str:
    percent_difference = calculate_percent_difference(
        first_value=first_value,
        second_value=second_value,
    )

    if (
        percent_difference is None
        or pd.isna(min_value)
        or pd.isna(max_value)
        or max_value == min_value
    ):
        return get_metric_color(value=0.5, min_value=0, max_value=1)

    best_value = min_value if lower_is_better else max_value
    worst_value = max_value if lower_is_better else min_value

    best_percent_difference = calculate_percent_difference(
        first_value=first_value,
        second_value=best_value,
    )
    worst_percent_difference = calculate_percent_difference(
        first_value=first_value,
        second_value=worst_value,
    )

    if best_percent_difference is None or worst_percent_difference is None:
        return get_metric_color(value=0.5, min_value=0, max_value=1)

    movement = -percent_difference if lower_is_better else percent_difference
    best_movement = (
        -best_percent_difference if lower_is_better else best_percent_difference
    )
    worst_movement = (
        -worst_percent_difference if lower_is_better else worst_percent_difference
    )

    if movement >= 0:
        max_better_movement = max(best_movement, 0)
        normalized_difference = (
            0.5
            if max_better_movement == 0
            else 0.5 + (0.5 * movement / max_better_movement)
        )
    else:
        max_worse_movement = abs(min(worst_movement, 0))
        normalized_difference = (
            0.5
            if max_worse_movement == 0
            else 0.5 + (0.5 * movement / max_worse_movement)
        )

    normalized_difference = max(0.0, min(1.0, normalized_difference))

    return get_metric_color(
        value=normalized_difference,
        min_value=0,
        max_value=1,
    )


def get_difference_color(
    column: str,
    first_value: float,
    second_value: float,
    min_value: float,
    max_value: float,
    lower_is_better: bool,
) -> str:
    if column == "cityfit_rank":
        return get_rank_difference_color(
            first_rank=first_value,
            second_rank=second_value,
            min_rank=min_value,
            max_rank=max_value,
        )

    return get_percent_difference_color(
        first_value=first_value,
        second_value=second_value,
        min_value=min_value,
        max_value=max_value,
        lower_is_better=lower_is_better,
    )


def build_city_comparison_table(
    globe_df: pd.DataFrame,
    all_df: pd.DataFrame,
    first_city_label: str,
    second_city_label: str,
) -> pd.DataFrame:
    first_city = get_city_row(globe_df, first_city_label)
    second_city = get_city_row(globe_df, second_city_label)

    if first_city is None or second_city is None:
        return pd.DataFrame()

    rows = []

    for column, (label, lower_is_better) in COMPARISON_METRICS.items():
        if column not in first_city.index or column not in second_city.index:
            continue

        if column not in all_df.columns:
            continue

        first_value = first_city[column]
        second_value = second_city[column]
        min_value = float(all_df[column].min())
        max_value = float(all_df[column].max())

        rows.append(
            {
                "Metric": label,
                first_city_label: format_metric_value(
                    column=column,
                    value=float(first_value),
                ),
                second_city_label: format_metric_value(
                    column=column,
                    value=float(second_value),
                ),
                DIFFERENCE_COLUMN: format_difference(
                    column=column,
                    first_value=float(first_value),
                    second_value=float(second_value),
                ),
                "First Color": get_metric_color_for_column(
                    column=column,
                    value=float(first_value),
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=lower_is_better,
                ),
                "Second Color": get_metric_color_for_column(
                    column=column,
                    value=float(second_value),
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=lower_is_better,
                ),
                "Difference Color": get_difference_color(
                    column=column,
                    first_value=float(first_value),
                    second_value=float(second_value),
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=lower_is_better,
                ),
            }
        )

    return pd.DataFrame(rows)


def get_city_options(globe_df: pd.DataFrame) -> list[str]:
    city_options_df = (
        globe_df[["city", "country"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["city", "country"])
    )

    return [
        format_city_label(row.city, row.country)
        for row in city_options_df.itertuples(index=False)
    ]


def sync_comparison_trace_selection() -> None:
    st.session_state[COMPARISON_TRACE_KEY] = get_comparison_trace_labels()


def get_comparison_trace_labels() -> list[str]:
    selected_city_labels = st.session_state.get(COMPARISON_WIDGET_KEY, [])

    if len(selected_city_labels) == 2:
        return list(selected_city_labels)

    return []


def has_active_comparison_selection() -> bool:
    return len(st.session_state.get(COMPARISON_WIDGET_KEY, [])) > 0


def swap_comparison_city_order() -> None:
    selected_city_labels = st.session_state.get(COMPARISON_WIDGET_KEY, [])

    if len(selected_city_labels) != 2:
        return

    swapped_city_labels = list(reversed(selected_city_labels))

    st.session_state[COMPARISON_WIDGET_KEY] = swapped_city_labels
    st.session_state[COMPARISON_TRACE_KEY] = swapped_city_labels
    st.session_state[COMPARISON_LAST_SELECTION_KEY] = tuple(swapped_city_labels)


def render_comparison_table(
    comparison_df: pd.DataFrame,
    first_city_label: str,
    second_city_label: str,
) -> None:
    rows_html = ""

    for _, row in comparison_df.iterrows():
        rows_html += (
            "<tr>"
            f"<td>{row['Metric']}</td>"
            f"<td class='metric-value-cell' style='--metric-color: {row['First Color']};'>"
            f"{row[first_city_label]}"
            "</td>"
            f"<td class='metric-value-cell' style='--metric-color: {row['Second Color']};'>"
            f"{row[second_city_label]}"
            "</td>"
            f"<td class='metric-value-cell' style='--metric-color: {row['Difference Color']};'>"
            f"{row[DIFFERENCE_COLUMN]}"
            "</td>"
            "</tr>"
        )

    table_html = (
        "<div class='metric-table-card comparison-table-card'>"
        "<table class='metric-table comparison-table'>"
        "<colgroup>"
        "<col class='comparison-metric-col' />"
        "<col class='comparison-city-col' />"
        "<col class='comparison-city-col' />"
        "<col class='comparison-difference-col' />"
        "</colgroup>"
        "<thead>"
        "<tr>"
        "<th>Metric</th>"
        f"<th>{render_city_header(first_city_label)}</th>"
        f"<th>{render_city_header(second_city_label)}</th>"
        f"<th class='comparison-difference-header'>{DIFFERENCE_COLUMN}</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        f"{rows_html}"
        "</tbody>"
        "</table>"
        "</div>"
    )

    st.markdown(table_html, unsafe_allow_html=True)


def render_selected_city_pill_flag_styles(selected_city_labels: list[str]) -> None:
    if len(selected_city_labels) != 2:
        return

    style_rules = []

    for index, city_label in enumerate(selected_city_labels, start=1):
        _, country = split_city_label(city_label)
        flag_url = get_country_flag_url(country, size=160)

        if not flag_url:
            continue

        style_rules.append(
            f"""
            .st-key-globe_city_comparison [data-baseweb="tag"]:nth-of-type({index}) {{
                position: relative !important;
                overflow: hidden !important;

                background:
                    linear-gradient(
                        90deg,
                        rgba(255, 255, 255, 0.72) 0%,
                        rgba(232, 237, 255, 0.58) 100%
                    ) !important;
            }}

            .st-key-globe_city_comparison [data-baseweb="tag"]:nth-of-type({index})::before {{
                content: "" !important;
                position: absolute !important;

                left: -0.35rem !important;
                top: 50% !important;

                width: 3.35rem !important;
                height: 2.15rem !important;

                background: url("{flag_url}") center / cover no-repeat !important;
                border-radius: 4px !important;

                transform: translateY(-50%) rotate(-10deg) !important;
                transform-origin: center !important;

                opacity: 0.82 !important;
                box-shadow: 0 3px 8px rgba(20, 30, 60, 0.20) !important;
                z-index: 0 !important;
                
                -webkit-mask-image: linear-gradient(
                    90deg,
                    black 0%,
                    black 58%,
                    transparent 100%
                ) !important;
                mask-image: linear-gradient(
                    90deg,
                    black 0%,
                    black 58%,
                    transparent 100%
                ) !important;
            }}

            .st-key-globe_city_comparison [data-baseweb="tag"]:nth-of-type({index})::after {{
                content: "" !important;
                position: absolute !important;
                inset: 0 !important;

                background:
                    linear-gradient(
                        90deg,
                        rgba(255, 255, 255, 0.38) 0%,
                        rgba(255, 255, 255, 0.72) 38%,
                        rgba(232, 237, 255, 0.64) 100%
                    ) !important;

                z-index: 1 !important;
                pointer-events: none !important;
            }}

            .st-key-globe_city_comparison [data-baseweb="tag"]:nth-of-type({index}) > * {{
                position: relative !important;
                z-index: 2 !important;
            }}
            """
        )

    if not style_rules:
        return

    st.markdown(
        f"<style>{''.join(style_rules)}</style>",
        unsafe_allow_html=True,
    )


def render_city_comparison(globe_df: pd.DataFrame, all_df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="comparison-section-heading">
            <div class="comparison-eyebrow">SIDE BY SIDE</div>
            <h3>Compare Two Cities</h3>
            <p>
                Choose two cities from the current globe view. CityFit will highlight them
                on the map and compare each metric against the first city you select.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    city_options = get_city_options(globe_df)
    previous_selection = tuple(
        st.session_state.get(COMPARISON_LAST_SELECTION_KEY, [])
    )

    selected_city_labels = st.multiselect(
        "Choose exactly two cities",
        options=city_options,
        default=[],
        max_selections=2,
        placeholder="Select two cities to compare...",
        key=COMPARISON_WIDGET_KEY,
        on_change=sync_comparison_trace_selection,
        label_visibility="collapsed",
    )

    current_selection = tuple(selected_city_labels)
    sync_comparison_trace_selection()
    render_selected_city_pill_flag_styles(selected_city_labels)

    if len(selected_city_labels) == 2 and current_selection != previous_selection:
        st.session_state[COMPARISON_LAST_SELECTION_KEY] = current_selection
        st.rerun()

    if len(selected_city_labels) < 2:
        st.session_state[COMPARISON_LAST_SELECTION_KEY] = current_selection

    if len(selected_city_labels) < 2:
        st.info("Choose two cities to compare their CityFit tradeoffs.")
        return

    st.button(
        "Swap",
        help="Switch which city is used as the baseline.",
        key=COMPARISON_SWAP_BUTTON_KEY,
        on_click=swap_comparison_city_order,
    )

    first_city_label, second_city_label = selected_city_labels

    comparison_df = build_city_comparison_table(
        globe_df=globe_df,
        all_df=all_df,
        first_city_label=first_city_label,
        second_city_label=second_city_label,
    )

    if comparison_df.empty:
        st.warning("Could not compare the selected cities.")
        return

    render_comparison_table(
        comparison_df=comparison_df,
        first_city_label=first_city_label,
        second_city_label=second_city_label,
    )
