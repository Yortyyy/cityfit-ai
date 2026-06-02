# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Train Ranking Model
# MAGIC
# MAGIC This notebook trains an XGBoost classifier to predict whether a city is a strong CityFit recommendation.
# MAGIC
# MAGIC The current version uses a synthetic label derived from the rule-based CityFit score:
# MAGIC
# MAGIC - `is_good_fit = 1` if the city is in the top 30% by CityFit score
# MAGIC - `is_good_fit = 0` otherwise
# MAGIC
# MAGIC In a production system, this label would ideally come from real user feedback such as saved cities, clicks, ratings, surveys, or relocation outcomes.

# COMMAND ----------

import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

GOLD_TABLE = "gold_cityfit_recommendations"
EXPERIMENT_NAME = "/Shared/cityfit-ranking-model"

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
    "quality_per_cost",
    "low_pollution_score",
    "low_traffic_score",
]

TARGET_COLUMN = "is_good_fit"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Gold table

# COMMAND ----------

gold_spark_df = spark.table(GOLD_TABLE)

display(gold_spark_df.orderBy("cityfit_rank"))

# COMMAND ----------

gold_df = gold_spark_df.toPandas()

gold_df.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create synthetic target
# MAGIC
# MAGIC This target is based on the existing CityFit scoring logic. It lets us demonstrate a supervised ML workflow while being transparent that the label is not real user behavior yet.

# COMMAND ----------

threshold = gold_df["cityfit_score"].quantile(0.70)
gold_df[TARGET_COLUMN] = (gold_df["cityfit_score"] >= threshold).astype(int)

gold_df[[  
    "city",
    "country",
    "cityfit_score",
    "cityfit_rank",
    TARGET_COLUMN,
]].sort_values("cityfit_rank").head(20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prepare train/test split

# COMMAND ----------

X = gold_df[FEATURE_COLUMNS]
y = gold_df[TARGET_COLUMN]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train XGBoost model with MLflow tracking

# COMMAND ----------

params = {
    "n_estimators": 100,
    "max_depth": 3,
    "learning_rate": 0.05,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "eval_metric": "logloss",
    "random_state": 42,
}

model = XGBClassifier(**params)

mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run(run_name="xgboost_cityfit_ranker") as run:
    mlflow.log_params(params)
    mlflow.log_param("gold_table", GOLD_TABLE)
    mlflow.log_param("target", "synthetic_good_fit_top_30_percent")
    mlflow.log_param("target_threshold_cityfit_score", threshold)
    mlflow.log_param("num_features", len(FEATURE_COLUMNS))
    mlflow.log_param("features", ",".join(FEATURE_COLUMNS))

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    pred_probs = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, preds)
    roc_auc = roc_auc_score(y_test, pred_probs)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("roc_auc", roc_auc)

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="cityfit_ranker_model",
        input_example=X_train.head(3),
    )

    run_id = run.info.run_id

print(f"Run ID: {run_id}")
print(f"Accuracy: {accuracy:.4f}")
print(f"ROC AUC: {roc_auc:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add model predictions back to Gold data

# COMMAND ----------

gold_df["good_fit_probability"] = model.predict_proba(gold_df[FEATURE_COLUMNS])[:, 1]
gold_df["model_predicted_good_fit"] = model.predict(gold_df[FEATURE_COLUMNS])

prediction_cols = [
    "city",
    "country",
    "cityfit_rank",
    "cityfit_score",
    "good_fit_probability",
    "model_predicted_good_fit",
    TARGET_COLUMN,
]

gold_df[prediction_cols].sort_values("good_fit_probability", ascending=False).head(20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save prediction table

# COMMAND ----------

PREDICTION_TABLE = "gold_cityfit_model_predictions"

predictions_spark_df = spark.createDataFrame(gold_df)

(
    predictions_spark_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(PREDICTION_TABLE)
)

display(
    spark.table(PREDICTION_TABLE)
    .select(
        "city",
        "country",
        "cityfit_rank",
        "cityfit_score",
        "good_fit_probability",
        "model_predicted_good_fit",
        "is_good_fit",
    )
    .orderBy("good_fit_probability", ascending=False)
)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   city,
# MAGIC   country,
# MAGIC   cityfit_rank,
# MAGIC   ROUND(cityfit_score, 2) AS cityfit_score,
# MAGIC   ROUND(good_fit_probability, 4) AS good_fit_probability,
# MAGIC   model_predicted_good_fit,
# MAGIC   is_good_fit
# MAGIC FROM gold_cityfit_model_predictions
# MAGIC ORDER BY good_fit_probability DESC
# MAGIC LIMIT 20;