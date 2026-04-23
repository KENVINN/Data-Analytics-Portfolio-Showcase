# Databricks Mini Pipeline

This folder contains a small notebook-source PySpark pipeline designed to support the Databricks item in the portfolio tech stack.

## Goal

Read the synthetic Maker Info service order dataset, organize it using a simple bronze/silver/gold pattern, and publish two analytical outputs:

- `gold_daily_operations_kpis`: daily operational KPIs for backlog, SLA pressure, and revenue monitoring
- `gold_company_profitability`: company and service line profitability view for margin analysis

## Input

- `Synthetic_Data/service_orders_clean.csv`

In Databricks, this file can be uploaded to DBFS or mounted storage before running the notebook.

## Output Layers

- Bronze: raw service orders with ingestion timestamp
- Silver: typed and curated operational order table
- Gold: ready-to-query KPI aggregates for BI and management reporting

## Main File

- `maker_info_medallion_pipeline.py`

The notebook uses standard PySpark + Delta Lake patterns and is written in notebook-source format so it can be imported into Databricks directly.

