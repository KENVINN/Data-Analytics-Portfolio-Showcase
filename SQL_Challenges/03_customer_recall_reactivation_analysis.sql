/*
Business question:
Which customers and B2B accounts should be prioritized for recall,
quote recovery, or reactivation inside the Maker Info system?

Assumed synthetic tables:
- dim_company(company_id, company_name, account_type, city, region, contract_status)
- dim_customer(customer_id, company_id, customer_name, phone_number, city, customer_type)
- fact_service_order(order_id, customer_id, company_id, technician_id, service_line, device_type, service_mode, opened_at, first_response_at, quoted_at, approved_at, closed_at, order_status, quoted_amount, approved_revenue, priority, sla_target_hours)
- fact_customer_contact(contact_id, customer_id, company_id, contact_type, contact_channel, contact_at, contact_outcome)
*/

WITH reference_date AS (
    SELECT
        MAX(reference_timestamp) AS as_of_timestamp
    FROM (
        SELECT MAX(CAST(closed_at AS TIMESTAMP)) AS reference_timestamp
        FROM fact_service_order
        UNION ALL
        SELECT MAX(CAST(contact_at AS TIMESTAMP)) AS reference_timestamp
        FROM fact_customer_contact
    ) AS source_dates
),
delivered_orders AS (
    SELECT
        fso.order_id,
        fso.customer_id,
        fso.company_id,
        fso.device_type,
        fso.service_line,
        CAST(fso.closed_at AS TIMESTAMP) AS closed_at,
        fso.approved_revenue
    FROM fact_service_order AS fso
    WHERE fso.closed_at IS NOT NULL
      AND fso.approved_revenue > 0
),
ordered_customer_orders AS (
    SELECT
        do.customer_id,
        do.company_id,
        do.device_type,
        do.closed_at,
        do.approved_revenue,
        LAG(do.device_type) OVER (
            PARTITION BY do.customer_id
            ORDER BY do.closed_at
        ) AS previous_device_type,
        LAG(do.closed_at) OVER (
            PARTITION BY do.customer_id
            ORDER BY do.closed_at
        ) AS previous_closed_at
    FROM delivered_orders AS do
),
repeat_device_issues AS (
    SELECT
        oco.customer_id,
        COUNT(*) FILTER (
            WHERE oco.device_type = oco.previous_device_type
              AND oco.closed_at <= oco.previous_closed_at + INTERVAL '90 days'
        ) AS repeat_device_issue_count
    FROM ordered_customer_orders AS oco
    GROUP BY oco.customer_id
),
customer_order_rollup AS (
    SELECT
        do.customer_id,
        do.company_id,
        COUNT(*) AS completed_orders,
        COUNT(DISTINCT do.service_line) AS service_lines_used,
        SUM(do.approved_revenue) AS total_revenue,
        MAX(do.closed_at) AS last_closed_at
    FROM delivered_orders AS do
    GROUP BY
        do.customer_id,
        do.company_id
),
quote_loss_summary AS (
    SELECT
        fso.customer_id,
        COUNT(*) FILTER (WHERE fso.order_status = 'quote_rejected') AS quote_rejections
    FROM fact_service_order AS fso
    GROUP BY fso.customer_id
),
open_order_summary AS (
    SELECT
        fso.customer_id,
        COUNT(*) FILTER (
            WHERE fso.order_status IN ('awaiting_part', 'in_repair', 'ready_for_pickup')
        ) AS open_orders
    FROM fact_service_order AS fso
    GROUP BY fso.customer_id
),
latest_contact AS (
    SELECT
        fcc.customer_id,
        fcc.company_id,
        fcc.contact_type,
        fcc.contact_channel,
        fcc.contact_outcome,
        CAST(fcc.contact_at AS TIMESTAMP) AS contact_at,
        ROW_NUMBER() OVER (
            PARTITION BY fcc.customer_id
            ORDER BY CAST(fcc.contact_at AS TIMESTAMP) DESC
        ) AS contact_rank
    FROM fact_customer_contact AS fcc
),
customer_snapshot AS (
    SELECT
        dc.customer_id,
        dc.customer_name,
        dc.phone_number,
        dc.city,
        dco.company_name,
        dco.account_type,
        cor.completed_orders,
        cor.service_lines_used,
        cor.total_revenue,
        cor.last_closed_at,
        COALESCE(rdi.repeat_device_issue_count, 0) AS repeat_device_issue_count,
        COALESCE(qls.quote_rejections, 0) AS quote_rejections,
        COALESCE(oos.open_orders, 0) AS open_orders,
        lc.contact_type AS latest_contact_type,
        lc.contact_channel AS latest_contact_channel,
        lc.contact_outcome AS latest_contact_outcome,
        lc.contact_at AS latest_contact_at,
        CAST(rd.as_of_timestamp AS DATE) - CAST(cor.last_closed_at AS DATE) AS days_since_last_order,
        CAST(rd.as_of_timestamp AS DATE) - CAST(lc.contact_at AS DATE) AS days_since_last_contact
    FROM dim_customer AS dc
    INNER JOIN dim_company AS dco
        ON dco.company_id = dc.company_id
    INNER JOIN customer_order_rollup AS cor
        ON cor.customer_id = dc.customer_id
    LEFT JOIN repeat_device_issues AS rdi
        ON rdi.customer_id = dc.customer_id
    LEFT JOIN quote_loss_summary AS qls
        ON qls.customer_id = dc.customer_id
    LEFT JOIN open_order_summary AS oos
        ON oos.customer_id = dc.customer_id
    LEFT JOIN latest_contact AS lc
        ON lc.customer_id = dc.customer_id
       AND lc.contact_rank = 1
    CROSS JOIN reference_date AS rd
),
scored_candidates AS (
    SELECT
        cs.*,
        (
            CASE
                WHEN cs.days_since_last_order BETWEEN 45 AND 120 THEN 30
                ELSE 0
            END
            + CASE
                WHEN cs.completed_orders >= 2 THEN 15
                ELSE 0
            END
            + CASE
                WHEN COALESCE(cs.days_since_last_contact, 999) > 21 THEN 15
                ELSE 0
            END
            + CASE
                WHEN cs.quote_rejections > 0 THEN 15
                ELSE 0
            END
            + CASE
                WHEN cs.repeat_device_issue_count > 0 THEN 10
                ELSE 0
            END
            + CASE
                WHEN cs.account_type = 'B2B' THEN 10
                ELSE 0
            END
            + CASE
                WHEN cs.open_orders = 0 THEN 5
                ELSE -20
            END
        ) AS recall_priority_score
    FROM customer_snapshot AS cs
),
prioritized_actions AS (
    SELECT
        sc.*,
        CASE
            WHEN sc.open_orders > 0 THEN 'Wait until active service order is resolved'
            WHEN sc.quote_rejections > 0 THEN 'Recover lost quote with targeted follow-up'
            WHEN sc.account_type = 'B2B' AND sc.recall_priority_score >= 50 THEN 'Schedule account review and upsell conversation'
            WHEN sc.recall_priority_score >= 40 THEN 'Launch recall contact via WhatsApp'
            ELSE 'Keep under observation'
        END AS recommended_action,
        DENSE_RANK() OVER (
            PARTITION BY sc.company_name
            ORDER BY
                sc.recall_priority_score DESC,
                sc.total_revenue DESC,
                sc.last_closed_at DESC
        ) AS company_priority_rank
    FROM scored_candidates AS sc
)
SELECT
    customer_name,
    company_name,
    account_type,
    city,
    completed_orders,
    service_lines_used,
    total_revenue,
    last_closed_at,
    days_since_last_order,
    COALESCE(days_since_last_contact, 999) AS days_since_last_contact,
    quote_rejections,
    repeat_device_issue_count,
    latest_contact_type,
    latest_contact_channel,
    latest_contact_outcome,
    recall_priority_score,
    recommended_action,
    company_priority_rank
FROM prioritized_actions
WHERE recall_priority_score > 0
ORDER BY
    recall_priority_score DESC,
    company_name,
    customer_name;

