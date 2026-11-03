-- Reconstructed, result-compatible query based on the saved daily activity CSV.
-- The original BigQuery SQL was not present in the project; verify this query
-- against the original query history before treating it as the source query.
-- Scope: the seven dates present in the exported result (2020-11-01 to 2020-11-07).

SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  event_name,
  COUNT(*) AS total_events,
  COUNT(DISTINCT user_pseudo_id) AS unique_users
FROM
  `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
GROUP BY
  event_date,
  event_name
ORDER BY
  event_date,
  event_name;
