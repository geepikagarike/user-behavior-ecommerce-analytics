# Power BI Implementation Guide

This guide prepares the existing analytics for a Power BI report that the
project owner will build in Power BI Desktop. It does not create a Power BI
file or dashboard application.

## 1. Prepare and import the CSVs

From the project root, run:

```powershell
python src\analysis\eda_analysis.py --prepare-only
```

In Power BI Desktop, select **Get data → Text/CSV** and import:

1. `data/processed/daily_activity.csv`
2. `data/processed/event_summary.csv`
3. `data/processed/funnel_stages.csv`

In Power Query, confirm the column types using
[`powerbi_data_dictionary.md`](./powerbi_data_dictionary.md). Set
`daily_activity[event_date]` to **Date**, counts and `stage_order` to **Whole
number**, rate columns to **Decimal number**, and names/labels to **Text**.
The prepared funnel rate columns use percentage points (for example, `16.85`
means 16.85); divide by 100 before applying Power BI's percentage formatting
if you display those columns directly. The DAX measures below already return
fractional rates and can be formatted as percentages.
Keep the first-stage blanks in `funnel_stages` blank; they do not represent a
zero conversion rate.

## 2. Recommended model

Use a small star-style model for the available aggregates:

- Create a Date dimension in Power BI and relate
  `Date[Date]` **one-to-many** to `daily_activity[event_date]`.
- Create an Event dimension from distinct `event_name` values and relate it
  **one-to-many** to both `daily_activity[event_name]` and
  `event_summary[event_name]`.
- Keep `funnel_stages` **disconnected**. It is a full-period aggregate with no
  date key. Do not create a relationship from it to daily activity.
- Do not directly relate `daily_activity` to `event_summary`; their grains
  differ and their event counts overlap.

Example calculated tables:

```DAX
Date =
CALENDAR (
    MIN ( daily_activity[event_date] ),
    MAX ( daily_activity[event_date] )
)
```

```DAX
Event =
DISTINCT (
    UNION (
        SELECTCOLUMNS ( daily_activity, "event_name", daily_activity[event_name] ),
        SELECTCOLUMNS ( event_summary, "event_name", event_summary[event_name] )
    )
)
```

Mark `Date` as the date table and create the relationships described above.
Use single-direction filtering from dimensions to facts.

## 3. Suggested DAX measures

These measures use the table and column names from the prepared CSVs.

```DAX
Total Events =
SUM ( daily_activity[total_events] )
```

```DAX
Product View Users =
CALCULATE (
    MAX ( funnel_stages[users] ),
    funnel_stages[stage] = "Product view"
)
```

```DAX
Checkout Users =
CALCULATE (
    MAX ( funnel_stages[users] ),
    funnel_stages[stage] = "Checkout"
)
```

```DAX
Purchase Users =
CALCULATE (
    MAX ( funnel_stages[users] ),
    funnel_stages[stage] = "Purchase"
)
```

```DAX
View to Checkout Rate =
DIVIDE ( [Checkout Users], [Product View Users] )
```

```DAX
Checkout to Purchase Rate =
DIVIDE ( [Purchase Users], [Checkout Users] )
```

```DAX
View to Purchase Rate =
DIVIDE ( [Purchase Users], [Product View Users] )
```

```DAX
Overall Funnel Count Drop-off =
1 - [View to Purchase Rate]
```

Format rates as percentages. The funnel measures are full-period because
`funnel_stages.csv` has no date column. The date slicer must not be presented as
filtering those measures.

Do not create a `DISTINCTCOUNT` measure from these aggregate tables. There is
no user ID column and no all-event distinct-user count. The `unique_users`
values in the daily table are event-specific daily counts; summing them across
dates or event types double-counts users.

## 4. Recommended report layout

### Page 1 — Executive overview

- KPI cards: Total Events, Product View Users, Checkout Users, Purchase Users,
  View-to-Checkout Rate, View-to-Purchase Rate, and Overall Funnel Count
  Drop-off.
- A clearly labeled note: **All-event unique users are unavailable in these
  exports.**
- A funnel or horizontal bar chart with the three reported stage counts.
- A visible caveat that these are aggregate stage-count comparisons, not
  confirmed individual journeys.

### Page 2 — Event and daily activity

- Line chart: `event_date` by `total_events`, with `event_name` as legend.
- Bar chart: event type by total period events using `event_summary`.
- Optional table: event type, period event count, event-specific period users.
- Slicers: Date from the Date dimension and Event from the Event dimension.
- The Date slicer filters `daily_activity`, not the full-period
  `event_summary` table; label the latter as a fixed-period comparison.
- Do not total event-specific users across categories as if they were unique
  people.

### Page 3 — Conversion analysis

- Ordered funnel/bar chart from `funnel_stages[stage_order]` and
  `funnel_stages[users]`.
- Conversion-rate bars or cards for view-to-checkout,
  checkout-to-purchase, and view-to-purchase.
- A count-difference table for each stage transition.
- A note highlighting the unusually small `add_to_cart` event count (4 events,
  1 event-specific user) and the need to verify its SQL/tracking definition.
- Keep the funnel full-period; the exports do not contain dates for the funnel
  counts.

## 5. Reconciliation and interpretation checks

- Confirm total events equals **35,434** for the full selected date range and
  all event types.
- Confirm funnel counts are **4,937** product-view users, **832** checkout
  users, and **224** purchase users.
- Confirm rates are approximately **16.85%**, **26.92%**, and **4.54%**.
- The daily and overall event exports reconcile. Do not add their event
  totals together because they are two views of the same records.
- Describe the 95.46% figure as **aggregate funnel count drop-off**, not
  observed user abandonment. The CSVs do not contain user-level journeys.
- The SQL files in `sql/` are reconstructed from the result schemas because
  the original SQL was not saved in this workspace. Verify their definitions
  against BigQuery query history before presenting them as the original query
  logic.
