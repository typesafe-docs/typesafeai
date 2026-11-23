# 10. Python SDK

[← Back to README](../README.md) · 📚 **[Full generated API reference](reference/python/README.md)** · Sources: <https://docs.typesafe.ai/sdk/python> · <https://docs.typesafe.ai/sdk/python/usage/basic> · <https://docs.typesafe.ai/sdk/python/usage/advanced> · GitHub: <https://github.com/typesafe-ai/typesafe-sdk-python>

Synchronous and asynchronous clients with typed questions and answers, plus automatic retries. Requires Python 3.10 or later.

## Install

```bash
pip install typesafe-sdk
# or
uv add typesafe-sdk
# extras: HTTP/2, Pillow images, zstd compression on Python 3.13 and earlier
pip install 'typesafe-sdk[http2,pil,zstd]'
```

Request bodies of 1 KiB or more are compressed with zstd by default (since v0.7.5), when zstd is available: Python 3.14 has it built in; on older versions install the `zstd` extra, or bodies go uncompressed. A gateway or custom `base_url` that doesn't accept `Content-Encoding: zstd` needs `compression=False` on the client.

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

Box(instructions="the coffee mug in `photo`")  # needs Jev 1.14 and an image (since v0.7.5)
```

`instructions` and every criteria value accept a `str`, a mapping, a sequence, an `Image`, or `None`.

### Images

Images need the `TypeSafe-Danger-Zone-Images: true` header (see [Images](04-primitives/images.md) for limits and formats). Requests with images are sent as `multipart/form-data`, one part per image. There are three ways to place one:

```python
from pathlib import Path

from typesafe_sdk import Image, Noul, TypeSafeClient

client = TypeSafeClient(headers={"TypeSafe-Danger-Zone-Images": "true"})
returned, listing = Image(Path("returned.jpg")), Image(Path("listing.jpg"))

# 1. Directly in the content (state, instructions, or criteria)
client.system_one(
    ["The customer returned this item:", returned],
    {"same_item": Noul(instructions=["Is it the item in this listing photo?", listing])},
)

# 2. Inside text: the reference in an f-string is sent only within `attach_assets`
with client.attach_assets(returned):
    client.system_one(f"The customer says {returned} arrived scratched.", {"damaged": Noul(instructions="Is the item damaged?")})

# 3. Under a name you choose
client.system_one(
    "Inspect this returned product: <product>",
    {"damaged": Noul(instructions="Is the product damaged?")},
    assets={"<product>": returned},
)
```

Forgetting the `with client.attach_assets(...)` block is the common mistake: the reference is then sent as plain text, without the image.

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
| `response.answers[id]` | `NoulAnswer \| ChoiceAnswer \| ScoreAnswer \| BoxAnswer` |
| `response.nouls[id].noul` | `float` |
| `response.choices[id].choice` / `.probabilities` / `.confidence` | `str` / `dict[str, float]` / `float` |
| `response.scores[id].score` / `.probabilities` / `.legend` / `.confidence` | `float` / `dict[int, float]` / `dict[int, ...]` / `float` |
| `response.boxes[id].box` / `.confidence` | `BoxCoordinates` (`top`, `bottom`, `left`, `right`) / `float \| None` ([Box](04-primitives/box.md)) |
| `response.model` | Versioned model ID, for example `jev-1.14.0` |
| `response.usage.input_tokens` / `.output_tokens` | `int \| None` (counts are optional: "when reported by the API") |
| `response.request_id` | The `x-typesafe-request-id` header |
| `response.raw_http_response` | The underlying HTTP response |

> 💡 **Use the typed accessors.** `response.answers[id]` is typed as the union `NoulAnswer | ChoiceAnswer | ScoreAnswer | BoxAnswer`, so `response.answers["x"].noul` fails a strict type check under mypy or pyright. `response.nouls`, `response.choices`, `response.scores`, and `response.boxes` are each narrowed to one answer type:
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
from typesafe_sdk import BoxAnswer, ChoiceAnswer, NoulAnswer, ScoreAnswer

for key, answer in response.answers.items():
    if isinstance(answer, NoulAnswer):
        print(key, answer.noul)
    elif isinstance(answer, ChoiceAnswer):
        print(key, answer.choice, answer.confidence)
    elif isinstance(answer, ScoreAnswer):
        print(key, answer.score, answer.legend)
    elif isinstance(answer, BoxAnswer):
        print(key, answer.box, answer.confidence)
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

client = TypeSafeClient(model="jev-1.14.0")        # pin a version on the client
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
| `http_client` | — | an `httpx2` client (mutually exclusive with `transport`) |
| `headers` | — | none; for example `{"TypeSafe-Danger-Zone-Images": "true"}` |
| `compression` | — | `"zstd"` when available; `False` sends bodies uncompressed |
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

Keep the default HTTP/1.1 for high request rates. Use HTTP/2 for low to moderate concurrency when you want fewer connections, for example behind a proxy or firewall that limits them.

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

| Field | Default | Meaning |
|---|---|---|
| `max_retries` | `2` | Retries after the first attempt. `0` disables retries. |
| `backoff_initial` | `0.5` | First delay in seconds, doubled each attempt up to `backoff_max`. |
| `backoff_max` | `5.0` | Maximum delay in seconds. |
| `backoff_jitter` | `0.25` | Fraction (0–1) of each delay randomly subtracted. |
| `http_statuses` | `408`, `429`, `500–599` | HTTP status codes to retry. `529` falls inside `500–599`. |
| `respect_retry_after` | `True` | Honor `Retry-After` / `retry-after-ms`. |
| `api_connection_error` | `True` | Retry connection failures. |
| `api_timeout_error` | `True` | Retry timeouts. |
| `exceptions` | `set()` | Extra exception types that trigger a retry. |
| `predicate` | `None` | `callable(exc) -> bool`. Returning `True` triggers a retry. |
| `timeout` | `30.0` | **Total** retry budget per call in seconds, including delays. `None` means no limit. |

### Two different timeouts

| Setting | Default | Limits |
|---|---|---|
| `TypeSafeClient(timeout=...)` / `system_one(timeout=...)` | `10.0` s | **Each** HTTP attempt |
| `RetryPolicy(timeout=...)` | `30.0` s | The **whole** call: every attempt plus the delays between them |

With the defaults, a call makes at most 3 attempts (1 + `max_retries=2`), each limited to 10 s, and the SDK stops before any retry whose delay would reach or pass the 30 s budget. It then raises the last error.

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

# Interactive path: fail within ~3 s overall
fast = TypeSafeClient(timeout=2.0, retry=RetryPolicy(max_retries=1, timeout=3.0))

# Batch job: be patient with 429/529
patient = TypeSafeClient(timeout=15.0, retry=RetryPolicy(max_retries=6, backoff_max=20.0, timeout=120.0))
```

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

## Performance

From the official advanced usage guide:

- **Reuse clients.** One client keeps a connection pool (up to 100 connections, idle ones kept 30 s). A client per request pays a new TLS handshake every time.
- **Keep zstd available** (`typesafe-sdk[zstd]` on Python 3.13 and earlier); compression is on by default.
- **Async at high concurrency:** an aiohttp transport, `AsyncTypeSafeClient(http_client=Httpx2AiohttpClient())` from `httpx-aiohttp[httpx2]`.
- **Threads:** give each thread its own client.
- **Raise the connection limit** when you run more than 100 requests at once:

```python
import threading

import httpx2
from typesafe_sdk import AsyncTypeSafeClient, TypeSafeClient

limits = httpx2.Limits(max_connections=200, max_keepalive_connections=200, keepalive_expiry=30)
aclient = AsyncTypeSafeClient(http_client=httpx2.AsyncClient(limits=limits))


class ThreadClients(threading.local):
    def __init__(self) -> None:
        self.client = TypeSafeClient()


clients = ThreadClients()  # in any thread, `clients.client` is that thread's own client
```

## Changelog highlights

| Version | Date | Change |
|---|---|---|
| v0.7.5 | 2026-10-14 | [Images](04-primitives/images.md) (`Image` from a path, bytes, base64, or Pillow; `attach_assets`; named `assets=`), [`Box`](04-primitives/box.md) questions and `BoxAnswer`, zstd request compression on by default. Usage guide split into [basic](reference/python/usage-basic.md) and [advanced](reference/python/usage-advanced.md). |
| v0.7.4 | 2026-10-09 | Non-finite numbers (`NaN`, `Infinity`) are serialized as strings instead of invalid JSON tokens |
| v0.7.3 | 2026-10-09 | Fix async client crashes during concurrent TLS connections (`truststore<=0.10.4`); more request validation; pooled connections kept alive 30 s; new [Performance](reference/python/usage-advanced.md#performance) docs |
| v0.7.2 | 2026-09-26 | `http2` extra |
| v0.7.1 | 2026-09-21 | API key validated early and kept out of logged exceptions; gateway examples |
| v0.7.0 | 2026-09-18 | **Breaking:** msgspec → pydantic. New `response_model=`. Fix for serializing `str` subclasses. |
| v0.6.0 | 2026-09-15 | **Breaking:** `Score.criteria` is now an ordered sequence. Accepts `Mapping` and `Sequence`. Picklable errors. |
| v0.5.7 | 2026-09-14 | Initial public release |

---

[← 9. HTTP API](09-api-reference.md) · Next: [11. JavaScript SDK →](11-sdk-javascript.md)
