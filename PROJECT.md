# Day 53 – LLMOps: Serving, Observability & CI/CD

## Project Overview

This project extends the ClimateTech sustainability assessment application with LLMOps practices covering API serving, monitoring, performance testing, evaluation validation, and continuous integration.

The objective is to move beyond fine-tuning a language model and establish a repeatable workflow for validating, serving, and monitoring an AI application.

**Model:** Qwen2.5-1.5B-Instruct
**Fine-tuning:** LoRA
**Adapter:** `final_adapter/`
**Evaluation dataset:** 100 examples
**API framework:** FastAPI
**Monitoring:** Prometheus and Grafana
**Load testing:** Locust
**CI:** GitHub Actions

## 1. Serving and API

Implemented a FastAPI application with:

- `/health` – application health check.
- `/demo/assessment` – serves a saved fine-tuned model prediction.
- `/metrics` – exposes Prometheus metrics.
- Request ID generation and response headers.
- Request processing time measurement.
- Structured request logging.
- JSON schema validation of the assessment response.

**Current limitation:** The API currently serves saved evaluation predictions. It is not yet connected to live inference using the fine-tuned model. Therefore, this is a serving and monitoring prototype, not a live model inference deployment.

## 2. Monitoring and Observability

### Implemented

- Prometheus metrics collection.
- HTTP request count.
- HTTP request duration.
- Grafana dashboard for API monitoring.
- Request ID correlation through middleware.
- Request latency and HTTP status logging.
- Locust-based load testing.

### Dashboard metrics

- Total HTTP requests.
- Request rate.
- Average latency.
- p95 latency.
- HTTP response status distribution.
- Error rate.

### Performance testing

A Locust test was conducted with 10 concurrent users for approximately two minutes.

| Metric | Result |
|---|---:|
| Total requests | 549 |
| Failed requests | 0 |
| Average response time | 52 ms |
| Median response time | 14 ms |
| p95 latency | 33 ms |
| p98 latency | 75 ms |
| p99 latency | 2,100 ms |
| Throughput | 4.78 requests/sec |

The p99 latency spike requires further investigation. These results measure the current API prototype and must not be interpreted as fine-tuned model inference performance.

## 3. CI for LLM Applications

Implemented a GitHub Actions workflow that runs on:

- Push events.
- Pull requests.
- Manual workflow dispatch.

### Automated quality gates

1. Assessment schema validation.
2. Evaluation baseline validation.
3. Automated test suite.
4. Ruff code quality checks.

### Evaluation results

The deterministic evaluation report contains 100 examples.

| Metric | Result |
|---|---:|
| Valid JSON | 100% |
| Schema compliance | 100% |
| Exact match | 95% |
| Industry agreement | 95% |
| SDG agreement | 97% |
| Evidence agreement | 97% |

These are agreement metrics against reference outputs, not independent verification of factual correctness.

### Local validation

- Assessment schema validation: 100/100 passed.
- Baseline validation: passed.
- Unit tests: 20/20 passed.
- Ruff: passed.

**CI limitation:** The current baseline validator checks the saved evaluation report against predefined expected values. It does not rerun model inference or compare freshly generated predictions against a previous model version.

## 4. Work Not Yet Completed

Some planned LLMOps capabilities remain incomplete.

| Planned capability | Current status |
|---|---|
| Live fine-tuned model inference through FastAPI | Pending |
| Full distributed request tracing with OpenTelemetry | Pending |
| Token usage and model inference cost tracking | Pending |
| Model cost dashboard | Pending |
| Automated alerting | Pending |
| Model card and deployment documentation | To be completed |
| Dynamic model regression comparison | Pending |
| Deliberately bad PR to demonstrate CI rejection | Not yet demonstrated |

### Why some work was deferred

The development environment is a Lenovo laptop with 8 GB RAM and an NVIDIA GTX 1650. The local PyTorch installation is CPU-only, and available system memory was insufficient for reliable local inference with the 1.5B base model.

To avoid unstable experiments and misleading performance measurements, live inference integration and model-dependent observability were deferred.

The current work focuses on API infrastructure, saved-prediction validation, monitoring, performance testing, and CI quality gates. Live model integration can be completed using a better-provisioned GPU environment, such as Google Colab or a suitable remote machine.

## 5. Important Distinction

This project demonstrates the infrastructure and quality-control foundations of an LLM application. It does not claim production-ready model serving, distributed tracing, token-level cost monitoring, or automated model deployment.

The next iteration will connect the fine-tuned adapter to live inference, add model-level telemetry, and introduce genuine regression testing across model versions.

## 6. Project Outcome

Day 53 established a foundation for operating an AI application beyond model training:

- API serving structure.
- Schema-based output validation.
- Prometheus and Grafana monitoring.
- Load testing and latency analysis.
- Deterministic evaluation checks.
- Automated CI quality gates.

The remaining work is documented explicitly so that future improvements can be measured against a clear baseline.