# EDA Business Insights

## Dataset scope

- The inputs are four aggregate BigQuery query results; they do not contain individual-user records.
- Daily activity covers 2020-11-01 through
  2020-11-07 (7 dates).
- The event summary contains 35,434 events in total. Its per-event
  event counts reconcile exactly with the daily activity export.
- Missing values, duplicate daily date/event keys, negative metrics, and
  mismatched funnel counts were checked by the EDA script.

## Findings supported by the exports

- The busiest date by recorded event count was 2020-11-03, with
  6,072 events.
- Average daily event volume was 5,062; the lowest
  daily total was 3,525 on 2020-11-01.
- The most frequent event was `view_item` with
  33,746 events.
- `view_item` represented
  95.24% of recorded events.
- The supplied funnel counts were 4,937 product-view
  users, 832 checkout users, and
  224 purchase users.
- Rates recalculated from those counts are 16.85% from
  view to checkout, 26.92% from checkout to
  purchase, and 4.54% from view to purchase. These
  match the rounded rates in the export.

## Event summary

- `view_item`: 33,746 events and 95.24% of recorded events; 4,937 event-specific users.
- `begin_checkout`: 1,411 events and 3.98% of recorded events; 832 event-specific users.
- `purchase`: 273 events and 0.77% of recorded events; 224 event-specific users.
- `add_to_cart`: 4 events and 0.01% of recorded events; 1 event-specific user.

## Daily event-specific user activity

- `add_to_cart` daily event-specific users ranged from 1 on 2020-11-01 to 1 on 2020-11-01.
- `begin_checkout` daily event-specific users ranged from 91 on 2020-11-01 to 152 on 2020-11-06.
- `purchase` daily event-specific users ranged from 13 on 2020-11-01 to 48 on 2020-11-06.
- `view_item` daily event-specific users ranged from 516 on 2020-11-01 to 944 on 2020-11-03.

These are distinct-user counts for each event type on each date. They overlap
across event types and dates; they must not be added to estimate daily or
period-wide distinct users. Across this seven-day window, `view_item` daily
user counts peaked on 2020-11-03, while `begin_checkout` and `purchase` daily
user counts peaked on 2020-11-06. These separate aggregates do not show that
the same users progressed between events.

## Interpretation limits and data checks

- User counts are aggregated by event. They cannot show individual journeys,
  cohort retention, repeat purchasing, or time between funnel steps.
- Daily `unique_users` values are event-specific. Adding them across event
  types or dates would double-count users and must not be presented as a
  distinct-user total.
- The event summary contains 4 `add_to_cart` events from 1 event-specific user. This is much smaller than the reported checkout and
  purchase counts. The funnel export has no add-to-cart stage, so the standard
  view → add-to-cart → checkout → purchase path cannot be validated from these
  files. Confirm the SQL event names, filters, date ranges, and funnel
  definitions before interpreting the aggregate funnel as a sequential path.
- The funnel counts do not identify which users proceeded between stages.
  Treat the supplied conversion percentages as aggregate ratios, not as
  user-level journey evidence or causal explanations.

## Outputs

- `outputs/visualizations/event_distribution.png`
- `outputs/visualizations/daily_user_activity.png`
- `outputs/visualizations/ecommerce_conversion_funnel.png`
- `outputs/visualizations/conversion_rates.png`

No raw CSVs are modified. No cleaned CSV is exported because these inputs are
already aggregated query results and this EDA does not require a separate
cleaned dataset.
