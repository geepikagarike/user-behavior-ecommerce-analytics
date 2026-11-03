# SQL Analysis Documentation

## Provenance and execution status

The original BigQuery query text was not present in the project workspace.
The files below are reconstructed GoogleSQL query definitions intended to
match the exported result schemas and the seven-day period. They are not
verified copies of the original queries, and they have not been executed
from this project. Compare them with BigQuery query history before claiming
they generated the saved CSVs.

All analysis queries read the public table family
`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` and filter
`_TABLE_SUFFIX` from `20201101` through `20201107`.

## Query inventory

| File | Purpose | Output grain |
| --- | --- | --- |
| `01_daily_activity.sql` | Count events and event-specific users by parsed event date and event name. | One row per date and event name. |
| `02_event_summary.sql` | Count events and event-specific users across the selected period. | One row per event name. |
| `03_funnel_stage_counts.sql` | Count distinct pseudonymous users with `view_item`, `begin_checkout`, and `purchase` events in the period. | One aggregate row. |
| `04_conversion_rates.sql` | Recalculate the three ratios from the same aggregate stage counts using `SAFE_DIVIDE`. | One aggregate row with counts and rounded percentage-point values. |
| `05_reconciliation_checks.sql` | Compare per-event totals when aggregated daily versus over the full period; return counts, differences, and presence labels. | One row per event name appearing in either aggregation. |

## Interpretation notes

- `unique_users` is distinct within the event type and query period or date.
  Summing these counts across event types does not produce an all-event
  distinct-user count.
- The funnel query counts users who had each event somewhere in the time
  window. It does not check whether the same users entered stages in order.
- The conversion rates are ratios of aggregate stage counts. They are not
  verified journey conversion rates without user-level overlap and ordering.
- The reconciliation query compares two aggregations of the same source
  table and date filter. It checks aggregation consistency; it does not
  independently prove the source exports or event instrumentation are
  correct.
- The result CSVs currently show 4 `add_to_cart` events and 1
  event-specific user, compared with 1,411 `begin_checkout` events and 273
  `purchase` events. Confirm source query filters and event definitions
  before interpreting this as a conventional ecommerce funnel.

## Reproducibility

The `.sql` files are for review and manual execution in BigQuery. No Python
script in this repository submits SQL to BigQuery. Save any verified original
queries separately and preserve the reconstructed-query caveat until their
provenance is confirmed.
