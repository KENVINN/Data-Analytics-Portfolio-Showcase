# Databricks notebook source
# MAGIC %md
# MAGIC # Maker Info Bronze, Silver, Gold Mini Pipeline
# MAGIC
# MAGIC This notebook reads the synthetic `service_orders_clean.csv` dataset and builds
# MAGIC a simple medallion-style analytical pipeline for Databricks portfolio demonstration.

# COMMAND ----------

from pyspark.sql import functions as F

SOURCE_PATH = "/FileStore/portfolio/service_orders_clean.csv"
CATALOG_NAME = "main"
SCHEMA_NAME = "maker_info_portfolio"

BRONZE_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.bronze_service_orders"
SILVER_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.silver_service_orders"
GOLD_DAILY_KPIS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.gold_daily_operations_kpis"
GOLD_COMPANY_MARGIN_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.gold_company_profitability"

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}")

# COMMAND ----------

bronze_orders = (
    spark.read.option("header", True).csv(SOURCE_PATH)
    .withColumn("ingested_at", F.current_timestamp())
    .withColumn("source_file", F.input_file_name())
)

(
    bronze_orders.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(BRONZE_TABLE)
)

# COMMAND ----------

silver_orders = (
    spark.table(BRONZE_TABLE)
    .select(
        F.col("order_id"),
        F.col("customer_name"),
        F.col("company_name"),
        F.col("service_line"),
        F.col("device_type"),
        F.col("current_status"),
        F.to_timestamp("opened_at").alias("opened_at"),
        F.to_timestamp("closed_at").alias("closed_at"),
        F.col("quoted_amount_brl").cast("double").alias("quoted_amount_brl"),
        F.col("approved_revenue_brl").cast("double").alias("approved_revenue_brl"),
        F.col("sla_target_hours").cast("int").alias("sla_target_hours"),
        F.col("hours_open").cast("double").alias("hours_open"),
        F.col("hours_to_close").cast("double").alias("hours_to_close"),
        F.col("revenue_realization_gap_brl").cast("double").alias("revenue_realization_gap_brl"),
        F.col("is_b2b_account").cast("boolean").alias("is_b2b_account"),
        F.col("order_health_flag"),
        F.col("ingested_at"),
    )
    .withColumn("opened_date", F.to_date("opened_at"))
    .withColumn(
        "sla_breached_flag",
        F.when(F.col("order_health_flag") == F.lit("sla_breached"), F.lit(1)).otherwise(F.lit(0)),
    )
    .withColumn(
        "critical_delay_flag",
        F.when(F.col("order_health_flag") == F.lit("critical_delay"), F.lit(1)).otherwise(F.lit(0)),
    )
)

(
    silver_orders.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)

# COMMAND ----------

gold_daily_operations_kpis = (
    spark.table(SILVER_TABLE)
    .groupBy("opened_date")
    .agg(
        F.count("*").alias("orders_opened"),
        F.sum("approved_revenue_brl").alias("approved_revenue_brl"),
        F.sum("sla_breached_flag").alias("sla_breached_orders"),
        F.sum("critical_delay_flag").alias("critical_delay_orders"),
        F.sum(
            F.when(
                F.col("current_status").isin("awaiting_part", "in_repair", "ready_for_pickup"),
                F.lit(1),
            ).otherwise(F.lit(0))
        ).alias("active_backlog_orders"),
    )
    .orderBy("opened_date")
)

(
    gold_daily_operations_kpis.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_DAILY_KPIS_TABLE)
)

# COMMAND ----------

gold_company_profitability = (
    spark.table(SILVER_TABLE)
    .groupBy("company_name", "service_line")
    .agg(
        F.count("*").alias("orders"),
        F.sum("quoted_amount_brl").alias("quoted_amount_brl"),
        F.sum("approved_revenue_brl").alias("approved_revenue_brl"),
        F.sum("revenue_realization_gap_brl").alias("revenue_realization_gap_brl"),
        F.avg("hours_to_close").alias("avg_hours_to_close"),
        F.sum("sla_breached_flag").alias("sla_breached_orders"),
    )
    .withColumn(
        "revenue_realization_pct",
        F.round(
            100.0 * F.col("approved_revenue_brl") / F.nullif(F.col("quoted_amount_brl"), F.lit(0.0)),
            2,
        ),
    )
    .orderBy(F.col("approved_revenue_brl").desc())
)

(
    gold_company_profitability.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_COMPANY_MARGIN_TABLE)
)

# COMMAND ----------

display(gold_daily_operations_kpis)

# COMMAND ----------

display(gold_company_profitability)

