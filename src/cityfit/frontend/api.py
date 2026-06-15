import requests


API_URL = "http://api:8000"


def get_recommendations_from_api(payload: dict) -> list[dict]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["recommendations"]


def query_agent_from_api(payload: dict) -> dict:
    response = requests.post(f"{API_URL}/agent/query", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()