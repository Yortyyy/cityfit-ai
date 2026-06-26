import pandas as pd

from cityfit.lifestyle.load_lifestyle_metrics import load_lifestyle_metrics
from cityfit.lifestyle.merge_lifestyle_metrics import add_lifestyle_metrics



def test_lifestyle_metrics_loads_with_required_columns():
    lifestyle_df = load_lifestyle_metrics()

    required_columns = [
        "city",
        "country",
        "latitude",
        "longitude",
        "daily_life_score",
        "food_scene_score",
        "culture_score",
        "outdoors_score",
        "transit_score",
        "airport_score",
        "nightlife_score",
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
    
def test_lifestyle_metrics_can_merge_onto_city_data():
    city_df = pd.DataFrame(
        [
            {
                "city": "Tampa",
                "country": "United States",
                "cityfit_score": 133.3,
            }
        ]
    )

    merged_df = add_lifestyle_metrics(city_df)

    assert "daily_life_score" in merged_df.columns
    assert "food_scene_score" in merged_df.columns
    assert "airport_score" in merged_df.columns
    assert "method_version" in merged_df.columns
