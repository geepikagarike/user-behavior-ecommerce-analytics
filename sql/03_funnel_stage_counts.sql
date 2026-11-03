-- Reconstructed, result-compatible aggregate stage counts from the saved CSVs.
-- This does not prove that the same users progressed through each stage.
-- Confirm stage definitions and filters against the original query history.

SELECT
  COUNT(DISTINCT IF(event_name = 'view_item', user_pseudo_id, NULL))
    AS product_view_users,
  COUNT(DISTINCT IF(event_name = 'begin_checkout', user_pseudo_id, NULL))
    AS checkout_users,
  COUNT(DISTINCT IF(event_name = 'purchase', user_pseudo_id, NULL))
    AS purchase_users
FROM
  `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20201101' AND '20201107';
