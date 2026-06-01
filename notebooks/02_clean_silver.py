# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Cleaning
# MAGIC
# MAGIC Cleans and validates the raw Bronze table, then writes a Silver Delta table.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

# COMMAND ----------

BRONZE_TABLE = "bronze_city_quality_of_life_raw"
SILVER_TABLE = "silver_city_quality_of_life_metrics"

bronze_df = spark.table(BRONZE_TABLE)

display(bronze_df)

# COMMAND ----------

required_columns = [
    "source_rank",
    "city",
    "country",
    "numbeo_quality_of_life_index",
    "purchasing_power_index",
    "safety_index",
    "healthcare_index",
    "cost_of_living_index",
    "property_price_to_income_ratio",
    "traffic_commute_index",
    "pollution_index",
    "climate_index",
    "source_url",
    "source_note",
]

missing_columns = [col for col in required_columns if col not in bronze_df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# COMMAND ----------

numeric_columns = [
    "numbeo_quality_of_life_index",
    "purchasing_power_index",
    "safety_index",
    "healthcare_index",
    "cost_of_living_index",
    "property_price_to_income_ratio",
    "traffic_commute_index",
    "pollution_index",
    "climate_index",
]

silver_df = bronze_df

for col_name in numeric_columns:
    silver_df = silver_df.withColumn(col_name, F.col(col_name).cast(DoubleType()))

silver_df = silver_df.withColumn("source_rank", F.col("source_rank").cast(IntegerType()))

silver_df = (
    silver_df
    .withColumn("city", F.trim(F.col("city")))
    .withColumn("country", F.trim(F.col("country")))
    .dropDuplicates(["city", "country"])
    .filter(F.col("city").isNotNull())
    .filter(F.col("country").isNotNull())
)

display(silver_df)

# COMMAND ----------

(
    silver_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(SILVER_TABLE)
)

# COMMAND ----------

spark.table(SILVER_TABLE).display()