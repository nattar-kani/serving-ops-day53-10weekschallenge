import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jsonschema import Draft202012Validator, ValidationError
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel
from starlette.responses import Response

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

PREDICTIONS_PATH = (
    PROJECT_ROOT / "evaluation" / "fine_tuned_predictions.jsonl"
)

ASSESSMENT_SCHEMA_PATH = (
    PROJECT_ROOT / "src" / "evaluation" / "assessment.schema.json"
)

with ASSESSMENT_SCHEMA_PATH.open("r", encoding="utf-8") as file:
    assessment_schema = json.load(file)

assessment_validator = Draft202012Validator(assessment_schema)

app = FastAPI(
    title="ClimateTech Assessment API",
    description=(
        "Demo serving API using a saved model assessment. "
        "This endpoint does not run live model inference."
    ),
    version="0.1.0",
)


class AssessmentResponse(BaseModel):
    request_id: str
    mode: str
    assessment: dict[str, Any]
    latency_ms: float


def load_saved_assessment() -> dict[str, Any]:
    """Load one saved prediction for the demo endpoint."""
    with PREDICTIONS_PATH.open("r", encoding="utf-8") as file:
        first_row = file.readline()

    if not first_row.strip():
        raise ValueError("Prediction dataset is empty.")

    import json

    row = json.loads(first_row)
    prediction = row.get("prediction")

    if not isinstance(prediction, str):
        raise TypeError("Saved prediction must be a JSON string.")

    assessment = json.loads(prediction)

    if not isinstance(assessment, dict):
        raise TypeError("Saved assessment must be a JSON object.")

    return assessment


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = (time.perf_counter() - start_time) * 1000

    if request.url.path != "/metrics":
        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=request.url.path,
            status=str(response.status_code),
        ).inc()

        HTTP_REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(latency_ms / 1000)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = f"{latency_ms:.2f}"

    logger.info(
        "HTTP request completed method=%s path=%s status=%d "
        "request_id=%s latency_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
        latency_ms,
    )

    return response


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

@app.get("/demo/assessment", response_model=AssessmentResponse)
def demo_assessment(request: Request):
    start_time = time.perf_counter()
    request_id = request.state.request_id

    try:
        assessment = load_saved_assessment()
        assessment_validator.validate(assessment)
    except (
    OSError,
    ValueError,
    KeyError,
    TypeError,
    ValidationError,
) as error:
        logger.exception(
            "Demo assessment loading or validation failed: %s",
            type(error).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Unable to load or validate the saved demo assessment.",
                "request_id": request_id,
            },
        )

    latency_ms = (time.perf_counter() - start_time) * 1000

    return AssessmentResponse(
        request_id=request_id,
        mode="saved_prediction_demo",
        assessment=assessment,
        latency_ms=round(latency_ms, 2),
    )