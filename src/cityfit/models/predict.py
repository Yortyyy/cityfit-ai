import pandas as pd

from cityfit.config import CITYFIT_SCORES_PATH, PROCESSED_DATA_DIR
from cityfit.models.train_ranker import FEATURE_COLUMNS, train_cityfit_ranker


PREDICTIONS_OUTPUT_PATH = PROCESSED_DATA_DIR / "cityfit_model_predictions.csv"


def add_model_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Train the current CityFit ranker and add model predictions.

    TODO: Load model instead of train
    """
    model = train_cityfit_ranker(df)

    predictions = df.copy()
    X = predictions[FEATURE_COLUMNS]

    predictions["good_fit_probability"] = model.predict_proba(X)[:, 1]
    predictions["model_predicted_good_fit"] = model.predict(X)

    return predictions.sort_values(
        ["good_fit_probability", "cityfit_score"],
        ascending=[False, False],
    ).reset_index(drop=True)


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CITYFIT_SCORES_PATH)
    predictions = add_model_predictions(df)

    predictions.to_csv(PREDICTIONS_OUTPUT_PATH, index=False)

    print(f"Saved model predictions to: {PREDICTIONS_OUTPUT_PATH}")
    print(
        predictions[
            [
                "city",
                "country",
                "cityfit_rank",
                "cityfit_score",
                "good_fit_probability",
                "model_predicted_good_fit",
            ]
        ].head(15).to_string(index=False)
    )


if __name__ == "__main__":
    main()