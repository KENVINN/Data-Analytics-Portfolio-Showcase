/*
Business question:
Which members are consistently engaged, starting to slip, inactive,
or returning after a long inactivity gap?

Assumed synthetic tables:
- dim_member(member_id, partner_id, signup_date, membership_status)
- dim_partner(partner_id, partner_name, region)
- fact_membership(member_id, plan_name, monthly_fee, membership_start_date, membership_end_date)
- fact_checkin(member_id, checkin_timestamp)
*/

WITH ordered_checkins AS (
    SELECT
        fc.member_id,
        CAST(fc.checkin_timestamp AS DATE) AS checkin_date,
        LAG(CAST(fc.checkin_timestamp AS DATE)) OVER (
            PARTITION BY fc.member_id
            ORDER BY CAST(fc.checkin_timestamp AS DATE)
        ) AS previous_checkin_date
    FROM fact_checkin AS fc
),
checkin_gaps AS (
    SELECT
        oc.member_id,
        oc.checkin_date,
        oc.previous_checkin_date,
        oc.checkin_date - oc.previous_checkin_date AS inactivity_gap_days
    FROM ordered_checkins AS oc
),
reactivation_events AS (
    SELECT
        cg.member_id,
        cg.checkin_date AS reactivated_on,
        cg.inactivity_gap_days
    FROM checkin_gaps AS cg
    WHERE cg.inactivity_gap_days >= 45
),
member_activity AS (
    SELECT
        fc.member_id,
        MAX(CAST(fc.checkin_timestamp AS DATE)) AS last_checkin_date,
        COUNT(*) FILTER (
            WHERE CAST(fc.checkin_timestamp AS DATE) >= CURRENT_DATE - INTERVAL '30 days'
        ) AS visits_last_30d,
        COUNT(*) FILTER (
            WHERE CAST(fc.checkin_timestamp AS DATE) >= CURRENT_DATE - INTERVAL '90 days'
        ) AS visits_last_90d
    FROM fact_checkin AS fc
    GROUP BY fc.member_id
),
reactivation_summary AS (
    SELECT
        re.member_id,
        COUNT(*) AS total_reactivation_events,
        MAX(re.reactivated_on) AS last_reactivation_date
    FROM reactivation_events AS re
    GROUP BY re.member_id
),
current_member_state AS (
    SELECT
        dm.member_id,
        dp.partner_name,
        dp.region,
        fm.plan_name,
        fm.monthly_fee,
        dm.signup_date,
        ma.last_checkin_date,
        COALESCE(ma.visits_last_30d, 0) AS visits_last_30d,
        COALESCE(ma.visits_last_90d, 0) AS visits_last_90d,
        COALESCE(rs.total_reactivation_events, 0) AS total_reactivation_events,
        rs.last_reactivation_date,
        CURRENT_DATE - ma.last_checkin_date AS days_since_last_checkin,
        CASE
            WHEN ma.last_checkin_date IS NULL THEN 'never_activated'
            WHEN CURRENT_DATE - ma.last_checkin_date <= 14 AND ma.visits_last_30d >= 6 THEN 'highly_engaged'
            WHEN CURRENT_DATE - ma.last_checkin_date <= 21 AND ma.visits_last_90d >= 10 THEN 'consistent'
            WHEN CURRENT_DATE - ma.last_checkin_date BETWEEN 22 AND 45 THEN 'slipping'
            WHEN rs.last_reactivation_date = ma.last_checkin_date THEN 'reactivated'
            ELSE 'inactive'
        END AS lifecycle_segment
    FROM dim_member AS dm
    INNER JOIN dim_partner AS dp
        ON dp.partner_id = dm.partner_id
    LEFT JOIN fact_membership AS fm
        ON fm.member_id = dm.member_id
       AND fm.membership_end_date IS NULL
    LEFT JOIN member_activity AS ma
        ON ma.member_id = dm.member_id
    LEFT JOIN reactivation_summary AS rs
        ON rs.member_id = dm.member_id
    WHERE dm.membership_status IN ('active', 'paused')
),
segment_summary AS (
    SELECT
        cms.partner_name,
        cms.region,
        cms.plan_name,
        cms.lifecycle_segment,
        COUNT(*) AS members_in_segment,
        ROUND(AVG(cms.monthly_fee), 2) AS avg_monthly_fee,
        ROUND(AVG(cms.days_since_last_checkin), 2) AS avg_days_since_last_checkin,
        ROUND(
            100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (PARTITION BY cms.partner_name), 0),
            2
        ) AS segment_mix_pct,
        DENSE_RANK() OVER (
            PARTITION BY cms.partner_name
            ORDER BY COUNT(*) DESC
        ) AS segment_rank_within_partner
    FROM current_member_state AS cms
    GROUP BY
        cms.partner_name,
        cms.region,
        cms.plan_name,
        cms.lifecycle_segment
)
SELECT
    partner_name,
    region,
    plan_name,
    lifecycle_segment,
    members_in_segment,
    avg_monthly_fee,
    avg_days_since_last_checkin,
    segment_mix_pct,
    segment_rank_within_partner
FROM segment_summary
ORDER BY partner_name, segment_rank_within_partner, lifecycle_segment;

