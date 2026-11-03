# Project Methodology

## Purpose and scope

This project analyzes four aggregate result exports from the public,
obfuscated GA4 ecommerce sample in BigQuery. The saved results cover
2020-11-01 through 2020-11-07. They contain event and event-specific user
counts, plus full-period funnel stage counts and rates; they do not contain
individual event or user rows.

The analysis is descriptive. It summarizes the supplied sample and does not
establish why users behaved a certain way, whether users followed a sequence
of funnel stages, or how a current ecommerce business is performing.

## Workflow

1. **Preserve source exports.** Keep the four downloaded BigQuery CSVs in
   `data/raw/`. The Python script reads these files and does not write to this
   folder.
2. **Identify and validate inputs.** The script recognizes each CSV by its
   column schema rather than relying on its generated filename. It checks row
   presence, missing values, numeric validity, dates, duplicate keys, and
   consistency between exports.
3. **Reconcile aggregates.** Sum daily event counts by event name and compare
   them with the event-summary export. Compare the two funnel count exports,
   compare stage counts with event-specific users, and recalculate exported
   rates.
4. **Calculate and communicate findings.** Calculate event and daily
   summaries, funnel count ratios, and chart-ready values. Label facts from
   exports separately from recommendations and interpretation limits.
5. **Prepare Power BI inputs.** Write typed, analysis-ready aggregate tables
   to `data/processed/`. These are derived files and can be regenerated.
6. **Build the final dashboard separately.** The project owner imports the
   prepared tables into Power BI Desktop using the implementation guide.

## Metric definitions

- **Total events:** sum of `total_events` in the overall event summary (also
  reconciled to the sum of daily event counts).
- **Event-specific users:** distinct pseudonymous users for one event type
  over the period, as reported by the source query. These counts can overlap
  across event types.
- **View-to-checkout rate:** checkout users / product-view users × 100.
- **Checkout-to-purchase rate:** purchase users / checkout users × 100.
- **View-to-purchase rate:** purchase users / product-view users × 100.
- **Aggregate count drop-off:** 100% − view-to-purchase rate. This compares
  two aggregate counts; it is not measured user-level abandonment.

Rates are recalculated from the exported funnel counts and checked against
the rounded rate export. A rate is not interpreted as a sequential conversion
unless a user-level query confirms shared users and event order.

## Data-quality rules

The analysis expects four distinct input schemas. It rejects empty files,
missing values, invalid dates, non-finite or negative metrics, non-integer
counts, duplicate daily date/event keys, duplicate event-summary names,
inconsistent funnel count exports, and event totals that do not reconcile.
It also verifies that event-specific user counts do not exceed corresponding
event counts and that exported rates are within 0–100%.

The current exports pass these checks: 22 daily rows over seven dates, four
event-summary rows, one row in each funnel export, no missing values, no
duplicate daily keys or event names, and 35,434 daily events matching the
event-summary total. See `reports/data_quality_report.md` for the generated
run-specific report.

## Findings versus recommendations

Counts, dates, and recalculated ratios in the reports are observations from
the supplied CSVs. Suggestions to inspect event definitions, query filters,
instrumentation, or follow-up analyses are recommendations; they are not
measured causes. The low `add_to_cart` result (4 events, 1 event-specific
user) is a validation question, not proof of a tracking defect.

## Limitations

- No distinct all-event user total can be calculated from overlapping
  event-specific counts.
- The exports cannot identify individual journeys, event order, time to
  convert, cohorts, retention, or reasons for non-progression.
- Funnel exports contain no date key, so funnel KPIs cannot be filtered by
  date in Power BI.
- Device, traffic source, geography, product, and revenue analyses are not
  available in these four aggregate exports.
- The seven-day period and obfuscated sample do not support durable trend or
  current-business benchmark claims.
- SQL in `sql/` is reconstructed and has not been run or verified against
  BigQuery query history. See `sql_analysis.md`.
