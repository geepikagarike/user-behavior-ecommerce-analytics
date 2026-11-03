# Power BI Data Dictionary

The Power BI preparation script writes three derived CSV tables to
`data/processed/`. The source BigQuery exports in `data/raw/` remain unchanged.
These tables contain aggregate query results, not individual-user records.

## Source BigQuery result CSVs

The four original files have generated filenames and are identified by their
schemas. Their current row counts are shown below; the EDA script checks these
schemas and does not rely on the filenames.

| Source result | Rows | Column | CSV type | Business meaning |
| --- | ---: | --- | --- | --- |
| Daily activity | 22 | `event_date` | Text (`YYYYMMDD`) | GA4 event date; parsed as a date in the prepared table. |
| Daily activity | 22 | `event_name` | Text | GA4 event type. |
| Daily activity | 22 | `total_events` | Whole number | Events for the date and event type. |
| Daily activity | 22 | `unique_users` | Whole number | Distinct pseudonymous users for this event on this date. |
| Event summary | 4 | `event_name` | Text | GA4 event type. |
| Event summary | 4 | `total_events` | Whole number | Events for this type across the exported period. |
| Event summary | 4 | `unique_users` | Whole number | Distinct pseudonymous users for this type across the period. |
| Funnel counts | 1 | `product_view_users` | Whole number | Users with a reported `view_item` event in the period. |
| Funnel counts | 1 | `checkout_users` | Whole number | Users with a reported `begin_checkout` event in the period. |
| Funnel counts | 1 | `purchase_users` | Whole number | Users with a reported `purchase` event in the period. |
| Funnel counts with rates | 1 | `product_view_users`, `checkout_users`, `purchase_users` | Whole numbers | Same full-period stage counts as the funnel-count export. |
| Funnel counts with rates | 1 | `view_to_checkout_pct`, `checkout_to_purchase_pct`, `view_to_purchase_pct` | Decimal number | Exported conversion ratios in percentage points, rounded to two decimals. |

The funnel result exports each contain one aggregate row. Their counts agree
with each other and with the corresponding event-specific user counts in the
event summary. They do not prove that the same users progressed through
stages.

## `daily_activity.csv`

**Grain:** one row per calendar date and event type.

| Column | Power BI type | Meaning |
| --- | --- | --- |
| `event_date` | Date | Event date parsed from the BigQuery `YYYYMMDD` value and formatted `YYYY-MM-DD`. |
| `event_name` | Text | GA4 event name. |
| `total_events` | Whole number | Number of events of this type on this date. |
| `unique_users` | Whole number | Distinct pseudonymous users for this event on this date only. Do not sum across event types or dates to claim period-unique users. |

## `event_summary.csv`

**Grain:** one row per event type across the exported seven-day period.

| Column | Power BI type | Meaning |
| --- | --- | --- |
| `event_name` | Text | GA4 event name. |
| `total_events` | Whole number | Total events of this type across the period. Matches the sum of daily event counts. |
| `unique_users` | Whole number | Distinct pseudonymous users for this event across the period. Counts can overlap between event types and must not be summed into all-event unique users. |

## `funnel_stages.csv`

**Grain:** one row per reported aggregate funnel stage. Values are derived
from the supplied funnel-count export and the supplied rate export.

| Column | Power BI type | Meaning |
| --- | --- | --- |
| `stage_order` | Whole number | Display order: 1 product view, 2 checkout, 3 purchase. |
| `stage` | Text | Business label for the reported stage. |
| `users` | Whole number | Aggregate stage count from the funnel query. It does not expose user identities or prove stage progression. |
| `previous_stage_users` | Whole number, blank for first stage | Count reported for the preceding stage. |
| `count_difference_from_previous` | Whole number, blank for first stage | Previous reported count minus current reported count. This is a difference between counts, not confirmed individual abandonment. |
| `conversion_from_previous_pct` | Decimal number in percentage points, blank for first stage | Current stage count divided by previous stage count, multiplied by 100 (for example, `16.85` means 16.85%). |
| `conversion_from_product_view_pct` | Decimal number in percentage points | Stage count divided by product-view count, multiplied by 100; 100 for product view. |

## Model notes

- `daily_activity` and `event_summary` have different grains. Do not join them
  directly or add their event counts together; both describe overlapping
  events at different aggregation levels.
- `funnel_stages` is a separate, full-period aggregate. It has no date or event
  key that supports a relationship to the daily event table.
- The exports do not contain a distinct all-event user count. Display this as
  unavailable instead of summing event-specific user counts.
- The event summary reports only 4 `add_to_cart` events from 1
  event-specific user. Validate the original SQL and event tracking before
  interpreting the supplied stages as one sequential funnel.
