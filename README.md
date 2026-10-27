# Day 53 — Model Serving & Guardrails

This project explores serving a fine-tuned ClimateTech LLM and adding basic safety checks around model inputs and outputs.

## What's included

- `guardrails.py` — PII redaction, prompt-injection checks, and toxicity checks.
- `guardrail_traces.jsonl` — traces from the CPU guardrail benchmark.
- `guardrail_benchmark_summary.json` — summary of the mock-generator benchmark.
- `hf_benchmark_summary.json` — Hugging Face model benchmark results.
- `hf_benchmark_requests.csv` — requests used for the Hugging Face benchmark.

## Guardrails

The pipeline checks inputs and outputs, redacts detected PII, blocks suspicious input prompts, and withholds outputs flagged by the implemented checks.

These checks use basic regex and keyword patterns. They are a learning implementation, not production-grade security classifiers.

## Benchmark status

The CPU benchmark measures guardrail overhead with a mock generator; it does not measure LLM inference performance.

The Hugging Face benchmark records the baseline model-serving measurements. The vLLM comparison is pending GPU availability.

## Limitations

- Pattern-based checks can miss attacks or incorrectly flag harmless text.
- CPU mock-generator measurements are not comparable to real model-serving latency.
- vLLM throughput and p95 latency have not yet been benchmarked.
