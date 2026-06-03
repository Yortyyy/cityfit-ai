from cityfit.api.schemas import UserProfile


def build_weights(profile: UserProfile) -> dict:
    traffic_weight = 0.03 if profile.remote_worker else 0.10

    return {
        "numbeo_quality_of_life": 0.15,
        "purchasing_power": 0.20 * profile.priority_purchasing_power,
        "safety": 0.20 * profile.priority_safety,
        "healthcare": 0.10 * profile.priority_healthcare,
        "climate": 0.10 * profile.priority_climate,
        "cost_penalty": 0.20 * profile.priority_low_cost,
        "housing_penalty": 0.15 * profile.priority_housing,
        "pollution_penalty": 0.07 * profile.priority_low_pollution,
        "traffic_penalty": traffic_weight,
    }