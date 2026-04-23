# Data Analytics Portfolio Showcase

Solving business problems through data, process intelligence, and decision-ready analytics.

I am a data professional focused on turning operational complexity into clear business decisions. This public portfolio was designed to showcase how I approach SQL problem-solving, Python automation, data modeling, and dashboard design for international Data Analyst and Business Intelligence opportunities.

All examples in this repository use synthetic scenarios and fictitious entities only. The portfolio is centered on a fictitious analytical version of the Maker Info service operations system, with no sensitive, proprietary, or real company data included.

## Tech Stack

- `SQL`: analytical querying, CTEs, window functions, business logic translation, and KPI calculation
- `Python`: data cleaning, automation, reproducible transformations, and pandas-based workflows
- `Power BI`: executive dashboards, self-service reporting, KPI storytelling, and usability-first design
- `Databricks`: scalable data pipelines, notebook-driven exploration, and medallion-style thinking
- `Git`: version control, documentation discipline, and collaborative development practices

## Featured Projects

### 1. Maker Info Service Order Profitability Analysis

Synthetic analytics case focused on operational and financial visibility for a repair and support management system.

- Which service lines generate the best margin after linked and unlinked costs?
- Which client accounts are leaking profitability due to stalled orders or unassigned expenses?
- Which operational patterns should managers prioritize to protect cash flow?

Technical highlights:

- Dimensional thinking around service orders, status history, costs, customers, and technicians
- Advanced SQL with multi-step CTEs, joins, window functions, and profitability bridges
- KPI design for margin, backlog aging, SLA attainment, quote recovery, and recall actions

### 2. Maker Info Operational Dashboard and Recall Intelligence

Synthetic BI case built around the daily decision layer of the Maker Info system.

- Tracks revenue, cost leakage, SLA compliance, backlog aging, quote approval, and recall opportunity
- Organizes KPIs for executive overview, operational diagnosis, and daily team action
- Applies UX principles for fast scanning, drill-down clarity, and trustworthy data storytelling

## Repository Structure

```text
Data-Analytics-Portfolio-Showcase/
|-- README.md
|-- .gitignore
|-- requirements.txt
|-- SQL_Challenges/
|   |-- 01_service_order_profitability_analysis.sql
|   |-- 02_operational_sla_backlog_analysis.sql
|   `-- 03_customer_recall_reactivation_analysis.sql
|-- Python_Automation/
|   |-- clean_service_orders_data.py
|   `-- generate_synthetic_portfolio_data.py
|-- Synthetic_Data/
|   |-- README.md
|   |-- dim_company.csv
|   |-- dim_customer.csv
|   |-- dim_technician.csv
|   |-- fact_service_order.csv
|   |-- fact_order_status_history.csv
|   |-- fact_cost_entry.csv
|   |-- fact_customer_contact.csv
|   |-- service_orders_raw.csv
|   `-- service_orders_clean.csv
`-- Dashboards/
    |-- README.md
    `-- assets/
        |-- dashboard-executive-overview.jpg
        `-- dashboard-operational-input.jpg
```

## Synthetic Data Pack

This repository also includes a reproducible synthetic data pack so the portfolio can be explored without any dependency on real business data.

- Service order tables for profitability, SLA, backlog, and recall analysis
- Operational cost and status history data for dashboard prototyping
- Customer contact history for recall and commercial follow-up use cases
- A deliberately messy service order export for Python-based data cleaning
- A cleaned service order export that demonstrates the output of the pandas workflow

## Quick Start

```bash
pip install -r requirements.txt
python Python_Automation/generate_synthetic_portfolio_data.py
python Python_Automation/clean_service_orders_data.py \
  --input Synthetic_Data/service_orders_raw.csv \
  --output Synthetic_Data/service_orders_clean.csv \
  --reference-date 2026-04-15
```

## How This Portfolio Creates Business Value

- Translates business questions into structured analytical logic
- Designs datasets and KPIs that support decision-making instead of vanity reporting
- Builds maintainable code that can move from analysis to production workflows
- Connects technical execution with stakeholder communication and business impact

## Professional Objective

I am pursuing opportunities where data can improve prioritization, operational visibility, and data-driven decision support across business, product, operations, or service teams.

## Contact

- LinkedIn: [linkedin.com/in/kevin-savio-data](https://www.linkedin.com/in/kevin-savio-data/)
