# Business Insights and KPI Analysis

## Executive summary

The four BigQuery result exports cover seven days, from 2020-11-01 through
2020-11-07. They contain **35,434 events** across four event types. The
event-summary totals match the sum of the daily activity export.

The funnel exports report 4,937 product-view users, 832 checkout users, and
224 purchase users. The corresponding view-to-checkout rate is 16.85%, the
checkout-to-purchase rate is 26.92%, and the overall view-to-purchase rate is
4.54%. These ratios are mathematically consistent with the exported counts
and with the corresponding event-specific user counts.

These are aggregate comparisons. The exports do not contain individual-user
records, so they cannot verify individual paths, stage order, or the reasons
for differences between reported counts.

## Evidence and recommendations

The KPI values and dated event observations below are **findings directly
supported by the CSV exports**. Recommendations are labeled separately and
should be treated as follow-up actions, not as measured causes.

## KPI summary

| KPI | Value | Definition and scope |
| --- | ---: | --- |
| Total events | 35,434 | Sum of event counts; reconciles between the daily and overall event exports. |
| Unique users across all events | Not available | Event-specific user counts overlap; there is no distinct all-event user total in the supplied results. |
| Product-view users | 4,937 | Full-period product-view user count reported by the funnel query. |
| Checkout users | 832 | Full-period checkout user count reported by the funnel query. |
| Purchase users | 224 | Full-period purchase user count reported by the funnel query. |
| Checkout conversion rate | 16.85% | 832 checkout users / 4,937 product-view users. |
| Purchase conversion rate | 4.54% | 224 purchase users / 4,937 product-view users. |
| Checkout-to-purchase rate | 26.92% | 224 purchase users / 832 checkout users. |
| Overall funnel count drop-off | 95.46% | 100% minus the reported purchase-to-product-view ratio; a count comparison, not verified user-level abandonment. |

## Key findings from the exports

- `view_item` is the most frequent event: 33,746 events and 4,937
  event-specific users; it represents 95.24% of all recorded events.
- `begin_checkout` has 1,411 events and 832 event-specific users.
- `purchase` has 273 events and 224 event-specific users.
- `add_to_cart` has 4 events and 1 event-specific user. This is unexpectedly
  low (0.01% of recorded events) relative to the checkout and purchase counts
  and should be investigated before using it as a funnel stage.
- The busiest date in the daily export is 2020-11-03, with 6,072 events.
- Average daily activity was 5,062 events; the lowest daily total was 3,525
  on 2020-11-01.
- Daily event volume increased from 3,525 on 2020-11-01 to that peak, then
  ended at 4,134 on 2020-11-07. The seven-day window is too short to establish
  a durable trend or explain the day-to-day changes.
- The daily event totals sum to 35,434 and match the event-summary total.

## Daily event-specific user activity

The daily export counts distinct users separately for each event type and
date. The reported counts peaked at:

| Event | Lowest daily count | Highest daily count |
| --- | --- | --- |
| `view_item` | 516 on 2020-11-01 | 944 on 2020-11-03 |
| `begin_checkout` | 91 on 2020-11-01 | 152 on 2020-11-06 |
| `purchase` | 13 on 2020-11-01 | 48 on 2020-11-06 |
| `add_to_cart` | 1 on 2020-11-01 | 1 on 2020-11-01 |

These are event-specific daily counts, not disjoint populations. They cannot
be added across dates or events to calculate daily or period-wide unique
users. The peak dates differ for product views versus checkout and purchase;
the aggregate data cannot establish that the same users progressed between
stages or explain the difference.

## Funnel count comparison

| Comparison | Reported counts | Count difference | Rate |
| --- | ---: | ---: | ---: |
| Product view → checkout | 4,937 → 832 | 4,105 fewer at checkout | 16.85% continue by aggregate ratio |
| Checkout → purchase | 832 → 224 | 608 fewer at purchase | 26.92% continue by aggregate ratio |
| Product view → purchase | 4,937 → 224 | 4,713 fewer at purchase | 4.54% continue; 95.46% count drop-off |

The largest count difference is between product view and checkout. This
identifies where the exported counts differ most, but not where specific users
abandoned. The queries provide stage totals rather than user paths, and the
event summary's `add_to_cart` count does not align with an intuitive
view → add-to-cart → checkout → purchase sequence. Check query event names,
filters, date windows, and stage definitions before labeling these differences
as actual user abandonment.

## Recommendations (not measured causes)

These are recommended validation steps based on data quality and scope, not
claims about why users behave a certain way:

1. **Validate funnel definitions first.** Review the original BigQuery query
   logic and confirm that all stages use compatible date ranges, user
   identifiers, event definitions, and inclusion rules.
2. **Investigate `add_to_cart` tracking.** Check whether the low count is
   expected for this sample or caused by the event definition/filter. Do not
   diagnose checkout behavior from this count until it is reconciled.
3. **Prioritize the view-to-checkout step for follow-up analysis.** It has the
   largest aggregate count difference. Treat this as a question for further
   investigation, not proof of a UX or product problem.
4. **For stronger funnel conclusions, query user-level stage membership.**
   A follow-up analysis should use a consistent period and user key, with
   privacy-appropriate handling, and ideally time-ordered events per user.
5. **Add comparable time and segment fields to future query outputs** if
   business stakeholders need date-filtered funnel results, device or channel
   comparisons, or product analysis.

## Power BI preparation and limitations

Power BI-ready aggregate tables are prepared in `data/processed/`. The daily
activity table supports date and event slicing. Event summary counts are for
the full seven-day period, while funnel counts and rates have no date key and
remain full-period KPIs. Consult `docs/powerbi_data_dictionary.md` and
`docs/powerbi_implementation_guide.md` before building the report in Power BI
Desktop.

The supplied files do not support:

- A distinct count of users across all event types.
- Individual journey paths, sequence, time-to-convert, or cohort retention.
- Reliable device, traffic-source, geography, or product segmentation.
- Explaining why a user did not proceed to the next funnel stage.
- Proving causation or evaluating changes over longer-term trends.

The sample covers only seven dates in these exported results. Do not interpret
the percentages as current or broadly representative ecommerce benchmarks.

The project workspace did not contain the original BigQuery SQL. The SQL files
under `sql/` are reconstructed query definitions based on the saved result
schemas and period; compare them with BigQuery query history before presenting
them as the exact source queries.
