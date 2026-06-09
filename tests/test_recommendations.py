from cityfit.api.schemas import UserProfile

from cityfit.recommendations.service import get_ranked_cities

def test_get_ranked_cities_returns_region_filtered_results():
    profile = UserProfile(region="Asia", top_n=5)

    ranked_df = get_ranked_cities(profile)

    assert len(ranked_df) > 0
    assert all(ranked_df["region"] == "Asia")