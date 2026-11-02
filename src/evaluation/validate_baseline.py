
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    REPO_ROOT
    / "evaluation"
    / "final_deterministic_evaluation_report.json"
)

EXPECTED_TEST_EXAMPLES = 100

# Approved results from the selected deterministic report.
REQUIRED_METRICS = {
    "valid_json": 100.0,
    "schema_compliant": 100.0,
    "exact_match": 95.0,
    "industry_agreement": 95.0,
    "sdg_agreement": 97.0,
    "evidence_agreement": 97.0,
}


def validate_baseline() -> bool:
    """Validate the structure and approved metrics of the baseline report."""

    if not REPORT_PATH.is_file():
        print(f"FAIL: Report not found: {REPORT_PATH}")
        return False

    try:
        with REPORT_PATH.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"FAIL: Could not read report: {exc}")
        return False

    errors = []

    if report.get("evaluation_type") != "deterministic":
        errors.append("evaluation_type must be 'deterministic'")

    if report.get("test_examples") != EXPECTED_TEST_EXAMPLES:
        errors.append(
            f"Expected {EXPECTED_TEST_EXAMPLES} test examples; "
            f"found {report.get('test_examples')}"
        )

    model_results = report.get("fine_tuned_model")

    if not isinstance(model_results, dict):
        errors.append("fine_tuned_model must be a JSON object")
    else:
        for metric, expected_rate in REQUIRED_METRICS.items():
            result = model_results.get(metric)

            if not isinstance(result, dict):
                errors.append(f"Missing metric object: {metric}")
                continue

            count = result.get("count")
            total = result.get("total")
            rate = result.get("rate_percent")

            if not all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in (count, total, rate)
            ):
                errors.append(f"{metric}: count, total and rate must be numeric")
                continue

            if total != EXPECTED_TEST_EXAMPLES:
                errors.append(
                    f"{metric}: expected total {EXPECTED_TEST_EXAMPLES}; "
                    f"found {total}"
                )

            if not 0 <= count <= total:
                errors.append(f"{metric}: count must be between 0 and total")
                continue

            calculated_rate = count / total * 100

            if abs(rate - calculated_rate) > 0.01:
                errors.append(
                    f"{metric}: reported rate {rate}% does not match "
                    f"count-derived rate {calculated_rate:.2f}%"
                )

            if rate != expected_rate:
                errors.append(
                    f"{metric}: expected approved rate {expected_rate}%; "
                    f"found {rate}%"
                )

    if errors:
        print("BASELINE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return False

    print("BASELINE VALIDATION PASSED")
    print(f"Report: {REPORT_PATH.name}")
    print(f"Test examples: {EXPECTED_TEST_EXAMPLES}")

    for metric, expected_rate in REQUIRED_METRICS.items():
        print(f"{metric}: {expected_rate:.1f}%")

    return True


if __name__ == "__main__":
    sys.exit(0 if validate_baseline() else 1)
