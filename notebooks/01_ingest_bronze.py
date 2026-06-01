# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

RAW_CSV_PATH = "/Workspace/Users/troydcrawford@outlook.com/cityfit-ai/bronze_city_quality_of_life_raw.csv"
BRONZE_TABLE = "bronze_city_quality_of_life_raw"

# COMMAND ----------

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(RAW_CSV_PATH)
)

# COMMAND ----------

bronze_df = (
    raw_df
    .withColumn("ingested_at", F.current_timestamp())
    .withColumn("source_file", F.lit(RAW_CSV_PATH))
)

# COMMAND ----------

(
    bronze_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(BRONZE_TABLE)
)

# COMMAND ----------

display(spark.table(BRONZE_TABLE))