from cityfit.api.schemas import UserProfile


def build_weights(profile: UserProfile) -> dict:
    traffic_weight = 0.03 if profile.remote_worker else 0.10

    return {
        "purchasing_power": 0.15 * profile.priority_purchasing_power,
        "safety": 0.20 * profile.priority_safety,
        "healthcare": 0.10 * profile.priority_healthcare,
        "climate": 0.15 * profile.priority_climate,
        "affordability": 0.10 * profile.priority_low_cost,
        "housing_affordability": 0.15 * profile.priority_housing,
        "low_pollution": 0.10 * profile.priority_low_pollution,
        "low_traffic": traffic_weight,
    }