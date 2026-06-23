import pandas as pd

from cityfit.lifestyle.load_lifestyle_metrics import load_lifestyle_metrics


def add_lifestyle_metrics(city_df: pd.DataFrame) -> pd.DataFrame:
    lifestyle_df = load_lifestyle_metrics()

    lifestyle_columns = [
        "city",
        "country",
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

    return city_df.merge(
        lifestyle_df[lifestyle_columns],
        on=["city", "country"],
        how="left",
    )