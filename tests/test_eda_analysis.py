"""Regression tests for the aggregate GA4 EDA pipeline."""

import unittest

import pandas as pd

from src.analysis import eda_analysis


class EDAAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tables = eda_analysis.load_input_tables()

    def test_source_exports_validate_and_reconcile(self) -> None:
        eda_analysis.validate_inputs(self.tables)
        daily = self.tables["daily_activity"]
        event_summary = self.tables["event_summary"]

        self.assertEqual(int(daily["total_events"].sum()), 35_434)
        self.assertEqual(
            daily.groupby("event_name")["total_events"].sum().to_dict(),
            event_summary.set_index("event_name")["total_events"].to_dict(),
        )

    def test_funnel_rates_match_reported_export(self) -> None:
        eda_analysis.validate_inputs(self.tables)
        funnel = self.tables["funnel_counts"].iloc[0]
        rates = eda_analysis.calculate_conversion_rates(funnel)

        self.assertAlmostEqual(rates["View to checkout"], 16.85, places=2)
        self.assertAlmostEqual(rates["Checkout to purchase"], 26.92, places=2)
        self.assertAlmostEqual(rates["View to purchase"], 4.54, places=2)
        eda_analysis.verify_reported_rates(
            self.tables["funnel_rates"].iloc[0], rates
        )

    def test_processed_tables_keep_aggregate_grains_and_metrics(self) -> None:
        eda_analysis.validate_inputs(self.tables)
        prepared = eda_analysis.build_processed_tables(self.tables)

        self.assertEqual(len(prepared["daily_activity"]), 22)
        self.assertEqual(len(prepared["event_summary"]), 4)
        self.assertEqual(prepared["funnel_stages"]["users"].tolist(), [4937, 832, 224])
        self.assertEqual(
            prepared["funnel_stages"]["count_difference_from_previous"].tolist(),
            [pd.NA, 4105, 608],
        )

    def test_validation_rejects_duplicate_daily_keys(self) -> None:
        daily = self.tables["daily_activity"]
        self.tables["daily_activity"] = pd.concat(
            [daily, daily.iloc[[0]]], ignore_index=True
        )

        with self.assertRaisesRegex(ValueError, "duplicate date/event"):
            eda_analysis.validate_inputs(self.tables)

    def test_quality_report_documents_reconciliation_and_limits(self) -> None:
        eda_analysis.validate_inputs(self.tables)
        report = eda_analysis.build_data_quality_report(self.tables)

        self.assertIn("Daily and overall event counts reconcile | PASS", report)
        self.assertIn("35,434 daily events", report)
        self.assertIn("No individual-user records are present", report)

    def test_business_report_includes_daily_event_specific_user_trends(self) -> None:
        eda_analysis.validate_inputs(self.tables)
        report = eda_analysis.build_business_report(
            self.tables["daily_activity"],
            self.tables["event_summary"],
            self.tables["funnel_counts"].iloc[0],
            eda_analysis.calculate_conversion_rates(
                self.tables["funnel_counts"].iloc[0]
            ),
        )

        self.assertIn("944 on 2020-11-03", report)
        self.assertIn("152 on 2020-11-06", report)
        self.assertIn("They overlap", report)


if __name__ == "__main__":
    unittest.main()
