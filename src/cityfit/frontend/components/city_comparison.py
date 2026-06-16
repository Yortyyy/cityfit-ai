import pandas as pd
import streamlit as st

from cityfit.frontend.components.city_profile import get_metric_color
from cityfit.utils.countries import get_country_flag_url


COMPARISON_METRICS = {
    "cityfit_rank": ("CityFit Rank", True),
    "cityfit_score": ("CityFit Score", False),
    "purchasing_power_index": ("Purchasing Power", False),
    "cost_of_living_index": ("Cost of Living", True),
    "safety_index": ("Safety", False),
    "healthcare_index": ("Healthcare", False),
    "property_price_to_income_ratio": ("Housing Price to Income", True),
    "traffic_commute_index": ("Traffic Commute", True),
    "climate_index": ("Climate", False),
    "pollution_index": ("Pollution", True),
}

DIFFERENCE_COLUMN = "Difference From First City"
COMPARISON_WIDGET_KEY = "globe_city_comparison"
COMPARISON_TRACE_KEY = "globe_city_comparison_trace_labels"
COMPARISON_LAST_SELECTION_KEY = "globe_city_comparison_last_selection"


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
        return f"{int(second_value - first_value):+d}"

    return format_percent_difference(
        calculate_percent_difference(
            first_value=first_value,
            second_value=second_value,
        )
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
                "First Color": get_metric_color(
                    value=float(first_value),
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=lower_is_better,
                ),
                "Second Color": get_metric_color(
                    value=float(second_value),
                    min_value=min_value,
                    max_value=max_value,
                    lower_is_better=lower_is_better,
                ),
                "Difference Color": get_metric_color(
                    value=float(second_value),
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
    selected_city_labels = st.session_state.get(COMPARISON_WIDGET_KEY, [])

    if len(selected_city_labels) == 2:
        st.session_state[COMPARISON_TRACE_KEY] = list(selected_city_labels)
    else:
        st.session_state[COMPARISON_TRACE_KEY] = []


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

    if len(selected_city_labels) == 2 and current_selection != previous_selection:
        st.session_state[COMPARISON_LAST_SELECTION_KEY] = current_selection
        st.rerun()

    if len(selected_city_labels) < 2:
        st.session_state[COMPARISON_LAST_SELECTION_KEY] = current_selection

    if len(selected_city_labels) < 2:
        st.info("Choose two cities to compare their CityFit tradeoffs.")
        return

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
