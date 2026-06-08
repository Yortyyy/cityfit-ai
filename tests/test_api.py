from fastapi.testclient import TestClient

from cityfit.api.main import app
from cityfit.api.schemas import UserProfile


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommend_endpoint_returns_recommendations():
    payload = {
        "priority_safety": 1.0,
        "priority_healthcare": 1.0,
        "priority_climate": 0.8,
        "priority_purchasing_power": 1.0,
        "priority_low_cost": 1.0,
        "priority_housing": 1.0,
        "priority_low_pollution": 0.7,
        "remote_worker": True,
        "top_n": 5,
    }

    response = client.post("/recommend", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "recommendations" in data
    assert len(data["recommendations"]) == 5

    first_recommendation = data["recommendations"][0]

    expected_fields = {
        "city",
        "country",
        "region",
        "numbeo_qol_rank",
        "cityfit_rank",
        "rank_difference",
        "numbeo_quality_of_life_index",
        "cityfit_score",
        "cost_of_living_index",
        "purchasing_power_index",
        "safety_index",
        "healthcare_index",
        "pollution_index",
        "climate_index",
        "explanation",
    }

    assert expected_fields.issubset(first_recommendation.keys())


def test_recommend_endpoint_filters_by_region():
    payload = {
        "priority_safety": 1.0,
        "priority_healthcare": 1.0,
        "priority_climate": 1.0,
        "priority_purchasing_power": 1.0,
        "priority_low_cost": 1.0,
        "priority_housing": 1.0,
        "priority_low_pollution": 1.0,
        "remote_worker": True,
        "top_n": 10,
        "region": "Europe",
    }

    response = client.post("/recommend", json=payload)

    assert response.status_code == 200

    data = response.json()
    recommendations = data["recommendations"]

    assert len(recommendations) > 0
    assert all(city["region"] == "Europe" for city in recommendations)


def test_recommend_endpoint_rejects_invalid_priority_value():
    payload = {
        "priority_safety": 3.0,
        "top_n": 5,
    }

    response = client.post("/recommend", json=payload)

    assert response.status_code == 422


def test_user_profile_allows_optional_region():
    profile = UserProfile(region="Europe")

    assert profile.region == "Europe"


def test_user_profile_region_defaults_to_none():
    profile = UserProfile()

    assert profile.region is None

def test_recommend_endpoint_filters_by_country():
    payload = {
        "priority_safety": 1.0,
        "priority_healthcare": 1.0,
        "priority_climate": 1.0,
        "priority_purchasing_power": 1.0,
        "priority_low_cost": 1.0,
        "priority_housing": 1.0,
        "priority_low_pollution": 1.0,
        "remote_worker": True,
        "top_n": 10,
        "country": "Japan",
    }

    response = client.post("/recommend", json=payload)

    assert response.status_code == 200

    data = response.json()
    recommendations = data["recommendations"]

    assert len(recommendations) > 0
    assert all(city["country"] == "Japan" for city in recommendations)

def test_user_profile_allows_optional_country():
    profile = UserProfile(country="United States")

    assert profile.country == "United States"


def test_user_profile_country_defaults_to_none():
    profile = UserProfile()

    assert profile.country is None