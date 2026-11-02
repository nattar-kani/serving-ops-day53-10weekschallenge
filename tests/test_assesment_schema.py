import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "evaluation"
    / "assessment.schema.json"
)


def load_validator():
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def valid_assessment():
    return {
        "industry": {
            "isic_code": "C2720",
            "isic_label": "Manufacture of batteries and accumulators",
            "classification_status": "broad_classification",
            "reason": "The described company manufactures batteries."
        },
        "sdg_assessment": [
            {
                "sdg_number": 7,
                "relationship": "potential_contribution",
                "rationale": "The product may support clean energy.",
                "supporting_evidence": None
            }
        ],
        "evidence_assessment": {
            "level": "E1",
            "source_type": "company_claim",
            "impact_claim": "The company claims an environmental benefit.",
            "supporting_evidence": None,
            "limitations": ["The claim has not been independently verified."]
        }
    }


class TestAssessmentSchema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_valid_assessment_passes(self):
        self.assertEqual(
            list(self.validator.iter_errors(valid_assessment())),
            []
        )

    def test_missing_industry_fails(self):
        assessment = valid_assessment()
        del assessment["industry"]

        self.assertTrue(
            list(self.validator.iter_errors(assessment))
        )

    def test_invalid_sdg_number_fails(self):
        assessment = valid_assessment()
        assessment["sdg_assessment"][0]["sdg_number"] = 18

        self.assertTrue(
            list(self.validator.iter_errors(assessment))
        )

    def test_invalid_evidence_level_fails(self):
        assessment = valid_assessment()
        assessment["evidence_assessment"]["level"] = "E9"

        self.assertTrue(
            list(self.validator.iter_errors(assessment))
        )

    def test_unexpected_top_level_field_fails(self):
        assessment = valid_assessment()
        assessment["unexpected_field"] = "not allowed"

        self.assertTrue(
            list(self.validator.iter_errors(assessment))
        )


if __name__ == "__main__":
    unittest.main()