
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "evaluation" / "final_deterministic_evaluation_report.json"


class TestBaselineEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not REPORT_PATH.exists():
            raise FileNotFoundError(
                f"Evaluation report not found: {REPORT_PATH}"
            )

        with REPORT_PATH.open("r", encoding="utf-8") as file:
            cls.report = json.load(file)

    def test_report_has_100_test_examples(self):
        self.assertEqual(self.report["test_examples"], 100)

    def test_fine_tuned_model_valid_json_is_100_percent(self):
        metric = self.report["fine_tuned_model"]["valid_json"]
        self.assertEqual(metric["rate_percent"], 100.0)

    def test_fine_tuned_model_schema_compliance_is_100_percent(self):
        metric = self.report["fine_tuned_model"]["schema_compliant"]
        self.assertEqual(metric["rate_percent"], 100.0)

    def test_fine_tuned_model_exact_match_is_95_percent(self):
        metric = self.report["fine_tuned_model"]["exact_match"]
        self.assertEqual(metric["rate_percent"], 95.0)

    def test_report_documents_no_llm_as_judge(self):
        methodology = self.report["methodology"]
        self.assertEqual(methodology["llm_as_judge"], "Not used.")


if __name__ == "__main__":
    unittest.main()
