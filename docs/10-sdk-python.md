# 10. Python SDK

[← Back to README](../README.md) · 📚 **[Full generated API reference](reference/python/README.md)** · Sources: <https://docs.typesafe.ai/sdk/python> · <https://docs.typesafe.ai/sdk/python/usage> · GitHub: <https://github.com/typesafe-ai/typesafe-sdk-python>

Synchronous and asynchronous clients with typed questions and answers, plus automatic retries. Requires Python 3.10 or later.

## Install

```bash
pip install typesafe-sdk
# or
uv add typesafe-sdk
# with HTTP/2 support
pip install 'typesafe-sdk[http2]'
```

```bash
export TYPESAFE_API_KEY="..."   # create one at https://console.typesafe.ai/
```

## Calling System One

### Sync

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this ticket about billing?"),
            "tone": Choice(
                instructions="What is the customer's tone?",
                criteria={"calm": None, "frustrated": None, "angry": None},
            ),
            "urgency": Score(
                instructions="How urgent is this ticket?",
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

print(response.nouls["billing"].noul)
print(response.choices["tone"].choice)
print(response.scores["urgency"].score)
```

### Async

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score


async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state={"document": "I was charged twice. Please fix this ASAP."},
            questions={
                "billing": Noul(instructions="Is this ticket about billing?"),
                "tone": Choice(
                    instructions="What is the customer's tone?",
                    criteria={"calm": None, "frustrated": None, "angry": None},
                ),
                "urgency": Score(
                    instructions="How urgent is this ticket?",
                    criteria=["can wait", "this week", "today"],
                ),
            },
        )

    print(response.nouls["billing"].noul)
    print(response.choices["tone"].choice)
    print(response.scores["urgency"].score)


asyncio.run(main())
```

### Positional arguments

`state` and `questions` can also be passed positionally:

```python
result = client.system_one(
    "I was charged twice. Please help ASAP.",
    {"billing": Noul(instructions="Is this about billing?")},
)
```

### Concurrency with the async client

```python
import asyncio
from typesafe_sdk import AsyncTypeSafeClient, Noul

QUESTIONS = {"billing": Noul(instructions="Is this about billing?")}


async def classify_all(tickets: list[str]) -> list[float]:
    async with AsyncTypeSafeClient() as client:
        sem = asyncio.Semaphore(16)

        async def one(t: str) -> float:
            async with sem:
                r = await client.system_one(t, QUESTIONS)
                return r.nouls["billing"].noul

        return await asyncio.gather(*(one(t) for t in tickets))
```

## Question types

```python
from typesafe_sdk import Choice, Noul, NoulCriteria, Score

Noul(instructions="Is the customer asking for a human agent?")

Noul(
    instructions="Has the customer contacted support about this before?",
    criteria=NoulCriteria(
        true="Mentions a prior attempt, ticket, or that they have asked before",
        false="No sign of any previous contact",
    ),
)

Choice(
    instructions="Which team should handle this?",
    criteria={"returns": "Exchanges, wrong or damaged items", "shipping": None},
)

Score(
    instructions="How severe is the reported issue?",
    criteria=["Cosmetic", "Degraded with workaround", "Blocking"],  # ordered sequence (since v0.6.0)
)
```

`instructions` and every criteria value accept a `str`, a mapping, a sequence, or `None` (JSON content).

### Raw question dictionaries

```python
client.system_one(
    "I was charged twice.",
    {"billing": {"type": "noul", "instructions": "About billing?"}},
)
```

## Reading answers

| Accessor | Type |
|---|---|
| `response.answers[id]` | `NoulAnswer \| ChoiceAnswer \| ScoreAnswer` |
| `response.nouls[id].noul` | `float` |
| `response.choices[id].choice` / `.probabilities` / `.confidence` | `str` / `dict[str, float]` / `float` |
| `response.scores[id].score` / `.probabilities` / `.legend` / `.confidence` | `float` / `dict[int, float]` / `dict[int, ...]` / `float` |
| `response.model` | Versioned model ID, for example `jev-1.13.0` |
| `response.usage.input_tokens` / `.output_tokens` | `int` |
| `response.request_id` | The `x-typesafe-request-id` header |
| `response.raw_http_response` | The underlying HTTP response |

> 💡 **Use the typed accessors.** `response.answers[id]` is typed as the union `NoulAnswer | ChoiceAnswer | ScoreAnswer`, so `response.answers["x"].noul` fails a strict type check under mypy or pyright. `response.nouls`, `response.choices`, and `response.scores` are each narrowed to one answer type:
>
> ```python
> r = client.system_one(state, questions)
> r.nouls["is_urgent"].noul          # NoulAnswer
> r.choices["department"].confidence # ChoiceAnswer
> r.scores["severity"].score         # ScoreAnswer
> ```
>
> Annotate question maps as `dict[str, Question]` (`from typesafe_sdk import Question`) so a mixed dict type-checks. For full attribute-style typing, use `response_model=` (below).

Dispatching on answer type:

```python
from typesafe_sdk import ChoiceAnswer, NoulAnswer, ScoreAnswer

for key, answer in response.answers.items():
    if isinstance(answer, NoulAnswer):
        print(key, answer.noul)
    elif isinstance(answer, ChoiceAnswer):
        print(key, answer.choice, answer.confidence)
    elif isinstance(answer, ScoreAnswer):
        print(key, answer.score, answer.legend)
```

## Typed `system_one` responses (pydantic)

Pass `response_model=` to get attribute access with full type checking (v0.7.0 and later):

```python
from typesafe_sdk import Noul, NoulAnswer, SystemOneResponse, TypeSafeClient


class BillingResponse(SystemOneResponse):
    billing: NoulAnswer


with TypeSafeClient() as client:
    result = client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="Is this about billing?")},
        response_model=BillingResponse,
    )
    assert 0 <= result.billing.noul <= 1
    assert result.billing == result.nouls["billing"]
    print(result.request_id)
```

A fully custom model, without inheriting from `SystemOneResponse`:

```python
from pydantic import BaseModel

from typesafe_sdk import Noul, NoulAnswer, TypeSafeClient


class BillingAnswers(BaseModel):
    billing: NoulAnswer


class BillingResponse(BaseModel):
    answers: BillingAnswers


result = TypeSafeClient().system_one(
    "I was charged twice.",
    {"billing": Noul(instructions="Is this about billing?")},
    response_model=BillingResponse,
)
assert 0 <= result.answers.billing.noul <= 1
```

## Choosing a model

```python
from typesafe_sdk import TypeSafeClient

with TypeSafeClient() as client:
    for model in client.models.list().models:
        print(model.name, model.release_date, model.description)

client = TypeSafeClient(model="jev-1.13.0")        # pin a version on the client
client.system_one(state, questions, model="jev-latest")  # or per call
```

## Configuration

| Constructor arg | Env var | Default |
|---|---|---|
| `api_key` | `TYPESAFE_API_KEY` | *(required)* |
| `base_url` | `TYPESAFE_BASE_URL` | `https://api.typesafe.ai` |
| `model` | `TYPESAFE_DEFAULT_MODEL` | `jev-latest` |
| `timeout` | — | `10.0` seconds per HTTP operation |
| `retry` | — | `RetryPolicy()` |
| `http_client` | — | an `httpx2` client |
| — | `TYPESAFE_LOG_LEVEL` | unset (`debug`/`info`/`warning`/`error`/`off`) |

Leading and trailing whitespace is stripped from API keys. Empty keys and keys with internal whitespace, control characters, or non-ASCII characters are rejected **before** any request is sent. An explicitly empty key doesn't fall back to the environment variable.

```python
from typesafe_sdk.constants import (
    API_KEY_ENV, BASE_URL_ENV, DEFAULT_MODEL_ENV, LOG_LEVEL_ENV,
    DEFAULT_BASE_URL, DEFAULT_MODEL, DEFAULT_TIMEOUT,
)
```

## AI gateways (custom `base_url`)

Any API that follows the TypeSafe OpenAPI spec works.

### OpenRouter

```python
import os
from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
    model="~typesafe/jev-latest",
) as client:
    result = client.system_one("I was charged twice.", {"billing": Noul(instructions="Is this about billing?")})
    print(result.nouls["billing"].noul)
```

### Vercel AI Gateway

```python
with TypeSafeClient(
    api_key=os.environ["AI_GATEWAY_API_KEY"],
    base_url="https://ai-gateway.vercel.sh/typesafe",
    model="typesafe-ai/jev",
) as client:
    ...
```

### Pydantic AI Gateway

```python
with TypeSafeClient(
    api_key=os.environ["PYDANTIC_AI_GATEWAY_API_KEY"],
    base_url="https://gateway-us.pydantic.dev/proxy/typesafe",
    model="jev-latest",
) as client:
    ...
```

## HTTP/2

HTTP/2 helps when you send many concurrent requests over one connection.

```python
import httpx2
from typesafe_sdk import AsyncTypeSafeClient, TypeSafeClient

client = TypeSafeClient(http_client=httpx2.Client(http2=True))
aclient = AsyncTypeSafeClient(http_client=httpx2.AsyncClient(http2=True))
```

## Retries

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

# On the client
client = TypeSafeClient(retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0))

# Per call
client.system_one(state, questions, retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0))

# Custom statuses
client = TypeSafeClient(
    retry=RetryPolicy(max_retries=3, timeout=10.0, http_statuses={429, 500, 502, 503, 504})
)
```

`RetryPolicy` fields:

| Field | Meaning |
|---|---|
| `max_retries` | Retries after the first attempt. `0` disables retries. |
| `backoff_initial` | First delay in seconds, doubled each attempt up to `backoff_max`. |
| `backoff_max` | Maximum delay in seconds. |
| `backoff_jitter` | Fraction (0–1) of each delay randomly subtracted. |
| `http_statuses` | HTTP status codes to retry. |
| `respect_retry_after` | Honor `Retry-After` / `retry-after-ms`. |
| `api_connection_error` | Retry connection failures. |
| `api_timeout_error` | Retry timeouts. |
| `exceptions` | Extra exception types that trigger a retry. |
| `predicate` | `callable(exc) -> bool`. Returning `True` triggers a retry. |
| `timeout` | **Total** retry budget per call in seconds, including delays. `None` means no limit. |

```python
RetryPolicy(
    max_retries=5,
    backoff_initial=1.0,
    backoff_max=20.0,
    predicate=lambda exc: "temporarily" in str(exc),
)
```

## Error handling

```python
from typesafe_sdk import (
    TypeSafeError,                        # base
    TypeSafeAPIError,                     # HTTP error: .status .body .headers .endpoint .request_id
    TypeSafeBadRequestError,              # 400
    TypeSafeAuthenticationError,          # 401
    TypeSafePermissionDeniedError,        # 403
    TypeSafeNotFoundError,                # 404
    TypeSafeUnprocessableEntityError,     # 422
    TypeSafeRateLimitError,               # 429  (.retry_after_ms)
    TypeSafeInternalServerError,          # 5xx
    TypeSafeAPIConnectionError,           # no HTTP response
    TypeSafeAPITimeoutError,              # timeout (.timeout)
    TypeSafeAPIResponseValidationError,   # 2xx with an invalid body (.field_path)
)

try:
    client.system_one(state, questions)
except TypeSafeRateLimitError as e:
    print("slow down; server asked for", e.retry_after_ms, "ms")
except TypeSafeUnprocessableEntityError as e:
    print("bad question:", e.body)
except TypeSafeAPIError as e:
    print(e.status, e.request_id)
except TypeSafeAPIConnectionError:
    print("network problem")
```

Exceptions and responses can be pickled (v0.6.0 and later).

## Logging

```python
import logging

logging.getLogger("typesafe_sdk").setLevel(logging.DEBUG)
```

Or set `TYPESAFE_LOG_LEVEL=debug` before importing. `info` logs one line per request. `debug` adds headers and bodies. Secret headers are redacted, but **bodies are not**.

## Forward compatibility

```python
# Send API fields the SDK doesn't model yet (beam_width is illustrative)
client.system_one("I was charged twice.", {"billing": Noul(instructions="About billing?")},
                  extra_body={"beam_width": 4})

# Unknown answer kinds are skipped with a warning, so inspect the raw JSON:
result = client.system_one("I was charged twice.", {"billing": Noul(instructions="Is this about billing?")})
raw_answers = result.raw_http_response.json()["answers"]
```

## Changelog highlights

| Version | Date | Change |
|---|---|---|
| v0.7.2 | 2026-09-26 | `http2` extra |
| v0.7.1 | 2026-09-21 | API key validated early and kept out of logged exceptions; gateway examples |
| v0.7.0 | 2026-09-18 | **Breaking:** msgspec → pydantic. New `response_model=`. Fix for serializing `str` subclasses. |
| v0.6.0 | 2026-09-15 | **Breaking:** `Score.criteria` is now an ordered sequence. Accepts `Mapping` and `Sequence`. Picklable errors. |
| v0.5.7 | 2026-09-14 | Initial public release |

---

[← 9. HTTP API](09-api-reference.md) · Next: [11. JavaScript SDK →](11-sdk-javascript.md)
