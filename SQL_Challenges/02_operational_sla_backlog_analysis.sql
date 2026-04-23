/*
Business question:
Which technicians and service lines are driving SLA breaches,
and where is backlog aging accumulating inside the operation?

Assumed synthetic tables:
- dim_technician(technician_id, technician_name, squad_name, specialty)
- fact_service_order(order_id, customer_id, company_id, technician_id, service_line, device_type, service_mode, opened_at, first_response_at, quoted_at, approved_at, closed_at, order_status, quoted_amount, approved_revenue, priority, sla_target_hours)
- fact_order_status_history(status_id, order_id, status_name, status_at)
*/

WITH reference_date AS (
    SELECT
        MAX(CAST(status_at AS TIMESTAMP)) AS as_of_timestamp
    FROM fact_order_status_history
),
status_flow AS (
    SELECT
        fosh.order_id,
        fosh.status_name,
        CAST(fosh.status_at AS TIMESTAMP) AS status_at,
        LEAD(CAST(fosh.status_at AS TIMESTAMP)) OVER (
            PARTITION BY fosh.order_id
            ORDER BY CAST(fosh.status_at AS TIMESTAMP)
        ) AS next_status_at
    FROM fact_order_status_history AS fosh
),
stage_durations AS (
    SELECT
        sf.order_id,
        ROUND(
            SUM(
                CASE
                    WHEN sf.status_name = 'awaiting_part'
                    THEN EXTRACT(EPOCH FROM (COALESCE(sf.next_status_at, rd.as_of_timestamp) - sf.status_at)) / 3600
                    ELSE 0
                END
            ),
            2
        ) AS hours_in_awaiting_part,
        ROUND(
            SUM(
                CASE
                    WHEN sf.status_name = 'in_repair'
                    THEN EXTRACT(EPOCH FROM (COALESCE(sf.next_status_at, rd.as_of_timestamp) - sf.status_at)) / 3600
                    ELSE 0
                END
            ),
            2
        ) AS hours_in_repair,
        ROUND(
            SUM(
                CASE
                    WHEN sf.status_name = 'ready_for_pickup'
                    THEN EXTRACT(EPOCH FROM (COALESCE(sf.next_status_at, rd.as_of_timestamp) - sf.status_at)) / 3600
                    ELSE 0
                END
            ),
            2
        ) AS hours_ready_for_pickup
    FROM status_flow AS sf
    CROSS JOIN reference_date AS rd
    GROUP BY sf.order_id
),
recent_orders AS (
    SELECT
        fso.order_id,
        fso.technician_id,
        fso.service_line,
        fso.order_status,
        CAST(fso.opened_at AS TIMESTAMP) AS opened_at,
        CAST(fso.first_response_at AS TIMESTAMP) AS first_response_at,
        CAST(fso.closed_at AS TIMESTAMP) AS closed_at,
        fso.sla_target_hours,
        ROUND(
            EXTRACT(EPOCH FROM (CAST(fso.first_response_at AS TIMESTAMP) - CAST(fso.opened_at AS TIMESTAMP))) / 3600,
            2
        ) AS first_response_hours,
        ROUND(
            EXTRACT(EPOCH FROM (CAST(fso.closed_at AS TIMESTAMP) - CAST(fso.opened_at AS TIMESTAMP))) / 3600,
            2
        ) AS resolution_hours
    FROM fact_service_order AS fso
    CROSS JOIN reference_date AS rd
    WHERE CAST(fso.opened_at AS DATE) >= CAST(rd.as_of_timestamp AS DATE) - INTERVAL '90 days'
),
closed_order_kpis AS (
    SELECT
        ro.technician_id,
        ro.service_line,
        COUNT(*) FILTER (WHERE ro.closed_at IS NOT NULL) AS closed_orders,
        ROUND(AVG(ro.first_response_hours) FILTER (WHERE ro.closed_at IS NOT NULL), 2) AS avg_first_response_hours,
        ROUND(AVG(ro.resolution_hours) FILTER (WHERE ro.closed_at IS NOT NULL), 2) AS avg_resolution_hours,
        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE ro.closed_at IS NOT NULL
                  AND ro.resolution_hours <= ro.sla_target_hours
            ) / NULLIF(COUNT(*) FILTER (WHERE ro.closed_at IS NOT NULL), 0),
            2
        ) AS sla_attainment_pct
    FROM recent_orders AS ro
    GROUP BY
        ro.technician_id,
        ro.service_line
),
active_backlog AS (
    SELECT
        ro.technician_id,
        ro.service_line,
        COUNT(*) FILTER (
            WHERE ro.order_status IN ('awaiting_part', 'in_repair', 'ready_for_pickup')
        ) AS open_backlog_orders,
        COUNT(*) FILTER (
            WHERE ro.order_status IN ('awaiting_part', 'in_repair', 'ready_for_pickup')
              AND EXTRACT(EPOCH FROM (rd.as_of_timestamp - ro.opened_at)) / 3600 > 72
        ) AS backlog_over_72h,
        ROUND(
            AVG(
                EXTRACT(EPOCH FROM (rd.as_of_timestamp - ro.opened_at)) / 3600
            ) FILTER (
                WHERE ro.order_status IN ('awaiting_part', 'in_repair', 'ready_for_pickup')
            ),
            2
        ) AS avg_open_hours
    FROM recent_orders AS ro
    CROSS JOIN reference_date AS rd
    GROUP BY
        ro.technician_id,
        ro.service_line
),
stage_summary AS (
    SELECT
        ro.technician_id,
        ro.service_line,
        ROUND(AVG(COALESCE(sd.hours_in_awaiting_part, 0)), 2) AS avg_hours_waiting_parts,
        ROUND(AVG(COALESCE(sd.hours_in_repair, 0)), 2) AS avg_hours_in_repair,
        ROUND(AVG(COALESCE(sd.hours_ready_for_pickup, 0)), 2) AS avg_hours_ready_for_pickup
    FROM recent_orders AS ro
    LEFT JOIN stage_durations AS sd
        ON sd.order_id = ro.order_id
    GROUP BY
        ro.technician_id,
        ro.service_line
),
technician_snapshot AS (
    SELECT
        dt.technician_name,
        dt.squad_name,
        dt.specialty,
        cok.service_line,
        cok.closed_orders,
        cok.avg_first_response_hours,
        cok.avg_resolution_hours,
        cok.sla_attainment_pct,
        COALESCE(ab.open_backlog_orders, 0) AS open_backlog_orders,
        COALESCE(ab.backlog_over_72h, 0) AS backlog_over_72h,
        COALESCE(ab.avg_open_hours, 0) AS avg_open_hours,
        COALESCE(ss.avg_hours_waiting_parts, 0) AS avg_hours_waiting_parts,
        COALESCE(ss.avg_hours_in_repair, 0) AS avg_hours_in_repair,
        COALESCE(ss.avg_hours_ready_for_pickup, 0) AS avg_hours_ready_for_pickup
    FROM closed_order_kpis AS cok
    INNER JOIN dim_technician AS dt
        ON dt.technician_id = cok.technician_id
    LEFT JOIN active_backlog AS ab
        ON ab.technician_id = cok.technician_id
       AND ab.service_line = cok.service_line
    LEFT JOIN stage_summary AS ss
        ON ss.technician_id = cok.technician_id
       AND ss.service_line = cok.service_line
),
ranked_technicians AS (
    SELECT
        ts.*,
        DENSE_RANK() OVER (
            ORDER BY
                ts.sla_attainment_pct DESC,
                ts.open_backlog_orders ASC,
                ts.avg_resolution_hours ASC
        ) AS efficiency_rank
    FROM technician_snapshot AS ts
)
SELECT
    technician_name,
    squad_name,
    specialty,
    service_line,
    closed_orders,
    avg_first_response_hours,
    avg_resolution_hours,
    sla_attainment_pct,
    open_backlog_orders,
    backlog_over_72h,
    avg_open_hours,
    avg_hours_waiting_parts,
    avg_hours_in_repair,
    avg_hours_ready_for_pickup,
    efficiency_rank
FROM ranked_technicians
ORDER BY efficiency_rank, technician_name, service_line;

