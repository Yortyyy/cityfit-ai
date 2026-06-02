# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Feature Engineering
# MAGIC
# MAGIC Creates CityFit features, personalized scores, and rank comparison.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

SILVER_TABLE = "silver_city_quality_of_life_metrics"
GOLD_TABLE = "gold_cityfit_recommendations"

silver_df = spark.table(SILVER_TABLE)

display(silver_df)

# COMMAND ----------

weights = {
    "numbeo_quality_of_life": 0.15,
    "purchasing_power": 0.20,
    "safety": 0.20,
    "healthcare": 0.10,
    "climate": 0.10,
    "cost_penalty": 0.20,
    "housing_penalty": 0.15,
    "pollution_penalty": 0.07,
    "traffic_penalty": 0.03,
}

# COMMAND ----------

feature_df = (
    silver_df
    .withColumn(
        "quality_per_cost",
        F.col("numbeo_quality_of_life_index") / F.col("cost_of_living_index")
    )
    .withColumn(
        "purchasing_power_per_cost",
        F.col("purchasing_power_index") / F.col("cost_of_living_index")
    )
    .withColumn(
        "low_pollution_score",
        F.lit(100) - F.col("pollution_index")
    )
    .withColumn(
        "low_traffic_score",
        F.lit(100) - F.col("traffic_commute_index")
    )
)

# COMMAND ----------

scored_df = (
    feature_df
    .withColumn(
        "positive_score",
        F.col("numbeo_quality_of_life_index") * F.lit(weights["numbeo_quality_of_life"])
        + F.col("purchasing_power_index") * F.lit(weights["purchasing_power"])
        + F.col("safety_index") * F.lit(weights["safety"])
        + F.col("healthcare_index") * F.lit(weights["healthcare"])
        + F.col("climate_index") * F.lit(weights["climate"])
    )
    .withColumn(
        "negative_score",
        F.col("cost_of_living_index") * F.lit(weights["cost_penalty"])
        + F.col("property_price_to_income_ratio") * F.lit(weights["housing_penalty"])
        + F.col("pollution_index") * F.lit(weights["pollution_penalty"])
        + F.col("traffic_commute_index") * F.lit(weights["traffic_penalty"])
    )
    .withColumn(
        "cityfit_score",
        F.col("positive_score") - F.col("negative_score")
    )
)

# COMMAND ----------

numbeo_rank_window = Window.orderBy(F.col("numbeo_quality_of_life_index").desc())
cityfit_rank_window = Window.orderBy(F.col("cityfit_score").desc())

ranked_df = (
    scored_df
    .withColumn("numbeo_qol_rank", F.rank().over(numbeo_rank_window))
    .withColumn("cityfit_rank", F.rank().over(cityfit_rank_window))
    .withColumn("rank_difference", F.col("numbeo_qol_rank") - F.col("cityfit_rank"))
)

# COMMAND ----------

gold_df = ranked_df.select(
    "source_rank",
    "city",
    "country",
    "numbeo_qol_rank",
    "cityfit_rank",
    "rank_difference",
    "numbeo_quality_of_life_index",
    "cityfit_score",
    "positive_score",
    "negative_score",
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
    "source_url",
    "source_note",
)

display(gold_df.orderBy("cityfit_rank"))

# COMMAND ----------

(
    gold_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(GOLD_TABLE)
)

# COMMAND ----------

spark.sql("""
SELECT
  city,
  country,
  numbeo_qol_rank,
  cityfit_rank,
  rank_difference,
  ROUND(numbeo_quality_of_life_index, 2) AS numbeo_quality_of_life_index,
  ROUND(cityfit_score, 2) AS cityfit_score,
  ROUND(cost_of_living_index, 2) AS cost_of_living_index,
  ROUND(purchasing_power_index, 2) AS purchasing_power_index
FROM gold_cityfit_recommendations
ORDER BY cityfit_rank
LIMIT 20
""").display()