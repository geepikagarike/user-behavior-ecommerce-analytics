# User Behavior Data Analytics

## Project overview

This project analyzes user activity in Google's public, obfuscated GA4
ecommerce sample. It uses saved BigQuery query results to explore event
activity and aggregate ecommerce conversion metrics, validate data quality,
document business observations, and prepare model-ready data for a Power BI
dashboard.

The project focuses on analytics rather than application development. The
final interactive dashboard will be built separately by the project owner in
Power BI Desktop. This project is not affiliated with Google and does not
contain private user data.

## Objectives

- Preserve original query-result CSVs and validate their schemas and metrics.
- Practice BigQuery SQL for daily activity, event summaries, funnel counts,
  rates, and reconciliation.
- Use Python, Pandas, and NumPy for reusable quality checks and analysis.
- Communicate evidence-based KPIs, observations, recommendations, and
  limitations.
- Prepare and document CSV tables and a data model for Power BI.

## Dataset and scope

The current inputs are four aggregate BigQuery result CSVs in `data/raw/`.
They cover 2020-11-01 through 2020-11-07 and do not contain individual-user
rows. A distinct all-event user total, user journeys, device/channel
segmentation, and user-level retention cannot be calculated from these
exports.

The original BigQuery SQL was not present in the workspace. The `.sql` files
in `sql/` are reconstructed, result-compatible query definitions based on the
saved outputs and date range. They are not confirmed copies of the original
queries and should be checked against BigQuery query history.

## Tools and methodology

- **BigQuery SQL:** source aggregation and validation query definitions.
- **Python, Pandas, NumPy:** schema/type validation, reconciliation, metric
  calculation, and Power BI table preparation.
- **Matplotlib and Seaborn:** exploratory charts saved in
  `outputs/visualizations/`.
- **Power BI Desktop:** final interactive dashboard, built separately by the
  project owner using the preparation guide.

Methodology preserves raw exports, checks event totals at daily and overall
grains, compares exported funnel counts and rates, and avoids interpreting
event-specific user counts as a distinct all-user total. The aggregate funnel
is treated as stage-count comparison, not proof of individual progression.
Detailed workflow and metric definitions are in
[`docs/methodology.md`](docs/methodology.md).

## Completed analysis and key findings

- **Total events:** 35,434 across the seven exported dates. Daily and overall
  event totals reconcile.
- **Product-view users:** 4,937; **checkout users:** 832; **purchase users:**
  224, as reported by the funnel query.
- **View-to-checkout rate:** 16.85%; **checkout-to-purchase rate:** 26.92%;
  **view-to-purchase rate:** 4.54%.
- **Aggregate count drop-off:** 95.46% between the reported product-view and
  purchase counts. This is not verified individual abandonment.
- **Data-quality review item:** the event summary contains 4 `add_to_cart`
  events from 1 event-specific user, far fewer than the checkout and purchase
  counts. Confirm event/query definitions before interpreting the stages.
- **All-event unique users:** unavailable from the aggregate exports.

The business report separates observed values from recommendations and
documents limitations. See `reports/business_insights_kpi_dashboard.md` and
`reports/data_quality_report.md`.

The five SQL files are reconstructed query definitions, not verified copies
of the original BigQuery SQL. Their purpose, output grain, and provenance are
documented in [`docs/sql_analysis.md`](docs/sql_analysis.md). The Python
workflow, generated outputs, and run commands are documented in
[`docs/python_eda.md`](docs/python_eda.md).

## Run the Python analysis

From the project root in PowerShell, create and activate a virtual environment
if desired, install dependencies, and prepare the Power BI tables and quality
report without rewriting the existing EDA charts or report:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\analysis\eda_analysis.py --prepare-only
```

To run the full EDA and refresh its charts and EDA report as well:

```powershell
python src\analysis\eda_analysis.py
```

The script reads from `data/raw/`, never writes to the raw inputs, and writes
derived Power BI tables to `data/processed/`. The command does not create or
run a dashboard application.

## Power BI handoff

The final dashboard is a separate manual Power BI Desktop task. Import the
three derived tables from `data/processed/`; use
`docs/powerbi_data_dictionary.md` and
`docs/powerbi_implementation_guide.md` for column meanings, relationships,
DAX measures, visuals, slicers, and page layout. Funnel KPIs are full-period
aggregates because the funnel source has no date column.

## Folder and file guide

| Path | Purpose |
| --- | --- |
| `data/raw/` | Original BigQuery result CSVs; do not edit these. |
| `data/processed/` | Derived, typed CSV tables prepared for Power BI. |
| `data/cleaned/` | Reserved for future cleaned source-level data. |
| `notebooks/` | Reserved for future interactive exploration notebooks. |
| `src/data_collection/` | Reserved for future data collection modules. |
| `src/data_cleaning/` | Reserved for future reusable cleaning modules. |
| `src/analysis/eda_analysis.py` | Validates exports, reports quality, prepares Power BI tables, and generates EDA outputs. |
| `sql/` | Reconstructed BigQuery analysis and reconciliation queries. |
| `powerbi/` | Reserved for Power BI Desktop project assets created separately. |
| `outputs/visualizations/` | Existing EDA charts. |
| `reports/` | EDA, data-quality, and business-insights reports. |
| `docs/` | Methodology, SQL/Python documentation, roadmap, data dictionary, and Power BI guide. |
| `requirements.txt` | Python packages used by the analytics workflow. |
| `.gitignore` | Excludes raw/local data and local environment files. |

## Project status

BigQuery result exports, Python EDA, initial business analysis, data-quality
checks, reconstructed SQL definitions, and Power BI data preparation are
documented in this project. The source SQL has not been recovered or verified
against BigQuery query history. **The Power BI dashboard has not been built;
it remains the final project stage.**
