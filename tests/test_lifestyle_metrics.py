from cityfit.lifestyle.load_lifestyle_metrics import load_lifestyle_metrics


def test_lifestyle_metrics_loads_with_required_columns():
    lifestyle_df = load_lifestyle_metrics()

    required_columns = [
        "city",
        "country",
        "latitude",
        "longitude",
        "daily_life_score",
        "food_scene_score",
        "nightlife_score",
        "culture_score",
        "outdoors_score",
        "transit_score",
        "airport_score",
        "friendliness_score",
        "pace_of_life",
        "lifestyle_score",
        "data_quality",
        "method_version",
    ]

    for column in required_columns:
        assert column in lifestyle_df.columns


def test_lifestyle_metrics_has_unique_city_country_rows():
    lifestyle_df = load_lifestyle_metrics()

    duplicates = lifestyle_df.duplicated(subset=["city", "country"])

    assert not duplicates.any()