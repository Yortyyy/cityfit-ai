import pandas as pd

from cityfit.frontend.components.globe_chart import (
    COMPARISON_BLUE_TRANSLUCENT,
    COMPARISON_LINE_POINTS,
    build_globe_figure,
    get_comparison_cities_df,
    interpolate_lateral_path,
)


def make_globe_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["Tampa", "Tokyo", "Rome"],
            "country": ["United States", "Japan", "Italy"],
            "region": ["North America", "Asia", "Europe"],
            "latitude": [27.9, 35.7, 41.9],
            "longitude": [-82.5, 139.7, 12.5],
            "cityfit_score": [133.3, 132.1, 120.0],
            "cityfit_rank": [57, 69, 185],
        }
    )


def test_get_comparison_cities_df_preserves_selected_order():
    comparison_df = get_comparison_cities_df(
        globe_df=make_globe_df(),
        comparison_city_labels=[
            "Tokyo, Japan",
            "Tampa, United States",
        ],
    )

    assert comparison_df["city"].tolist() == ["Tokyo", "Tampa"]


def test_build_globe_figure_layers_active_marker_after_comparison_markers():
    fig = build_globe_figure(
        globe_df=make_globe_df(),
        all_df=make_globe_df(),
        focused_city="Rome",
        focused_country="Italy",
        comparison_city_labels=[
            "Tokyo, Japan",
            "Tampa, United States",
        ],
    )

    assert len(fig.data) == 6
    assert fig.data[2].marker.line.color == COMPARISON_BLUE_TRANSLUCENT
    assert fig.data[-1].marker.color == "rgb(255, 255, 255)"
    assert fig.data[-2].marker.line.color == "rgba(31, 37, 79, 0.95)"


def test_interpolate_lateral_path_uses_requested_number_of_points():
    lats, lons = interpolate_lateral_path(
        start_lat=35.7,
        start_lon=139.7,
        end_lat=27.9,
        end_lon=-82.5,
    )

    assert len(lats) == COMPARISON_LINE_POINTS
    assert len(lons) == COMPARISON_LINE_POINTS
    assert lats[0] == 35.7
    assert lats[-1] == 27.9


def test_build_globe_figure_uses_interpolated_comparison_line():
    fig = build_globe_figure(
        globe_df=make_globe_df(),
        all_df=make_globe_df(),
        comparison_city_labels=[
            "Tokyo, Japan",
            "Tampa, United States",
        ],
    )

    assert len(fig.data[1].lat) == COMPARISON_LINE_POINTS
