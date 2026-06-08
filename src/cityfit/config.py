from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CITY_METRICS_RAW_PATH = RAW_DATA_DIR / "numbeo_quality_of_life_city_current_dataset_2_with_region.csv"

CITY_METRICS_CLEAN_PATH = INTERIM_DATA_DIR / "cleaned_city_metrics.csv"
CITY_FEATURES_PATH = PROCESSED_DATA_DIR / "city_features.csv"
CITYFIT_SCORES_PATH = PROCESSED_DATA_DIR / "cityfit_scores.csv"

KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

COLLECTION_NAME = "cityfit_knowledge_base"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"