import pandas as pd

from cityfit.frontend.components.city_comparison import (
    COMPARISON_TRACE_KEY,
    COMPARISON_WIDGET_KEY,
    DIFFERENCE_COLUMN,
    build_city_comparison_table,
    calculate_percent_difference,
    format_difference,
    get_comparison_trace_labels,
    has_active_comparison_selection,
    get_percent_difference_color,
    get_rank_difference_color,
    render_city_header,
    swap_comparison_city_order,
    sync_comparison_trace_selection,
)
from cityfit.frontend.components.city_profile import get_metric_color
from cityfit.frontend.components.city_profile import get_metric_color_for_column


def make_comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["Tampa", "Tokyo"],
            "country": ["United States", "Japan"],
            "cityfit_score": [133.3, 132.1],
            "cityfit_rank": [57, 69],
            "practical_score": [130.0, 125.0],
            "lifestyle_fit_score": [120.0, 135.0],
            "purchasing_power_index": [110.0, 95.0],
            "cost_of_living_index": [70.0, 60.0],
            "safety_index": [55.0, 80.0],
            "healthcare_index": [70.0, 85.0],
            "property_price_to_income_ratio": [5.0, 12.0],
            "traffic_commute_index": [35.0, 45.0],
            "climate_index": [90.0, 85.0],
            "pollution_index": [25.0, 20.0],
        }
    )


def test_build_city_comparison_table_includes_percent_difference_from_first_city():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    score_row = comparison[comparison["Metric"] == "CityFit Score"].iloc[0]

    assert score_row[DIFFERENCE_COLUMN] == "-0.9%"


def test_build_city_comparison_table_displays_rank_first_with_hashmark():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    rank_row = comparison.iloc[0]

    assert rank_row["Metric"] == "CityFit Rank"
    assert rank_row["Tampa, United States"] == "#57"
    assert rank_row["Tokyo, Japan"] == "#69"
    assert rank_row[DIFFERENCE_COLUMN] == "↓ 12"


def test_build_city_comparison_table_omits_stronger_fit_column():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    assert "Stronger Fit" not in comparison.columns


def test_build_city_comparison_table_colors_values_from_global_scale():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    cost_row = comparison[comparison["Metric"] == "Cost of Living"].iloc[0]

    assert cost_row["First Color"] != cost_row["Second Color"]


def test_build_city_comparison_table_labels_and_colors_housing_ratio_by_severity():
    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=make_comparison_df(),
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    housing_row = comparison[
        comparison["Metric"] == "Housing to Income Ratio"
    ].iloc[0]

    assert housing_row["Tampa, United States"] == "5.0"
    assert housing_row["Tokyo, Japan"] == "12.0"
    assert housing_row["First Color"] == get_metric_color_for_column(
        column="property_price_to_income_ratio",
        value=5.0,
        min_value=5.0,
        max_value=12.0,
        lower_is_better=True,
    )
    assert housing_row["First Color"] != housing_row["Second Color"]


def test_build_city_comparison_table_colors_percent_difference_from_movement():
    global_scale_df = pd.concat(
        [
            make_comparison_df(),
            pd.DataFrame(
                [
                    {
                        "cityfit_rank": 300,
                        "cityfit_score": 100.0,
                        "practical_score": 100.0,
                        "lifestyle_fit_score": 100.0,
                        "purchasing_power_index": 50.0,
                        "cost_of_living_index": 100.0,
                        "safety_index": 0.0,
                        "healthcare_index": 30.0,
                        "property_price_to_income_ratio": 20.0,
                        "traffic_commute_index": 90.0,
                        "climate_index": 10.0,
                        "pollution_index": 90.0,
                    },
                    {
                        "cityfit_rank": 1,
                        "cityfit_score": 200.0,
                        "practical_score": 200.0,
                        "lifestyle_fit_score": 200.0,
                        "purchasing_power_index": 200.0,
                        "cost_of_living_index": 0.0,
                        "safety_index": 100.0,
                        "healthcare_index": 100.0,
                        "property_price_to_income_ratio": 1.0,
                        "traffic_commute_index": 0.0,
                        "climate_index": 100.0,
                        "pollution_index": 0.0,
                    },
                ]
            ),
        ],
        ignore_index=True,
    )

    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=global_scale_df,
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    safety_row = comparison[comparison["Metric"] == "Safety"].iloc[0]

    assert safety_row["Difference Color"] != safety_row["Second Color"]


def test_percent_difference_color_uses_midpoint_for_no_changeformat_city_():
    same_value_color = get_percent_difference_color(
        first_value=50,
        second_value=50,
        min_value=0,
        max_value=100,
        lower_is_better=False,
    )
    midpoint_color = get_metric_color(value=0.5, min_value=0, max_value=1)

    assert same_value_color == midpoint_color


def test_percent_difference_color_gets_better_or_worse_from_first_city():
    better_color = get_percent_difference_color(
        first_value=50,
        second_value=75,
        min_value=0,
        max_value=100,
        lower_is_better=False,
    )
    worse_color = get_percent_difference_color(
        first_value=50,
        second_value=25,
        min_value=0,
        max_value=100,
        lower_is_better=False,
    )

    assert better_color != worse_color


def test_percent_difference_color_flips_for_lower_is_better_metrics():
    better_color = get_percent_difference_color(
        first_value=50,
        second_value=25,
        min_value=0,
        max_value=100,
        lower_is_better=True,
    )
    worse_color = get_percent_difference_color(
        first_value=50,
        second_value=75,
        min_value=0,
        max_value=100,
        lower_is_better=True,
    )

    assert better_color != worse_color


def test_rank_difference_color_uses_midpoint_for_same_rank():
    same_rank_color = get_rank_difference_color(
        first_rank=57,
        second_rank=57,
        min_rank=1,
        max_rank=300,
    )
    midpoint_color = get_metric_color(value=0.5, min_value=0, max_value=1)

    assert same_rank_color == midpoint_color


def test_rank_difference_color_gets_better_or_worse_from_first_city():
    better_rank_color = get_rank_difference_color(
        first_rank=57,
        second_rank=27,
        min_rank=1,
        max_rank=300,
    )
    worse_rank_color = get_rank_difference_color(
        first_rank=57,
        second_rank=87,
        min_rank=1,
        max_rank=300,
    )

    assert better_rank_color != worse_rank_color


def test_build_city_comparison_table_colors_rank_difference_from_rank_movement():
    global_scale_df = pd.concat(
        [
            make_comparison_df(),
            pd.DataFrame(
                [
                    {
                        "cityfit_rank": 300,
                        "cityfit_score": 100.0,
                        "practical_score": 100.0,
                        "lifestyle_fit_score": 100.0,
                        "purchasing_power_index": 50.0,
                        "cost_of_living_index": 100.0,
                        "safety_index": 20.0,
                        "healthcare_index": 30.0,
                        "property_price_to_income_ratio": 20.0,
                        "traffic_commute_index": 90.0,
                        "climate_index": 10.0,
                        "pollution_index": 90.0,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    comparison = build_city_comparison_table(
        globe_df=make_comparison_df(),
        all_df=global_scale_df,
        first_city_label="Tampa, United States",
        second_city_label="Tokyo, Japan",
    )

    rank_row = comparison[comparison["Metric"] == "CityFit Rank"].iloc[0]

    assert rank_row["Difference Color"] != rank_row["Second Color"]


def test_calculate_percent_difference_uses_first_city_as_baseline():
    assert calculate_percent_difference(first_value=50, second_value=75) == 50


def test_format_difference_uses_better_worse_sign_for_rank():
    assert format_difference(column="cityfit_rank", first_value=57, second_value=69) == "↓ 12"


def test_render_city_header_includes_country_flag():
    header_html = render_city_header("Tampa, United States")

    assert "flagcdn.com" in header_html
    assert "United States flag" in header_html
    assert "Tampa, United States" in header_html


def test_sync_comparison_trace_selection_clears_trace_state_when_less_than_two_selected():
    import streamlit as st

    st.session_state[COMPARISON_WIDGET_KEY] = ["Tampa, United States"]
    st.session_state[COMPARISON_TRACE_KEY] = ["Tampa, United States", "Tokyo, Japan"]

    sync_comparison_trace_selection()

    assert st.session_state[COMPARISON_TRACE_KEY] == []


def test_get_comparison_trace_labels_ignores_stale_trace_selection():
    import streamlit as st

    st.session_state[COMPARISON_WIDGET_KEY] = []
    st.session_state[COMPARISON_TRACE_KEY] = ["Tampa, United States", "Tokyo, Japan"]

    assert get_comparison_trace_labels() == []


def test_has_active_comparison_selection_tracks_partial_and_complete_selection():
    import streamlit as st

    st.session_state[COMPARISON_WIDGET_KEY] = []

    assert not has_active_comparison_selection()

    st.session_state[COMPARISON_WIDGET_KEY] = ["Tampa, United States"]

    assert has_active_comparison_selection()

    st.session_state[COMPARISON_WIDGET_KEY] = [
        "Tampa, United States",
        "Tokyo, Japan",
    ]

    assert has_active_comparison_selection()


def test_sync_comparison_trace_selection_sets_trace_state_for_two_selected():
    import streamlit as st

    selected_cities = ["Tampa, United States", "Tokyo, Japan"]
    st.session_state[COMPARISON_WIDGET_KEY] = selected_cities

    sync_comparison_trace_selection()

    assert st.session_state[COMPARISON_TRACE_KEY] == selected_cities


def test_swap_comparison_city_order_reverses_selected_city_priority():
    import streamlit as st

    selected_cities = ["Tampa, United States", "Tokyo, Japan"]
    st.session_state[COMPARISON_WIDGET_KEY] = selected_cities
    st.session_state[COMPARISON_TRACE_KEY] = selected_cities

    swap_comparison_city_order()

    assert st.session_state[COMPARISON_WIDGET_KEY] == [
        "Tokyo, Japan",
        "Tampa, United States",
    ]
    assert st.session_state[COMPARISON_TRACE_KEY] == [
        "Tokyo, Japan",
        "Tampa, United States",
    ]


def test_swap_comparison_city_order_ignores_partial_selection():
    import streamlit as st

    selected_cities = ["Tampa, United States"]
    st.session_state[COMPARISON_WIDGET_KEY] = selected_cities
    st.session_state[COMPARISON_TRACE_KEY] = []

    swap_comparison_city_order()

    assert st.session_state[COMPARISON_WIDGET_KEY] == selected_cities
    assert st.session_state[COMPARISON_TRACE_KEY] == []
