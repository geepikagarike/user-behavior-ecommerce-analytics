# Python EDA Documentation

## Entry point

The complete Python analysis is in `src/analysis/eda_analysis.py`. It uses
Pandas and NumPy for loading, validation, calculations, and derived tables;
Matplotlib and Seaborn create the four static exploratory charts.

The script identifies the four BigQuery result CSVs in `data/raw/` by their
column schemas, not by their generated filenames. It expects daily activity,
event summary, funnel counts, and funnel counts with rates.

## Analysis steps

1. Load and identify all four CSVs.
2. Parse daily `event_date` values and validate required rows, missing values,
   numeric types and ranges, duplicate keys, and event-name values.
3. Reconcile daily event totals with the overall event summary.
4. Check that the two funnel exports agree, compare funnel counts to the
   matching event-specific user counts, and recalculate the reported rates.
5. Create the quality report and Power BI-ready aggregate tables.
6. For a full run, generate event distribution, daily activity, aggregate
   funnel, and conversion-rate visualizations and refresh the EDA report.

## Run from the project root

PowerShell:

```powershell
python -m pip install -r requirements.txt
python src\analysis\eda_analysis.py --prepare-only
```

`--prepare-only` validates the raw exports and rewrites
`reports/data_quality_report.md` and the three CSV files in
`data/processed/`. It does not refresh the EDA charts or
`reports/eda_business_insights.md`.

To run the complete analysis and regenerate the charts and EDA report:

```powershell
python src\analysis\eda_analysis.py
```

The full run also refreshes the quality report and processed CSVs. Neither
command writes to `data/raw/`. Outputs are intentionally regenerated from the
current input exports.

## Generated files

- `reports/data_quality_report.md`
- `reports/eda_business_insights.md` (full run only)
- `data/processed/daily_activity.csv`
- `data/processed/event_summary.csv`
- `data/processed/funnel_stages.csv`
- `outputs/visualizations/event_distribution.png` (full run only)
- `outputs/visualizations/daily_user_activity.png` (full run only)
- `outputs/visualizations/ecommerce_conversion_funnel.png` (full run only)
- `outputs/visualizations/conversion_rates.png` (full run only)

The funnel chart displays aggregate counts and ratios, not individual user
paths. Its rate annotation is placed in the title area so it does not overlap
the largest stage's count label.

## Tests

Run the standard-library unit tests from the project root:

```powershell
python -m unittest discover -s tests -v
```
