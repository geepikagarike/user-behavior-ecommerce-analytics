# Project Roadmap and Status

This roadmap reflects what is in the workspace now. The final interactive
dashboard is a separate Power BI Desktop task owned by the project owner. No
Streamlit or other dashboard application is part of the deliverable.

## Phase 1 — Project setup: complete

- Created an analytics-focused project structure and documented its purpose,
  tools, and workflow.

## Phase 2 — Dataset selection: complete

- Selected Google's public, obfuscated GA4 ecommerce sample in BigQuery.
- The saved result exports cover 2020-11-01 through 2020-11-07.
- The sample is obfuscated and may contain placeholders; findings describe
  only this sample and not current store performance.

## Phase 3 — BigQuery access and exports: complete for this analysis

- Four aggregate BigQuery result CSVs are preserved in `data/raw/`.
- The exports contain event counts, event-specific user counts, and aggregate
  funnel counts/rates. They contain no individual-user rows.

## Phase 4 — SQL analysis: exported results available; source SQL not verified

- The SQL folder contains named, commented query definitions for daily
  activity, event summaries, funnel stage counts, conversion rates, and
  reconciliation checks.
- These queries are reconstructed from the result schemas, observed outputs,
  and seven-day period because the original SQL was not saved in this
  workspace.
- Compare the reconstructed definitions with BigQuery query history before
  presenting them as the original source queries. No SQL has been run from
  this project workspace.
- Query purpose, output grain, and interpretation notes are documented in
  `docs/sql_analysis.md`.

## Phase 5 — Python EDA and data quality: complete

- `src/analysis/eda_analysis.py` validates input schemas, missing values,
  types, duplicates, count/rate consistency, and event-total reconciliation.
- The reusable workflow and its generated outputs are documented in
  `docs/python_eda.md`; metric definitions and quality rules are in
  `docs/methodology.md`.
- The script can write a data quality report and Power BI-ready aggregate CSV
  tables without refreshing existing charts using `--prepare-only`.
- Full EDA can be rerun with `python src\analysis\eda_analysis.py`.
- Original CSVs in `data/raw/` remain unchanged.

## Phase 6 — Business insights and Power BI preparation: complete

- KPI calculations and business observations are documented separately from
  recommendations in `reports/business_insights_kpi_dashboard.md`.
- The data dictionary and Power BI modeling, DAX, and visualization guide are
  in `docs/`.
- Prepared CSVs are written to `data/processed/`.
- Limitations are explicit: no all-event distinct-user count, user-level
  journeys, retention, or funnel date slicing can be derived from the current
  aggregate exports.

## Phase 7 — Final Power BI dashboard: pending

- The project owner will build the interactive report in Power BI Desktop.
- Import the three files in `data/processed/` and follow
  `docs/powerbi_data_dictionary.md` and
  `docs/powerbi_implementation_guide.md`.
- Validate dashboard totals and measures against the CSV exports and this
  project's documented KPIs.
- The funnel exports have no date key, so funnel KPIs remain full-period.

## Verified findings

- **Total events:** 35,434 across the seven exported dates; daily and overall
  event totals reconcile.
- **Product-view users:** 4,937; **checkout users:** 832; **purchase users:**
  224.
- **View-to-checkout conversion:** 16.85%; **checkout-to-purchase conversion:**
  26.92%; **view-to-purchase conversion:** 4.54%.
- **Aggregate view-to-purchase count drop-off:** 95.46%. This is a count
  comparison, not verified individual abandonment.
- **Review item:** the event summary has 4 `add_to_cart` events from 1
  event-specific user, much lower than checkout and purchase counts. Verify
  SQL filters and event tracking before interpreting the funnel.

## Final handoff checklist

- [ ] Compare reconstructed SQL with the original BigQuery query history.
- [ ] Run `python src\analysis\eda_analysis.py --prepare-only` after any raw
  input change and review the data quality report.
- [x] Document project methodology, SQL query intent, Python EDA, and source
  and processed data columns.
- [x] Run the project unit tests and the full analysis pipeline.
- [ ] Build and validate the Power BI report separately in Power BI Desktop.
- [ ] Label aggregate limitations and distinguish findings from
  recommendations in the final presentation.
