/*
Business question:
Which gym partners are driving the strongest member engagement,
and which accounts show early signs of churn risk?

Assumed synthetic tables:
- dim_partner(partner_id, partner_name, region, contract_status)
- dim_member(member_id, partner_id, signup_date, membership_status)
- fact_checkin(member_id, checkin_timestamp)
- fact_class_booking(member_id, class_start_at, booking_status)
*/

WITH member_base AS (
    SELECT
        m.member_id,
        m.partner_id,
        m.signup_date
    FROM dim_member AS m
    WHERE m.membership_status = 'active'
),
monthly_checkins AS (
    SELECT
        mb.partner_id,
        fc.member_id,
        DATE_TRUNC('month', fc.checkin_timestamp) AS activity_month,
        COUNT(*) AS total_checkins,
        COUNT(DISTINCT CAST(fc.checkin_timestamp AS DATE)) AS active_days,
        MAX(CAST(fc.checkin_timestamp AS DATE)) AS last_checkin_date
    FROM member_base AS mb
    INNER JOIN fact_checkin AS fc
        ON fc.member_id = mb.member_id
    WHERE fc.checkin_timestamp >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '4 months'
    GROUP BY
        mb.partner_id,
        fc.member_id,
        DATE_TRUNC('month', fc.checkin_timestamp)
),
monthly_class_behavior AS (
    SELECT
        mb.partner_id,
        fcb.member_id,
        DATE_TRUNC('month', fcb.class_start_at) AS activity_month,
        COUNT(*) FILTER (WHERE fcb.booking_status = 'completed') AS classes_completed,
        COUNT(*) FILTER (WHERE fcb.booking_status IN ('cancelled', 'no_show')) AS classes_missed
    FROM member_base AS mb
    INNER JOIN fact_class_booking AS fcb
        ON fcb.member_id = mb.member_id
    WHERE fcb.class_start_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '4 months'
    GROUP BY
        mb.partner_id,
        fcb.member_id,
        DATE_TRUNC('month', fcb.class_start_at)
),
member_monthly_engagement AS (
    SELECT
        mc.partner_id,
        mc.member_id,
        mc.activity_month,
        mc.total_checkins,
        mc.active_days,
        COALESCE(mcb.classes_completed, 0) AS classes_completed,
        COALESCE(mcb.classes_missed, 0) AS classes_missed,
        mc.last_checkin_date
    FROM monthly_checkins AS mc
    LEFT JOIN monthly_class_behavior AS mcb
        ON mcb.partner_id = mc.partner_id
       AND mcb.member_id = mc.member_id
       AND mcb.activity_month = mc.activity_month
),
partner_monthly_metrics AS (
    SELECT
        mme.partner_id,
        mme.activity_month,
        COUNT(DISTINCT mme.member_id) AS engaged_members,
        ROUND(AVG(mme.total_checkins), 2) AS avg_checkins_per_member,
        ROUND(AVG(mme.classes_completed), 2) AS avg_classes_completed,
        SUM(
            CASE
                WHEN mme.last_checkin_date < CURRENT_DATE - INTERVAL '30 days' THEN 1
                ELSE 0
            END
        ) AS members_at_risk,
        ROUND(
            AVG(mme.total_checkins) * 0.50
            + AVG(mme.classes_completed) * 0.35
            - AVG(mme.classes_missed) * 0.15,
            2
        ) AS engagement_score
    FROM member_monthly_engagement AS mme
    GROUP BY
        mme.partner_id,
        mme.activity_month
),
partner_trend AS (
    SELECT
        pmm.partner_id,
        pmm.activity_month,
        pmm.engaged_members,
        pmm.avg_checkins_per_member,
        pmm.avg_classes_completed,
        pmm.members_at_risk,
        pmm.engagement_score,
        LAG(pmm.engaged_members) OVER (
            PARTITION BY pmm.partner_id
            ORDER BY pmm.activity_month
        ) AS previous_month_engaged_members,
        LAG(pmm.engagement_score) OVER (
            PARTITION BY pmm.partner_id
            ORDER BY pmm.activity_month
        ) AS previous_month_engagement_score,
        ROW_NUMBER() OVER (
            PARTITION BY pmm.partner_id
            ORDER BY pmm.activity_month DESC
        ) AS recency_rank
    FROM partner_monthly_metrics AS pmm
),
latest_partner_snapshot AS (
    SELECT
        pt.partner_id,
        pt.activity_month,
        pt.engaged_members,
        pt.avg_checkins_per_member,
        pt.avg_classes_completed,
        pt.members_at_risk,
        pt.engagement_score,
        COALESCE(pt.engaged_members - pt.previous_month_engaged_members, 0) AS member_delta_vs_previous_month,
        COALESCE(pt.engagement_score - pt.previous_month_engagement_score, 0) AS score_delta_vs_previous_month
    FROM partner_trend AS pt
    WHERE pt.recency_rank = 1
)
SELECT
    dp.partner_name,
    dp.region,
    lps.activity_month,
    lps.engaged_members,
    lps.avg_checkins_per_member,
    lps.avg_classes_completed,
    lps.members_at_risk,
    ROUND(100.0 * lps.members_at_risk / NULLIF(lps.engaged_members, 0), 2) AS at_risk_member_pct,
    lps.engagement_score,
    lps.member_delta_vs_previous_month,
    lps.score_delta_vs_previous_month,
    DENSE_RANK() OVER (
        ORDER BY lps.engagement_score DESC, lps.engaged_members DESC
    ) AS engagement_rank
FROM latest_partner_snapshot AS lps
INNER JOIN dim_partner AS dp
    ON dp.partner_id = lps.partner_id
WHERE dp.contract_status = 'active'
ORDER BY engagement_rank, dp.partner_name;

