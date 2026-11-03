-- Reconstructed conversion-rate calculation based on the saved funnel results.
-- Ratios use aggregate distinct-user counts; they do not prove user-level paths.

WITH funnel_counts AS (
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
    _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
)
SELECT
  product_view_users,
  checkout_users,
  purchase_users,
  ROUND(SAFE_DIVIDE(checkout_users, product_view_users) * 100, 2)
    AS view_to_checkout_pct,
  ROUND(SAFE_DIVIDE(purchase_users, checkout_users) * 100, 2)
    AS checkout_to_purchase_pct,
  ROUND(SAFE_DIVIDE(purchase_users, product_view_users) * 100, 2)
    AS view_to_purchase_pct
FROM
  funnel_counts;
