# Data Analytics Portfolio Showcase

Solving business problems through data, process intelligence, and decision-ready analytics.

I am a data professional focused on turning operational complexity into clear business decisions. This public portfolio was designed to showcase how I approach SQL problem-solving, Python automation, data modeling, and dashboard design for international Data Analyst and Business Intelligence opportunities.

All examples in this repository use synthetic scenarios and fictitious entities only. No sensitive, proprietary, or real company data is included.

## Tech Stack

- `SQL`: analytical querying, CTEs, window functions, business logic translation, and KPI calculation
- `Python`: data cleaning, automation, reproducible transformations, and pandas-based workflows
- `Power BI`: executive dashboards, self-service reporting, KPI storytelling, and usability-first design
- `Databricks`: scalable data pipelines, notebook-driven exploration, and medallion-style thinking
- `Git`: version control, documentation discipline, and collaborative development practices

## Featured Projects

### 1. Gym Partner Engagement Analysis

Synthetic analytics case that simulates a fitness partnership program and answers questions such as:

- Which partner gyms drive the highest member engagement?
- Where is churn risk increasing month over month?
- Which behaviors signal reactivation potential?

Technical highlights:

- Star-schema thinking using member, partner, booking, and check-in entities
- Advanced SQL with multi-step CTEs, joins, and window functions
- KPI design for retention, engagement score, and partner performance ranking

### 2. IT Service Efficiency Dashboard

Synthetic BI case focused on operational support performance and decision support for service managers.

- Tracks SLA compliance, backlog aging, first response time, and mean time to resolution
- Organizes KPIs for executive overview, operational diagnosis, and team-level action
- Applies UX principles for fast scanning, drill-down clarity, and trustworthy data storytelling

## Repository Structure

```text
Data-Analytics-Portfolio-Showcase/
|-- README.md
|-- .gitignore
|-- requirements.txt
|-- SQL_Challenges/
|   |-- 01_gym_partner_engagement_analysis.sql
|   |-- 02_saas_subscription_health.sql
|   `-- 03_member_lifecycle_reactivation.sql
|-- Python_Automation/
|   |-- clean_membership_data.py
|   `-- generate_synthetic_portfolio_data.py
|-- Synthetic_Data/
|   |-- README.md
|   |-- dim_partner.csv
|   |-- dim_member.csv
|   |-- fact_membership.csv
|   |-- fact_checkin.csv
|   |-- fact_class_booking.csv
|   |-- membership_export_raw.csv
|   |-- membership_export_clean.csv
|   |-- dim_account.csv
|   |-- dim_plan.csv
|   |-- fact_subscription_snapshot.csv
|   `-- it_service_tickets.csv
`-- Dashboards/
    |-- README.md
    `-- assets/
        |-- dashboard-executive-overview.jpg
        `-- dashboard-operational-input.jpg
```

## Synthetic Data Pack

This repository also includes a reproducible synthetic data pack so the portfolio can be explored without any dependency on real business data.

- Gym engagement tables for SQL analysis and lifecycle segmentation
- SaaS revenue snapshots for MRR, churn, and expansion analysis
- Service ticket data for dashboard and operational KPI prototyping
- A deliberately messy membership export for Python-based data cleaning
- A cleaned membership export that demonstrates the output of the pandas workflow

## Quick Start

```bash
pip install -r requirements.txt
python Python_Automation/generate_synthetic_portfolio_data.py
python Python_Automation/clean_membership_data.py \
  --input Synthetic_Data/membership_export_raw.csv \
  --output Synthetic_Data/membership_export_clean.csv \
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
