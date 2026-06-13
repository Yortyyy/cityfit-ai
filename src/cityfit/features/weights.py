from cityfit.api.schemas import UserProfile


def build_weights(profile: UserProfile) -> dict:
    traffic_remote_multiplier = 0.5 if profile.remote_worker else 1.0

    return {
        "purchasing_power": 0.15 * profile.priority_purchasing_power,
        "safety": 0.20 * profile.priority_safety,
        "healthcare": 0.10 * profile.priority_healthcare,
        "climate": 0.15 * profile.priority_climate,
        "affordability": 0.10 * profile.priority_low_cost,
        "housing_affordability": 0.15 * profile.priority_housing,
        "low_pollution": 0.10 * profile.priority_low_pollution,
        "low_traffic": (
            0.10
            * profile.priority_low_traffic
            * traffic_remote_multiplier
        ),
    }