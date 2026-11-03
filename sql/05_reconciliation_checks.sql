-- Compare event totals from the daily and overall aggregation grains.
-- A zero difference indicates that the two result sets reconcile.
-- This validation query does not certify the underlying event tracking.

WITH daily_by_date AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS event_date,
    event_name,
    COUNT(*) AS daily_events
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
  GROUP BY
    event_date,
    event_name
),
daily_totals AS (
  SELECT
    event_name,
    SUM(daily_events) AS daily_total_events
  FROM
    daily_by_date
  GROUP BY
    event_name
),
summary_totals AS (
  SELECT
    event_name,
    COUNT(*) AS summary_total_events
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
  GROUP BY
    event_name
)
SELECT
  COALESCE(daily_totals.event_name, summary_totals.event_name) AS event_name,
  daily_total_events,
  summary_total_events,
  COALESCE(daily_total_events, 0) - COALESCE(summary_total_events, 0)
    AS event_count_difference,
  CASE
    WHEN daily_totals.event_name IS NULL THEN 'missing_from_daily'
    WHEN summary_totals.event_name IS NULL THEN 'missing_from_summary'
    ELSE 'present_in_both'
  END AS event_presence
FROM
  daily_totals
FULL OUTER JOIN
  summary_totals
USING (event_name)
ORDER BY
  event_name;
