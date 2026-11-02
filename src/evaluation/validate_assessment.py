import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

SCHEMA_PATH = Path(__file__).with_name("assessment.schema.json")
PREDICTIONS_PATH = (
    PROJECT_ROOT / "evaluation" / "fine_tuned_predictions.jsonl"
)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)
    return schema


def validate_prediction_json(
    prediction: str,
    validator: Draft202012Validator,
) -> list[str]:
    try:
        assessment = json.loads(prediction)
    except json.JSONDecodeError as error:
        return [f"Invalid JSON: {error.msg}"]

    if not isinstance(assessment, dict):
        return ["Top-level JSON value must be an object."]

    errors = sorted(
        validator.iter_errors(assessment),
        key=lambda error: list(map(str, error.absolute_path)),
    )

    return [
        f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: "
        f"{error.message}"
        for error in errors
    ]


def main() -> int:
    validator = Draft202012Validator(load_schema())
    total = 0
    passed = 0
    failures = []
    logger.info("Starting assessment schema validation")

    with PREDICTIONS_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            total += 1

            try:
                row = json.loads(line)
                prediction = row["prediction"]

                if not isinstance(prediction, str):
                    errors = ["The prediction field must be a JSON string."]
                else:
                    errors = validate_prediction_json(prediction, validator)

            except (json.JSONDecodeError, KeyError, TypeError) as error:
                errors = [f"Invalid prediction record: {error}"]

            if errors:
                failures.append((line_number, errors))
            else:
                passed += 1

    logger.info(
        "Assessment validation completed: total=%d passed=%d failed=%d",
        total,
        passed,
        len(failures)
    )

    print("ASSESSMENT SCHEMA VALIDATION")
    print(f"Total records: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failures)}")

    for line_number, errors in failures[:10]:
        print(f"\nRecord {line_number}:")
        for error in errors:
            logger.warning(
                    "Schema validation failed for record %d: %s",
                    line_number,
                    "; ".join(errors),
                )
            print(f"  - {error}")

    if len(failures) > 10:
        print(f"\n... and {len(failures) - 10} more failing records.")

    if failures:
        print("\nVALIDATION FAILED")
        return 1

    
    
    print("\nVALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())