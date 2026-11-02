import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from src.serving.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_assessment_endpoint():
    response = client.get("/demo/assessment")

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "saved_prediction_demo"
    assert isinstance(data["request_id"], str)
    assert data["request_id"]
    assert isinstance(data["assessment"], dict)
    assert isinstance(data["latency_ms"], (int, float))


def test_request_id_matches_response_header():
    response = client.get("/demo/assessment")

    assert response.status_code == 200
    assert response.json()["request_id"] == response.headers["X-Request-ID"]

from unittest.mock import patch


def test_demo_assessment_rejects_invalid_schema():
    with patch(
        "src.serving.app.load_saved_assessment",
        return_value={"unexpected_field": "invalid"},
    ):
        response = client.get("/demo/assessment")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Unable to load or validate the saved demo assessment."
    )
    assert response.json()["request_id"] == response.headers["X-Request-ID"]

def test_demo_assessment_matches_json_schema():
    project_root = Path(__file__).resolve().parents[1]
    schema_path = (
        project_root
        / "src"
        / "evaluation"
        / "assessment.schema.json"
    )

    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    response = client.get("/demo/assessment")

    assert response.status_code == 200

    assessment = response.json()["assessment"]
    errors = list(
        Draft202012Validator(schema).iter_errors(assessment)
    )

    assert errors == []


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert "text/plain" in response.headers["content-type"]


from src.serving.app import HTTP_REQUESTS


def test_metrics_endpoint_does_not_increment_application_counter():
    before = HTTP_REQUESTS.labels(
        method="GET",
        endpoint="/metrics",
        status="200",
    )._value.get()

    response = client.get("/metrics")

    after = HTTP_REQUESTS.labels(
        method="GET",
        endpoint="/metrics",
        status="200",
    )._value.get()

    assert response.status_code == 200
    assert after == before
