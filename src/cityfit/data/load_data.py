import pandas as pd

from cityfit.config import CITY_METRICS_RAW_PATH


def load_city_metrics(path=CITY_METRICS_RAW_PATH) -> pd.DataFrame:
    """Load raw city quality-of-life metrics from CSV."""
    return pd.read_csv(path)