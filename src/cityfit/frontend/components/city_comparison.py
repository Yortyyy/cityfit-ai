import pandas as pd
import streamlit as st

from cityfit.frontend.components.city_profile import get_metric_color


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

DIFFERENCE_BETTER_COLOR = "rgb(0, 95, 65)"
DIFFERENCE_WORSE_COLOR = "rgb(165, 45, 45)"
DIFFERENCE_TIE_COLOR = "rgb(31, 37, 79)"
DIFFERENCE_COLUMN = "Difference From First City"


def format_city_label(city: str, country: str) -> str:
    return f"{city}, {country}"


def split_city_label(city_label: str) -> tuple[str, str]:
    return city_label.rsplit(", ", 1)


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


def get_difference_color(
    first_value: float,
    second_value: float,
    lower_is_better: bool,
) -> str:
    if pd.isna(first_value) or pd.isna(second_value) or first_value == second_value:
        return DIFFERENCE_TIE_COLOR

    second_is_better = (
        second_value < first_value
        if lower_is_better
        else second_value > first_value
    )

    return DIFFERENCE_BETTER_COLOR if second_is_better else DIFFERENCE_WORSE_COLOR


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
                "Difference Color": get_difference_color(
                    first_value=float(first_value),
                    second_value=float(second_value),
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
        "<div class='metric-table-card'>"
        "<table class='metric-table'>"
        "<thead>"
        "<tr>"
        "<th>Metric</th>"
        f"<th>{first_city_label}</th>"
        f"<th>{second_city_label}</th>"
        f"<th>{DIFFERENCE_COLUMN}</th>"
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
    st.subheader("Compare Two Cities")

    city_options = get_city_options(globe_df)

    selected_city_labels = st.multiselect(
        "Choose exactly two cities",
        options=city_options,
        default=[],
        max_selections=2,
        key="globe_city_comparison",
    )

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
