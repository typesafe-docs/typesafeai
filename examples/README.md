# Examples

Runnable, type-checked examples for the TypeSafe System One API. **Every example runs end to end in CI** against an offline mock of the API, so you can try them with no API key.

## Run them

```bash
# Option A: offline, no key needed (fake answers)
pip install -r python/requirements.txt
./run_all.sh

# Option B: the real API
export TYPESAFE_API_KEY="..."   # https://console.typesafe.ai/keys
USE_REAL_API=1 ./run_all.sh

# A single example
python python/quickstart.py
cd typescript && npm install && npx tsx quickstart.ts
```

> 🧪 [`mock/mock_server.py`](mock/mock_server.py) checks the basic request shape and returns well-formed fake answers: Choice picks the first option, Score picks the middle level, and Noul returns 0.9. Point any SDK at it with `TYPESAFE_BASE_URL=http://127.0.0.1:8765`. It's for wiring tests only. The answers mean nothing.

## cURL

| Example | What it shows |
|---|---|
| [`curl/quickstart.sh`](curl/quickstart.sh) | A raw HTTP request mixing Choice, Score, and Noul |
| [`curl/list_models.sh`](curl/list_models.sh) | `GET /v1/models` |

## Python

| Example | What it shows | Docs |
|---|---|---|
| [`quickstart.py`](python/quickstart.py) | SDK basics with all three question types | [Quick start](../docs/02-quickstart.md) |
| [`http_no_sdk.py`](python/http_no_sdk.py) | Plain `requests` with retries and backoff | [API reference](../docs/09-api-reference.md) |
| [`typed_response.py`](python/typed_response.py) | `response_model=` with pydantic, plus error handling | [Python SDK](../docs/10-sdk-python.md) |
| [`async_batch.py`](python/async_batch.py) | Async client, a concurrency cap, and a Noul review band | [Noul](../docs/04-primitives/noul.md) |
| [`ticket_triage.py`](python/ticket_triage.py) | Speculative fan-out plus confidence-gated routing | [Patterns](../docs/07-patterns.md) |
| [`composite_scoring.py`](python/composite_scoring.py) | Ranking resumes for two roles with weights in code | [Composite scoring](../docs/07-patterns.md#composite-scoring) |
| [`spam_decomposition.py`](python/spam_decomposition.py) | Six atomic phishing signals with a weighted risk score | [How to build](../docs/06-building-with-typesafe.md) |
| [`tool_trace_verification.py`](python/tool_trace_verification.py) | Nine checks on an agent's tool-call trace | [How to build](../docs/06-building-with-typesafe.md) |
| [`llm_guardrails.py`](python/llm_guardrails.py) | Hazard Nouls plus a severity Score: pass, review, block, or support | [Guardrails cookbook](../docs/cookbooks/llm_guardrails.md) |
| [`rag_passage_gate.py`](python/rag_passage_gate.py) | Gating retrieved passages, including prompt-injection detection | [RAG cookbook](../docs/cookbooks/classifying_rag_passages.md) |
| [`citation_check.py`](python/citation_check.py) | Quote check in code, then a supports/contradicts/says-nothing Choice | [Citations cookbook](../docs/cookbooks/citation_check.md) |
| [`rerank.py`](python/rerank.py) | One Noul per (query, candidate), sorted by probability | [Re-ranking cookbook](../docs/cookbooks/rerank_typesafe.md) |
| [`pre_parsed_extraction.py`](python/pre_parsed_extraction.py) | Regex finds candidates and TypeSafe picks one | [Extraction cookbook](../docs/cookbooks/pre_parsed_value_extraction_cookbook.md) |
| [`date_extraction.py`](python/date_extraction.py) | Date parts as Choices, with the date math in code | [Date cookbook](../docs/cookbooks/date_extraction_cookbook.md) |

## TypeScript

| Example | What it shows |
|---|---|
| [`quickstart.ts`](typescript/quickstart.ts) | The JS SDK with answer types inferred from questions |
| [`routing.ts`](typescript/routing.ts) | Intent routing with confidence gates and typed errors |
| [`fanout.ts`](typescript/fanout.ts) | Speculative fan-out with an exhaustive `switch` |
| [`spam.ts`](typescript/spam.ts) | Decomposed phishing signals with typed weights |
