from fastapi.testclient import TestClient

from cityfit.api.main import app


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


def test_recommend_endpoint_rejects_invalid_priority_value():
    payload = {
        "priority_safety": 3.0,
        "top_n": 5,
    }

    response = client.post("/recommend", json=payload)

    assert response.status_code == 422