/*
Business question:
Which Maker Info service lines and client accounts generate the healthiest margin,
and where are unlinked costs eroding profitability?

Assumed synthetic tables:
- dim_company(company_id, company_name, account_type, city, region, contract_status)
- dim_technician(technician_id, technician_name, squad_name, specialty)
- fact_service_order(order_id, customer_id, company_id, technician_id, service_line, device_type, service_mode, opened_at, first_response_at, quoted_at, approved_at, closed_at, order_status, quoted_amount, approved_revenue, priority, sla_target_hours)
- fact_cost_entry(cost_id, order_id, company_id, cost_category, cost_amount, linked_status, recorded_at)
*/

WITH reference_date AS (
    SELECT
        MAX(COALESCE(CAST(closed_at AS DATE), CAST(opened_at AS DATE))) AS as_of_date
    FROM fact_service_order
),
closed_orders AS (
    SELECT
        fso.order_id,
        fso.company_id,
        fso.technician_id,
        fso.service_line,
        DATE_TRUNC('month', CAST(fso.closed_at AS TIMESTAMP)) AS closed_month,
        fso.approved_revenue,
        fso.order_status
    FROM fact_service_order AS fso
    CROSS JOIN reference_date AS rd
    WHERE fso.closed_at IS NOT NULL
      AND CAST(fso.closed_at AS DATE) >= DATE_TRUNC('month', rd.as_of_date) - INTERVAL '5 months'
),
linked_order_costs AS (
    SELECT
        fce.order_id,
        SUM(fce.cost_amount) AS linked_cost_amount
    FROM fact_cost_entry AS fce
    WHERE fce.linked_status = 'linked'
    GROUP BY fce.order_id
),
company_monthly_unlinked_costs AS (
    SELECT
        fce.company_id,
        DATE_TRUNC('month', CAST(fce.recorded_at AS TIMESTAMP)) AS closed_month,
        SUM(fce.cost_amount) AS unlinked_cost_amount
    FROM fact_cost_entry AS fce
    CROSS JOIN reference_date AS rd
    WHERE fce.linked_status = 'unlinked'
      AND CAST(fce.recorded_at AS DATE) >= DATE_TRUNC('month', rd.as_of_date) - INTERVAL '5 months'
    GROUP BY
        fce.company_id,
        DATE_TRUNC('month', CAST(fce.recorded_at AS TIMESTAMP))
),
order_financials AS (
    SELECT
        co.order_id,
        co.company_id,
        co.technician_id,
        co.service_line,
        co.closed_month,
        co.approved_revenue,
        COALESCE(loc.linked_cost_amount, 0) AS linked_cost_amount,
        co.approved_revenue - COALESCE(loc.linked_cost_amount, 0) AS gross_profit
    FROM closed_orders AS co
    LEFT JOIN linked_order_costs AS loc
        ON loc.order_id = co.order_id
),
company_monthly_revenue AS (
    SELECT
        ofn.company_id,
        ofn.closed_month,
        SUM(ofn.approved_revenue) AS company_revenue
    FROM order_financials AS ofn
    GROUP BY
        ofn.company_id,
        ofn.closed_month
),
service_line_monthly_metrics AS (
    SELECT
        dc.company_id,
        dc.company_name,
        dc.account_type,
        dc.region,
        ofn.service_line,
        ofn.closed_month,
        COUNT(*) AS closed_orders,
        SUM(ofn.approved_revenue) AS recognized_revenue,
        SUM(ofn.linked_cost_amount) AS linked_cost_amount,
        SUM(ofn.gross_profit) AS gross_profit_before_unlinked,
        SUM(CASE WHEN ofn.gross_profit < 0 THEN 1 ELSE 0 END) AS negative_margin_orders,
        ROUND(AVG(ofn.approved_revenue), 2) AS avg_ticket
    FROM order_financials AS ofn
    INNER JOIN dim_company AS dc
        ON dc.company_id = ofn.company_id
    WHERE dc.contract_status = 'active'
    GROUP BY
        dc.company_id,
        dc.company_name,
        dc.account_type,
        dc.region,
        ofn.service_line,
        ofn.closed_month
),
allocated_leakage AS (
    SELECT
        slmm.company_id,
        slmm.company_name,
        slmm.account_type,
        slmm.region,
        slmm.service_line,
        slmm.closed_month,
        slmm.closed_orders,
        slmm.recognized_revenue,
        slmm.linked_cost_amount,
        slmm.gross_profit_before_unlinked,
        slmm.negative_margin_orders,
        slmm.avg_ticket,
        COALESCE(cmulc.unlinked_cost_amount, 0)
        * slmm.recognized_revenue
        / NULLIF(cmr.company_revenue, 0) AS allocated_unlinked_cost
    FROM service_line_monthly_metrics AS slmm
    INNER JOIN company_monthly_revenue AS cmr
        ON cmr.company_id = slmm.company_id
       AND cmr.closed_month = slmm.closed_month
    LEFT JOIN company_monthly_unlinked_costs AS cmulc
        ON cmulc.company_id = slmm.company_id
       AND cmulc.closed_month = slmm.closed_month
),
profitability_trend AS (
    SELECT
        al.company_id,
        al.company_name,
        al.account_type,
        al.region,
        al.service_line,
        al.closed_month,
        al.closed_orders,
        al.recognized_revenue,
        al.linked_cost_amount,
        ROUND(al.allocated_unlinked_cost, 2) AS allocated_unlinked_cost,
        ROUND(al.gross_profit_before_unlinked - al.allocated_unlinked_cost, 2) AS net_profit_after_unlinked,
        ROUND(
            100.0 * (al.gross_profit_before_unlinked - al.allocated_unlinked_cost)
            / NULLIF(al.recognized_revenue, 0),
            2
        ) AS net_margin_pct,
        al.negative_margin_orders,
        al.avg_ticket,
        LAG(
            ROUND(
                100.0 * (al.gross_profit_before_unlinked - al.allocated_unlinked_cost)
                / NULLIF(al.recognized_revenue, 0),
                2
            )
        ) OVER (
            PARTITION BY al.company_id, al.service_line
            ORDER BY al.closed_month
        ) AS previous_month_margin_pct,
        ROW_NUMBER() OVER (
            PARTITION BY al.company_id, al.service_line
            ORDER BY al.closed_month DESC
        ) AS recency_rank
    FROM allocated_leakage AS al
)
SELECT
    pt.company_name,
    pt.account_type,
    pt.region,
    pt.service_line,
    pt.closed_month,
    pt.closed_orders,
    pt.recognized_revenue,
    pt.linked_cost_amount,
    pt.allocated_unlinked_cost,
    pt.net_profit_after_unlinked,
    pt.net_margin_pct,
    pt.negative_margin_orders,
    pt.avg_ticket,
    COALESCE(pt.net_margin_pct - pt.previous_month_margin_pct, 0) AS margin_delta_vs_previous_month,
    DENSE_RANK() OVER (
        ORDER BY pt.net_profit_after_unlinked DESC, pt.recognized_revenue DESC
    ) AS profitability_rank
FROM profitability_trend AS pt
WHERE pt.recency_rank = 1
ORDER BY profitability_rank, pt.company_name, pt.service_line;

