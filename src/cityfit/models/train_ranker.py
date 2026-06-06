import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from cityfit.config import CITYFIT_SCORES_PATH


FEATURE_COLUMNS = [
    "numbeo_quality_of_life_index",
    "purchasing_power_index",
    "safety_index",
    "healthcare_index",
    "cost_of_living_index",
    "property_price_to_income_ratio",
    "traffic_commute_index",
    "pollution_index",
    "climate_index",
    "low_pollution_score",
    "low_traffic_score",
]


def train_cityfit_ranker(df: pd.DataFrame) -> XGBClassifier:
    df = df.copy()

    threshold = df["cityfit_score"].quantile(0.70)
    df["is_good_fit"] = (df["cityfit_score"] >= threshold).astype(int)

    X = df[FEATURE_COLUMNS]
    y = df["is_good_fit"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=123,
        stratify=y,
    )

    params = {
        "n_estimators": 100,
        "max_depth": 3,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "eval_metric": "logloss",
        "random_state": 123,
    }

    model = XGBClassifier(**params)

    mlflow.set_experiment("cityfit-ranking-model")

    with mlflow.start_run(run_name="xgboost_cityfit_ranker"):
        mlflow.log_params(params)
        mlflow.log_param("target", "synthetic_good_fit_top_30_percent")
        mlflow.log_param("num_features", len(FEATURE_COLUMNS))
        mlflow.log_param("features", ",".join(FEATURE_COLUMNS))

        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        pred_probs = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, preds)
        roc_auc = roc_auc_score(y_test, pred_probs)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("roc_auc", roc_auc)

        mlflow.sklearn.log_model(model, "cityfit_ranker_model")

    return model


def main() -> None:
    df = pd.read_csv(CITYFIT_SCORES_PATH)
    train_cityfit_ranker(df)
    print("Finished training CityFit XGBoost ranker with MLflow tracking.")


if __name__ == "__main__":
    main()