-- Reconstructed, result-compatible query based on the saved event summary CSV.
-- The original BigQuery SQL was not present in the project; verify this query
-- against the original query history before treating it as the source query.
-- The date range matches the daily activity export.

SELECT
  event_name,
  COUNT(*) AS total_events,
  COUNT(DISTINCT user_pseudo_id) AS unique_users
FROM
  `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
GROUP BY
  event_name
ORDER BY
  total_events DESC;
