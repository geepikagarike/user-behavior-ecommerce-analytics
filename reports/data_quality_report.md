# Data Quality Report

## Input inventory

| Input table | Rows | Columns | Missing values | Schema validation |
| --- | ---: | --- | ---: | --- |
| daily_activity | 22 | event_date: datetime64[us], event_name: str, total_events: int64, unique_users: int64 | 0 | PASS |
| funnel_rates | 1 | product_view_users: int64, checkout_users: int64, purchase_users: int64, view_to_checkout_pct: float64, checkout_to_purchase_pct: float64, view_to_purchase_pct: float64 | 0 | PASS |
| funnel_counts | 1 | product_view_users: int64, checkout_users: int64, purchase_users: int64 | 0 | PASS |
| event_summary | 4 | event_name: str, total_events: int64, unique_users: int64 | 0 | PASS |

## Validation checks

| Check | Result | Evidence |
| --- | --- | --- |
| Expected four distinct schemas | PASS | All four expected CSV schemas were identified. |
| Required values are present | PASS | No missing values were found in any input table. |
| Numeric metrics are valid | PASS | Counts and rates are finite, non-negative, and in range. |
| Daily date/event keys are unique | PASS | 0 duplicate date/event keys. |
| Overall event names are unique | PASS | 0 duplicate event names. |
| Daily and overall event counts reconcile | PASS | Daily event total: 35,434; overall summary total: 35,434. |
| Funnel count exports agree | PASS | The count-only and count-plus-rate exports were compared. |
| Funnel exports have the expected row grain | PASS | Each funnel export contains exactly one aggregate row. |
| Funnel users match event-specific summary | PASS | Funnel stage counts were compared to the corresponding event-specific user counts. |
| Exported conversion rates match counts | PASS | Recalculated percentages agree within 0.01 percentage points. |

## Scope and reconciliation

- Daily activity contains 22 rows across
  7 dates, from 2020-11-01
  through 2020-11-07.
- Daily and overall event totals reconcile:
  35,434 daily events versus
  35,434 overall events.
- The two funnel exports agree on
  stage counts. Exported rates match the
  rates recalculated from those counts.
- Funnel stage counts match the corresponding
  event-specific user counts in the overall event summary.

## Review notes and limitations

- The export contains 4 add_to_cart events and 1 event-specific user. This is a review item because it is much lower than checkout/purchase counts; it does not by itself prove a tracking error.
- Daily `unique_users` is a daily, event-specific count. It must not be summed
  across dates or event types to represent distinct users across the period.
- No individual-user records are present, so this report cannot validate user
  paths or confirm stage-to-stage membership.
- The original BigQuery SQL files were not present in the workspace. The
  checks compare saved exports; they cannot establish the exact source query
  definitions.

This report is generated from the current CSV exports. Raw files are read-only
inputs to the analysis and are not rewritten.
