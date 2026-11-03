"""Exploratory analysis for the exported, aggregated GA4 query results."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
VISUALIZATIONS_DIR = PROJECT_ROOT / "outputs" / "visualizations"
REPORT_PATH = PROJECT_ROOT / "reports" / "eda_business_insights.md"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

EXPECTED_SCHEMAS = {
    "daily_activity": frozenset(
        {"event_date", "event_name", "total_events", "unique_users"}
    ),
    "event_summary": frozenset({"event_name", "total_events", "unique_users"}),
    "funnel_counts": frozenset(
        {"product_view_users", "checkout_users", "purchase_users"}
    ),
    "funnel_rates": frozenset(
        {
            "product_view_users",
            "checkout_users",
            "purchase_users",
            "view_to_checkout_pct",
            "checkout_to_purchase_pct",
            "view_to_purchase_pct",
        }
    ),
}

CHART_NAMES = (
    "event_distribution.png",
    "daily_user_activity.png",
    "ecommerce_conversion_funnel.png",
    "conversion_rates.png",
)


def load_input_tables() -> dict[str, pd.DataFrame]:
    """Load each expected CSV by its columns, not by an assumed filename."""
    csv_paths = sorted(RAW_DATA_DIR.glob("*.csv"))
    if len(csv_paths) != len(EXPECTED_SCHEMAS):
        raise ValueError(
            f"Expected {len(EXPECTED_SCHEMAS)} CSV files in {RAW_DATA_DIR}, "
            f"but found {len(csv_paths)}."
        )

    tables: dict[str, pd.DataFrame] = {}
    for path in csv_paths:
        frame = pd.read_csv(path)
        columns = frozenset(frame.columns)
        matches = [
            table_name
            for table_name, schema in EXPECTED_SCHEMAS.items()
            if columns == schema
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Could not identify {path.name} by its columns. "
                f"Found columns: {list(frame.columns)}"
            )
        table_name = matches[0]
        if table_name in tables:
            raise ValueError(
                f"More than one CSV matches the {table_name} schema."
            )
        tables[table_name] = frame

    missing_tables = set(EXPECTED_SCHEMAS) - set(tables)
    if missing_tables:
        raise ValueError(f"Missing expected CSV schemas: {sorted(missing_tables)}")
    return tables


def validate_inputs(tables: dict[str, pd.DataFrame]) -> None:
    """Check completeness, types, key uniqueness, and aggregate consistency."""
    daily = tables["daily_activity"]
    event_summary = tables["event_summary"]
    funnel_counts = tables["funnel_counts"]
    funnel_rates = tables["funnel_rates"]

    for table_name, frame in tables.items():
        if frame.empty:
            raise ValueError(f"The {table_name} CSV contains no data rows.")
        if frame.isna().any().any():
            null_counts = frame.isna().sum()
            raise ValueError(
                f"The {table_name} CSV contains missing values: "
                f"{null_counts[null_counts > 0].to_dict()}"
            )

    daily["event_date"] = pd.to_datetime(
        daily["event_date"].astype(str), format="%Y%m%d", errors="raise"
    )
    for frame in (daily, event_summary):
        for column in ("total_events", "unique_users"):
            frame[column] = pd.to_numeric(frame[column], errors="raise")
            if not np.isfinite(frame[column]).all():
                raise ValueError(f"{column} contains a non-finite value.")
            if (frame[column] % 1 != 0).any():
                raise ValueError(f"{column} contains a non-integer value.")
            if (frame[column] < 0).any():
                raise ValueError(f"{column} contains negative values.")
        if (frame["unique_users"] > frame["total_events"]).any():
            raise ValueError("A user count exceeds its corresponding event count.")
        if frame["event_name"].astype(str).str.strip().eq("").any():
            raise ValueError("An event name is empty.")

    if daily.duplicated(["event_date", "event_name"]).any():
        raise ValueError("Daily activity contains duplicate date/event rows.")
    if event_summary["event_name"].duplicated().any():
        raise ValueError("Event summary contains duplicate event names.")

    count_columns = ("product_view_users", "checkout_users", "purchase_users")
    for frame in (funnel_counts, funnel_rates):
        for column in count_columns:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
            if not np.isfinite(frame[column]).all():
                raise ValueError(f"{column} contains a non-finite value.")
            if (frame[column] % 1 != 0).any():
                raise ValueError(f"{column} contains a non-integer value.")
            if (frame[column] < 0).any():
                raise ValueError(f"{column} contains negative values.")
    for column in (
        "view_to_checkout_pct",
        "checkout_to_purchase_pct",
        "view_to_purchase_pct",
    ):
        funnel_rates[column] = pd.to_numeric(funnel_rates[column], errors="raise")
        if not np.isfinite(funnel_rates[column]).all():
            raise ValueError(f"{column} contains a non-finite value.")
        if not funnel_rates[column].between(0, 100).all():
            raise ValueError(f"{column} must be between 0 and 100.")

    if len(funnel_counts) != 1 or len(funnel_rates) != 1:
        raise ValueError("Each funnel CSV is expected to contain exactly one row.")
    if not funnel_counts.loc[0, list(count_columns)].equals(
        funnel_rates.loc[0, list(count_columns)]
    ):
        raise ValueError("The two funnel CSVs contain different user counts.")

    daily_event_totals = daily.groupby("event_name")["total_events"].sum()
    summary_event_totals = event_summary.set_index("event_name")["total_events"]
    if set(daily_event_totals.index) != set(summary_event_totals.index):
        raise ValueError("Daily and overall event summaries have different event names.")
    if not np.array_equal(
        daily_event_totals.sort_index().to_numpy(),
        summary_event_totals.sort_index().to_numpy(),
    ):
        raise ValueError(
            "Daily event totals do not reconcile with the event-summary totals."
        )


def build_data_quality_report(tables: dict[str, pd.DataFrame]) -> str:
    """Create a fact-based quality report for the validated CSV inputs."""
    daily = tables["daily_activity"]
    event_summary = tables["event_summary"]
    funnel_counts = tables["funnel_counts"].iloc[0]
    funnel_rates = tables["funnel_rates"].iloc[0]

    daily_event_totals = daily.groupby("event_name")["total_events"].sum()
    summary_event_totals = event_summary.set_index("event_name")["total_events"]
    reconciliation_ok = daily_event_totals.sort_index().equals(
        summary_event_totals.sort_index()
    )
    funnel_counts_match = all(
        int(funnel_counts[column]) == int(funnel_rates[column])
        for column in ("product_view_users", "checkout_users", "purchase_users")
    )
    event_users = event_summary.set_index("event_name")["unique_users"]
    funnel_event_names = {
        "product_view_users": "view_item",
        "checkout_users": "begin_checkout",
        "purchase_users": "purchase",
    }
    funnel_event_users_match = all(
        event_name in event_users.index
        and int(funnel_counts[funnel_column]) == int(event_users[event_name])
        for funnel_column, event_name in funnel_event_names.items()
    )
    date_event_duplicates = int(daily.duplicated(["event_date", "event_name"]).sum())
    event_name_duplicates = int(event_summary["event_name"].duplicated().sum())
    missing_values = {
        name: int(frame.isna().sum().sum()) for name, frame in tables.items()
    }

    rows = []
    for name, frame in tables.items():
        rows.append(
            f"| {name} | {len(frame)} | "
            f"{', '.join(f'{column}: {dtype}' for column, dtype in frame.dtypes.items())} | "
            f"{missing_values[name]} | PASS |"
        )

    checks = [
        ("Expected four distinct schemas", "PASS", "All four expected CSV schemas were identified."),
        ("Required values are present", "PASS", "No missing values were found in any input table."),
        ("Numeric metrics are valid", "PASS", "Counts and rates are finite, non-negative, and in range."),
        (
            "Daily date/event keys are unique",
            "PASS" if date_event_duplicates == 0 else "FAIL",
            f"{date_event_duplicates} duplicate date/event keys.",
        ),
        (
            "Overall event names are unique",
            "PASS" if event_name_duplicates == 0 else "FAIL",
            f"{event_name_duplicates} duplicate event names.",
        ),
        (
            "Daily and overall event counts reconcile",
            "PASS" if reconciliation_ok else "FAIL",
            f"Daily event total: {int(daily['total_events'].sum()):,}; "
            f"overall summary total: {int(event_summary['total_events'].sum()):,}.",
        ),
        (
            "Funnel count exports agree",
            "PASS" if funnel_counts_match else "FAIL",
            "The count-only and count-plus-rate exports were compared.",
        ),
        (
            "Funnel exports have the expected row grain",
            "PASS",
            "Each funnel export contains exactly one aggregate row.",
        ),
        (
            "Funnel users match event-specific summary",
            "PASS" if funnel_event_users_match else "REVIEW",
            "Funnel stage counts were compared to the corresponding event-specific user counts.",
        ),
    ]

    expected_rates = calculate_conversion_rates(funnel_counts)
    rates_match = all(
        np.isclose(
            float(funnel_rates[column]),
            expected_rates[rate_name],
            atol=0.01,
        )
        for column, rate_name in (
            ("view_to_checkout_pct", "View to checkout"),
            ("checkout_to_purchase_pct", "Checkout to purchase"),
            ("view_to_purchase_pct", "View to purchase"),
        )
    )
    checks.append(
        (
            "Exported conversion rates match counts",
            "PASS" if rates_match else "FAIL",
            "Recalculated percentages agree within 0.01 percentage points."
            if rates_match
            else "At least one exported rate differs from the rate recalculated from counts.",
        )
    )

    add_to_cart = event_summary.loc[event_summary["event_name"] == "add_to_cart"]
    add_to_cart_note = (
        f"The export contains {int(add_to_cart.iloc[0]['total_events']):,} "
        f"add_to_cart events and {int(add_to_cart.iloc[0]['unique_users']):,} "
        f"event-specific {'user' if int(add_to_cart.iloc[0]['unique_users']) == 1 else 'users'}. "
        "This is a review item because it is much lower "
        "than checkout/purchase counts; it does not by itself prove a tracking error."
        if not add_to_cart.empty
        else "No add_to_cart row appears in the event summary; review the query scope."
    )

    check_lines = "\n".join(
        f"| {name} | {status} | {details} |" for name, status, details in checks
    )
    return f"""# Data Quality Report

## Input inventory

| Input table | Rows | Columns | Missing values | Schema validation |
| --- | ---: | --- | ---: | --- |
{chr(10).join(rows)}

## Validation checks

| Check | Result | Evidence |
| --- | --- | --- |
{check_lines}

## Scope and reconciliation

- Daily activity contains {len(daily)} rows across
  {daily['event_date'].nunique()} dates, from {daily['event_date'].min():%Y-%m-%d}
  through {daily['event_date'].max():%Y-%m-%d}.
- Daily and overall event totals {'reconcile' if reconciliation_ok else 'do not reconcile'}:
  {int(daily['total_events'].sum()):,} daily events versus
  {int(event_summary['total_events'].sum()):,} overall events.
- The two funnel exports {'agree' if funnel_counts_match else 'do not agree'} on
  stage counts. Exported rates {'match' if rates_match else 'do not match'} the
  rates recalculated from those counts.
- Funnel stage counts {'match' if funnel_event_users_match else 'do not fully match'} the corresponding
  event-specific user counts in the overall event summary.

## Review notes and limitations

- {add_to_cart_note}
- Daily `unique_users` is a daily, event-specific count. It must not be summed
  across dates or event types to represent distinct users across the period.
- No individual-user records are present, so this report cannot validate user
  paths or confirm stage-to-stage membership.
- The original BigQuery SQL files were not present in the workspace. The
  checks compare saved exports; they cannot establish the exact source query
  definitions.

This report is generated from the current CSV exports. Raw files are read-only
inputs to the analysis and are not rewritten.
"""


def build_processed_tables(
    tables: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Build Power BI tables from the saved exports without inferring users."""
    daily = tables["daily_activity"].copy()
    daily["event_date"] = daily["event_date"].dt.strftime("%Y-%m-%d")
    for column in ("total_events", "unique_users"):
        daily[column] = daily[column].astype("int64")

    event_summary = tables["event_summary"].copy()
    for column in ("total_events", "unique_users"):
        event_summary[column] = event_summary[column].astype("int64")
    event_summary = event_summary.sort_values("event_name").reset_index(drop=True)

    funnel = tables["funnel_counts"].iloc[0]
    rates = calculate_conversion_rates(funnel)
    stage_values = [
        ("Product view", int(funnel["product_view_users"]), None, None),
        (
            "Checkout",
            int(funnel["checkout_users"]),
            int(funnel["product_view_users"]),
            rates["View to checkout"],
        ),
        (
            "Purchase",
            int(funnel["purchase_users"]),
            int(funnel["checkout_users"]),
            rates["Checkout to purchase"],
        ),
    ]
    funnel_stages = pd.DataFrame(
        [
            {
                "stage_order": order,
                "stage": stage,
                "users": users,
                "previous_stage_users": previous_users,
                "count_difference_from_previous": (
                    previous_users - users if previous_users is not None else pd.NA
                ),
                "conversion_from_previous_pct": rate,
                "conversion_from_product_view_pct": (
                    100.0 if order == 1 else rates[
                        "View to checkout" if order == 2 else "View to purchase"
                    ]
                ),
            }
            for order, (stage, users, previous_users, rate) in enumerate(
                stage_values, start=1
            )
        ]
    )
    funnel_stages = funnel_stages.astype(
        {
            "stage_order": "int64",
            "users": "int64",
            "previous_stage_users": "Int64",
            "count_difference_from_previous": "Int64",
        }
    )
    return {
        "daily_activity": daily.sort_values(["event_date", "event_name"]),
        "event_summary": event_summary,
        "funnel_stages": funnel_stages,
    }


def write_powerbi_tables(tables: dict[str, pd.DataFrame]) -> list[Path]:
    """Write derived Power BI CSVs; never write into the raw-data folder."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    processed_tables = build_processed_tables(tables)
    output_paths = []
    for table_name, frame in processed_tables.items():
        path = PROCESSED_DATA_DIR / f"{table_name}.csv"
        frame.to_csv(path, index=False, na_rep="")
        output_paths.append(path)
    return output_paths


def calculate_conversion_rates(funnel: pd.Series) -> dict[str, float]:
    """Calculate stage conversion rates from the supplied aggregate user counts."""
    views = float(funnel["product_view_users"])
    checkouts = float(funnel["checkout_users"])
    purchases = float(funnel["purchase_users"])
    if views <= 0 or checkouts <= 0:
        raise ValueError("Cannot calculate funnel rates with a zero denominator.")
    return {
        "View to checkout": checkouts / views * 100,
        "Checkout to purchase": purchases / checkouts * 100,
        "View to purchase": purchases / views * 100,
    }


def verify_reported_rates(
    funnel: pd.Series, calculated_rates: dict[str, float]
) -> None:
    reported = {
        "View to checkout": float(funnel["view_to_checkout_pct"]),
        "Checkout to purchase": float(funnel["checkout_to_purchase_pct"]),
        "View to purchase": float(funnel["view_to_purchase_pct"]),
    }
    for name, calculated in calculated_rates.items():
        if not np.isclose(reported[name], calculated, atol=0.01):
            raise ValueError(
                f"Reported {name.lower()} rate ({reported[name]:.2f}%) does not "
                f"match the rate calculated from the supplied user counts "
                f"({calculated:.2f}%)."
            )


def save_event_distribution(event_summary: pd.DataFrame, path: Path) -> None:
    ordered = event_summary.sort_values("total_events", ascending=True)
    figure, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.barplot(data=ordered, x="total_events", y="event_name", ax=axes[0], color="#4472C4")
    sns.barplot(data=ordered, x="unique_users", y="event_name", ax=axes[1], color="#70AD47")
    axes[0].set(title="Recorded events by type", xlabel="Event count", ylabel="")
    axes[1].set(title="Event-specific users by type", xlabel="User count", ylabel="")
    figure.suptitle("E-commerce event distribution")
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def save_daily_activity(daily: pd.DataFrame, path: Path) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    sns.lineplot(
        data=daily,
        x="event_date",
        y="total_events",
        hue="event_name",
        marker="o",
        ax=axes[0],
    )
    sns.lineplot(
        data=daily,
        x="event_date",
        y="unique_users",
        hue="event_name",
        marker="o",
        ax=axes[1],
    )
    axes[0].set(title="Daily event volume", xlabel="", ylabel="Events")
    axes[1].set(
        title="Daily event-specific user counts",
        xlabel="Event date",
        ylabel="Users for this event",
    )
    axes[1].tick_params(axis="x", rotation=30)
    figure.suptitle("Daily activity (user counts are not deduplicated across events)")
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def save_conversion_funnel(
    funnel: pd.Series, rates: dict[str, float], path: Path
) -> None:
    stages = pd.DataFrame(
        {
            "stage": ["Product view", "Checkout", "Purchase"],
            "users": [
                int(funnel["product_view_users"]),
                int(funnel["checkout_users"]),
                int(funnel["purchase_users"]),
            ],
        }
    )
    figure, axis = plt.subplots(figsize=(9, 5))
    sns.barplot(data=stages, x="stage", y="users", hue="stage", legend=False, ax=axis,
                palette=["#4472C4", "#ED7D31", "#70AD47"])
    for index, row in stages.iterrows():
        axis.text(index, row["users"], f" {row['users']:,}", ha="center", va="bottom")
    axis.set(
        xlabel="Reported stage",
        ylabel="User count",
    )
    axis.set_title(
        "Reported aggregate users by funnel stage\n"
        f"Aggregate ratios: view → checkout {rates['View to checkout']:.2f}%  |  "
        f"checkout → purchase {rates['Checkout to purchase']:.2f}%  |  "
        f"view → purchase {rates['View to purchase']:.2f}%",
        pad=12,
    )
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def save_conversion_rates(rates: dict[str, float], path: Path) -> None:
    rate_data = pd.DataFrame(
        {"stage": list(rates), "conversion_rate_pct": list(rates.values())}
    )
    figure, axis = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=rate_data,
        x="stage",
        y="conversion_rate_pct",
        hue="stage",
        legend=False,
        ax=axis,
        palette=["#4472C4", "#ED7D31", "#70AD47"],
    )
    axis.set(
        title="Conversion rates from supplied funnel counts",
        xlabel="Funnel transition",
        ylabel="Users continuing (%)",
        ylim=(0, 100),
    )
    axis.tick_params(axis="x", rotation=15)
    for index, value in enumerate(rate_data["conversion_rate_pct"]):
        axis.text(index, value, f" {value:.2f}%", ha="center", va="bottom")
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def build_business_report(
    daily: pd.DataFrame,
    event_summary: pd.DataFrame,
    funnel: pd.Series,
    rates: dict[str, float],
) -> str:
    daily_totals = daily.groupby("event_date")["total_events"].sum()
    peak_date = daily_totals.idxmax()
    peak_count = int(daily_totals.max())
    lowest_date = daily_totals.idxmin()
    lowest_count = int(daily_totals.min())
    average_daily_events = daily_totals.mean()
    total_events = int(event_summary["total_events"].sum())
    top_event = event_summary.loc[event_summary["total_events"].idxmax()]
    add_to_cart = event_summary.loc[event_summary["event_name"] == "add_to_cart"]
    add_to_cart_user_count = (
        int(add_to_cart.iloc[0]["unique_users"]) if not add_to_cart.empty else 0
    )
    add_to_cart_user_label = (
        "user" if add_to_cart_user_count == 1 else "users"
    )
    add_to_cart_note = (
        f"The event summary contains {int(add_to_cart.iloc[0]['total_events']):,} "
        f"`add_to_cart` events from "
        f"{add_to_cart_user_count:,} event-specific {add_to_cart_user_label}."
        if not add_to_cart.empty
        else "The event summary does not contain an `add_to_cart` row."
    )
    event_lines = "\n".join(
        f"- `{row.event_name}`: {int(row.total_events):,} events and "
        f"{int(row.total_events) / total_events:.2%} of recorded events; "
        f"{int(row.unique_users):,} event-specific "
        f"{'user' if int(row.unique_users) == 1 else 'users'}."
        for row in event_summary.sort_values("total_events", ascending=False).itertuples()
    )
    daily_user_lines = []
    for event_name, event_daily in daily.groupby("event_name", sort=True):
        lowest = event_daily.loc[event_daily["unique_users"].idxmin()]
        highest = event_daily.loc[event_daily["unique_users"].idxmax()]
        daily_user_lines.append(
            f"- `{event_name}` daily event-specific users ranged from "
            f"{int(lowest['unique_users']):,} on {lowest['event_date']:%Y-%m-%d} "
            f"to {int(highest['unique_users']):,} on "
            f"{highest['event_date']:%Y-%m-%d}."
        )
    daily_user_summary = "\n".join(daily_user_lines)
    return f"""# EDA Business Insights

## Dataset scope

- The inputs are four aggregate BigQuery query results; they do not contain individual-user records.
- Daily activity covers {daily['event_date'].min():%Y-%m-%d} through
  {daily['event_date'].max():%Y-%m-%d} ({daily['event_date'].nunique()} dates).
- The event summary contains {total_events:,} events in total. Its per-event
  event counts reconcile exactly with the daily activity export.
- Missing values, duplicate daily date/event keys, negative metrics, and
  mismatched funnel counts were checked by the EDA script.

## Findings supported by the exports

- The busiest date by recorded event count was {peak_date:%Y-%m-%d}, with
  {peak_count:,} events.
- Average daily event volume was {average_daily_events:,.0f}; the lowest
  daily total was {lowest_count:,} on {lowest_date:%Y-%m-%d}.
- The most frequent event was `{top_event['event_name']}` with
  {int(top_event['total_events']):,} events.
- `{top_event['event_name']}` represented
  {int(top_event['total_events']) / total_events:.2%} of recorded events.
- The supplied funnel counts were {int(funnel['product_view_users']):,} product-view
  users, {int(funnel['checkout_users']):,} checkout users, and
  {int(funnel['purchase_users']):,} purchase users.
- Rates recalculated from those counts are {rates['View to checkout']:.2f}% from
  view to checkout, {rates['Checkout to purchase']:.2f}% from checkout to
  purchase, and {rates['View to purchase']:.2f}% from view to purchase. These
  match the rounded rates in the export.

## Event summary

{event_lines}

## Daily event-specific user activity

{daily_user_summary}

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
- {add_to_cart_note} This is much smaller than the reported checkout and
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
"""


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate aggregate BigQuery CSV exports and prepare analysis outputs."
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help=(
            "Write the data quality report and Power BI CSV tables without "
            "regenerating the existing EDA report or charts."
        ),
    )
    args = parser.parse_args(argv)

    tables = load_input_tables()
    validate_inputs(tables)
    daily = tables["daily_activity"]
    event_summary = tables["event_summary"]
    funnel = tables["funnel_counts"].iloc[0]
    rates = calculate_conversion_rates(funnel)
    verify_reported_rates(tables["funnel_rates"].iloc[0], rates)

    QUALITY_REPORT_PATH.write_text(
        build_data_quality_report(tables),
        encoding="utf-8",
    )
    processed_paths = write_powerbi_tables(tables)

    if args.prepare_only:
        print(f"Validated {len(tables)} BigQuery result CSV files.")
        print(f"Data quality report: {QUALITY_REPORT_PATH}")
        print(f"Power BI-ready CSVs: {len(processed_paths)} files in {PROCESSED_DATA_DIR}")
        return

    sns.set_theme(style="whitegrid", palette="deep")
    VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)
    save_event_distribution(
        event_summary, VISUALIZATIONS_DIR / "event_distribution.png"
    )
    save_daily_activity(daily, VISUALIZATIONS_DIR / "daily_user_activity.png")
    save_conversion_funnel(
        funnel,
        rates,
        VISUALIZATIONS_DIR / "ecommerce_conversion_funnel.png",
    )
    save_conversion_rates(rates, VISUALIZATIONS_DIR / "conversion_rates.png")
    REPORT_PATH.write_text(
        build_business_report(daily, event_summary, funnel, rates),
        encoding="utf-8",
    )

    print(f"Analyzed {len(tables)} BigQuery result CSV files.")
    print(f"Total events: {int(event_summary['total_events'].sum()):,}")
    print(f"Daily activity dates: {daily['event_date'].nunique()}")
    print(f"Report: {REPORT_PATH}")
    print(f"Data quality report: {QUALITY_REPORT_PATH}")
    print(f"Power BI-ready CSVs: {len(processed_paths)} files in {PROCESSED_DATA_DIR}")
    print(f"Visualizations: {VISUALIZATIONS_DIR}")


if __name__ == "__main__":
    main()
