/*
Business question:
How is monthly recurring revenue evolving across SaaS customer segments,
and what portion of movement comes from new, expansion, contraction, or churn?

Assumed synthetic tables:
- dim_account(account_id, account_name, region, industry)
- dim_plan(plan_id, plan_name, plan_tier)
- fact_subscription_snapshot(snapshot_date, account_id, plan_id, mrr_amount, subscription_status)
*/

WITH monthly_account_mrr AS (
    SELECT
        DATE_TRUNC('month', fss.snapshot_date) AS revenue_month,
        fss.account_id,
        da.region,
        da.industry,
        dp.plan_tier,
        SUM(fss.mrr_amount) AS ending_mrr
    FROM fact_subscription_snapshot AS fss
    INNER JOIN dim_account AS da
        ON da.account_id = fss.account_id
    INNER JOIN dim_plan AS dp
        ON dp.plan_id = fss.plan_id
    WHERE fss.snapshot_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months'
      AND fss.subscription_status IN ('active', 'cancelled')
    GROUP BY
        DATE_TRUNC('month', fss.snapshot_date),
        fss.account_id,
        da.region,
        da.industry,
        dp.plan_tier
),
mrr_bridge AS (
    SELECT
        mam.revenue_month,
        mam.account_id,
        mam.region,
        mam.industry,
        mam.plan_tier,
        mam.ending_mrr,
        LAG(mam.ending_mrr) OVER (
            PARTITION BY mam.account_id
            ORDER BY mam.revenue_month
        ) AS previous_mrr
    FROM monthly_account_mrr AS mam
),
classified_mrr_change AS (
    SELECT
        mb.revenue_month,
        mb.account_id,
        mb.region,
        mb.industry,
        mb.plan_tier,
        mb.ending_mrr,
        COALESCE(mb.previous_mrr, 0) AS previous_mrr,
        CASE
            WHEN COALESCE(mb.previous_mrr, 0) = 0 AND mb.ending_mrr > 0 THEN 'new'
            WHEN COALESCE(mb.previous_mrr, 0) > 0 AND mb.ending_mrr = 0 THEN 'churn'
            WHEN mb.ending_mrr > COALESCE(mb.previous_mrr, 0) THEN 'expansion'
            WHEN mb.ending_mrr < COALESCE(mb.previous_mrr, 0) AND mb.ending_mrr > 0 THEN 'contraction'
            ELSE 'stable'
        END AS revenue_movement
    FROM mrr_bridge AS mb
),
segment_monthly_summary AS (
    SELECT
        cmc.revenue_month,
        cmc.region,
        cmc.industry,
        cmc.plan_tier,
        SUM(cmc.previous_mrr) AS starting_mrr,
        SUM(cmc.ending_mrr) AS ending_mrr,
        SUM(
            CASE
                WHEN cmc.revenue_movement = 'new' THEN cmc.ending_mrr
                ELSE 0
            END
        ) AS new_mrr,
        SUM(
            CASE
                WHEN cmc.revenue_movement = 'expansion' THEN cmc.ending_mrr - cmc.previous_mrr
                ELSE 0
            END
        ) AS expansion_mrr,
        SUM(
            CASE
                WHEN cmc.revenue_movement = 'contraction' THEN cmc.previous_mrr - cmc.ending_mrr
                ELSE 0
            END
        ) AS contraction_mrr,
        SUM(
            CASE
                WHEN cmc.revenue_movement = 'churn' THEN cmc.previous_mrr
                ELSE 0
            END
        ) AS churned_mrr
    FROM classified_mrr_change AS cmc
    GROUP BY
        cmc.revenue_month,
        cmc.region,
        cmc.industry,
        cmc.plan_tier
),
ranked_segments AS (
    SELECT
        sms.revenue_month,
        sms.region,
        sms.industry,
        sms.plan_tier,
        sms.starting_mrr,
        sms.ending_mrr,
        sms.new_mrr,
        sms.expansion_mrr,
        sms.contraction_mrr,
        sms.churned_mrr,
        ROUND(
            100.0 * (
                sms.starting_mrr
                + sms.expansion_mrr
                - sms.contraction_mrr
                - sms.churned_mrr
            ) / NULLIF(sms.starting_mrr, 0),
            2
        ) AS net_revenue_retention_pct,
        ROUND(
            100.0 * sms.churned_mrr / NULLIF(sms.starting_mrr, 0),
            2
        ) AS gross_revenue_churn_pct,
        DENSE_RANK() OVER (
            PARTITION BY sms.revenue_month
            ORDER BY sms.ending_mrr DESC
        ) AS segment_rank
    FROM segment_monthly_summary AS sms
)
SELECT
    revenue_month,
    region,
    industry,
    plan_tier,
    starting_mrr,
    ending_mrr,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churned_mrr,
    net_revenue_retention_pct,
    gross_revenue_churn_pct,
    segment_rank
FROM ranked_segments
ORDER BY revenue_month DESC, segment_rank, region, industry;

