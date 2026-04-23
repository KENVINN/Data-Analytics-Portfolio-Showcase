# Dashboard Design Notes

This folder shows how I structure BI dashboards for decision-making, KPI storytelling, and executive usability. The screenshots below come from real product screens in a working application context, with values intentionally zeroed, masked, or generic to preserve confidentiality.

## Dashboard Strategy

I design dashboards with three layers in mind:

1. Executive layer: headline KPIs, trend direction, and immediate business status
2. Diagnostic layer: drill-down dimensions that explain what changed
3. Action layer: operational details that support prioritization and follow-up

## KPI Structure I Prefer

- Outcome KPIs: revenue, retention, SLA compliance, churn, member engagement
- Diagnostic KPIs: segment mix, partner performance, aging buckets, resolution stages
- Action KPIs: accounts at risk, tickets breaching SLA, inactive members, backlog owners
- Trust signals: last refresh timestamp, metric definitions, filter context, and exception notes

## Example 1: Decision Layer Dashboard

![Real Executive Dashboard Screenshot](./assets/dashboard-executive-overview.jpg)

What this screen is designed to do:

- Show financial and operational status within the first few seconds
- Centralize revenue, cost, margin, and blocked-value indicators in one place
- Expose exception signals early so managers can act before the issue impacts cash flow

UX choices:

- KPI cards are grouped in a predictable scan order
- Filters stay visible near the top because date range and service line change interpretation
- Navigation separates business domains such as profitability, operations, pricing, and recall

## Example 2: Operational Input Layer

![Real Operational Input Screenshot](./assets/dashboard-operational-input.jpg)

Why this screen matters for BI quality:

- Reliable dashboards depend on consistent operational data capture upstream
- Structured form inputs reduce ambiguity in ticket, device, customer, and service-stage records
- Standardized status transitions improve SLA analysis, bottleneck detection, and backlog visibility

UX choices:

- Required fields are visually obvious, reducing missing-data risk
- Process stages are explicit, helping convert operational actions into analytical events
- The form keeps business language close to the workflow, which improves adoption and data consistency

## UX Principles I Apply in BI

- Every page should answer one primary business question clearly
- Users should understand status within the first five seconds
- Drill paths should feel intentional, not accidental
- Metric definitions must be consistent across pages
- Mobile and lower-resolution screens should still preserve hierarchy and readability

## Data Modeling Behind the Visuals

I typically design dashboards on top of a simple and scalable analytical model:

- Fact tables for events such as check-ins, bookings, invoices, subscriptions, or tickets
- Dimension tables for entities such as member, partner, account, technician, or calendar
- Clear date grain and business definitions to avoid duplicated logic in the BI layer
- Reusable measures so KPI calculations remain consistent across reports
