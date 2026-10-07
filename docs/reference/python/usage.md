# Usage

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/usage>


> Guides and patterns for working with the TypeSafe Python SDK.

<a id="usage"></a>

<a id="calling-the-system-one-api"></a>

## Calling the System One API

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            "I was charged twice. Please help ASAP.",
            {
                "billing": Noul(instructions="Is this about billing?"),
                "tone": Choice(
                    instructions="What is the tone?",
                    criteria={"calm": None, "angry": None},
                ),
                "urgency": Score(
                    instructions="How urgent is this?",
                    criteria=["low", "medium", "high"],
                ),
            },
        )
        print(
            result.nouls["billing"].noul,
            result.choices["tone"].choice,
            result.scores["urgency"].score,
        )

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()
state = "I was charged twice. Please help ASAP."
questions = {
    "billing": Noul(instructions="Is this about billing?"),
    "tone": Choice(
        instructions="What is the tone?", criteria={"calm": None, "angry": None}
    ),
    "urgency": Score(
        instructions="How urgent is this?", criteria=["low", "medium", "high"]
    ),
}
result = client.system_one(state, questions)
print(
    result.nouls["billing"].noul,
    result.choices["tone"].choice,
    result.scores["urgency"].score,
)
```

<a id="typed-system_one-responses"></a>

## Typed system_one responses

It is possible to provide a response model to `system_one` to make using the response more *type-safe*:

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer, SystemOneResponse

class BillingResponse(SystemOneResponse):
    billing: NoulAnswer

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
            response_model=BillingResponse,
        )
        assert 0 <= result.billing.noul <= 1
        assert result.billing == result.nouls["billing"]
        print(result.request_id)

asyncio.run(main())
```

**Sync**

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

<a id="custom-response-types"></a>

### Custom response types

It is also possible to define a completely new response model without inheriting from `SystemOneResponse`:

**Async**

```python
import asyncio

from pydantic import BaseModel

from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer

class BillingAnswers(BaseModel):
    billing: NoulAnswer

class BillingResponse(BaseModel):
    answers: BillingAnswers

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
            response_model=BillingResponse,
        )
        assert 0 <= result.answers.billing.noul <= 1

asyncio.run(main())
```

**Sync**

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

<a id="choosing-a-model"></a>

## Choosing a model

Inspect the available models:

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        print(await client.models.list())

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import TypeSafeClient

print(TypeSafeClient().models.list())
```

Select the model when constructing a client:

**Async**

```python
client = AsyncTypeSafeClient(model="jev")
```

**Sync**

```python
client = TypeSafeClient(model="jev")
```

See the [Models resource reference](sync-client.md#models-resource) for details.

<a id="configuring-the-base-url"></a>

## Configuring the base URL

In order to use the SDK with a different API url, set `base_url` on the client or the `TYPESAFE_BASE_URL` environment variable. This requires the alternative API to follow the [TypeSafe OpenAPI spec](https://api.typesafe.ai/docs/).

For example, connect through an AI gateway using its API key and model ID.

**OpenRouter**

Use an OpenRouter API key and an [OpenRouter model ID](https://openrouter.ai/~typesafe/jev-latest/):

**Async client**

```python
import asyncio
import os

from typesafe_sdk import AsyncTypeSafeClient, Noul

async def main() -> None:
    async with AsyncTypeSafeClient(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api",
        model="~typesafe/jev-latest",
    ) as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
        )
        print(result.nouls["billing"].noul)

asyncio.run(main())
```

**Sync client**

```python
import os

from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
    model="~typesafe/jev-latest",
) as client:
    result = client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="Is this about billing?")},
    )
    print(result.nouls["billing"].noul)
```

**Vercel AI Gateway**

[Vercel's TypeSafe-compatible API](https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe) can be used with the SDK:

**Async client**

```python
import asyncio
import os

from typesafe_sdk import AsyncTypeSafeClient, Noul

async def main() -> None:
    async with AsyncTypeSafeClient(
        api_key=os.environ["AI_GATEWAY_API_KEY"],
        base_url="https://ai-gateway.vercel.sh/typesafe",
        model="typesafe-ai/jev",
    ) as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
        )
        print(result.nouls["billing"].noul)

asyncio.run(main())
```

**Sync client**

```python
import os

from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient(
    api_key=os.environ["AI_GATEWAY_API_KEY"],
    base_url="https://ai-gateway.vercel.sh/typesafe",
    model="typesafe-ai/jev",
) as client:
    result = client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="Is this about billing?")},
    )
    print(result.nouls["billing"].noul)
```

**Pydantic AI Gateway**

Use a [Pydantic AI Gateway API key](https://pydantic.dev/articles/jev-pydantic-ai-gateway):

**Async client**

```python
import asyncio
import os

from typesafe_sdk import AsyncTypeSafeClient, Noul

async def main() -> None:
    async with AsyncTypeSafeClient(
        api_key=os.environ["PYDANTIC_AI_GATEWAY_API_KEY"],
        base_url="https://gateway-us.pydantic.dev/proxy/typesafe",
        model="jev-latest",
    ) as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
        )
        print(result.nouls["billing"].noul)

asyncio.run(main())
```

**Sync client**

```python
import os

from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient(
    api_key=os.environ["PYDANTIC_AI_GATEWAY_API_KEY"],
    base_url="https://gateway-us.pydantic.dev/proxy/typesafe",
    model="jev-latest",
) as client:
    result = client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="Is this about billing?")},
    )
    print(result.nouls["billing"].noul)
```

<a id="http2"></a>

## `HTTP/2`

> 💡 **Tip**
>
> **Tip**
>
> It is often beneficial to enable HTTP/2 when sending many concurrent requests, because it allows multiple requests to be multiplexed over a single connection. The `'typesafe-sdk[http2]'` extra provides a convenient way to install the required dependencies. See the [`httpx2` HTTP/2 guide](https://pydantic.dev/docs/httpx2/guides/http2/) for details.

**Async**

```python
import httpx2

from typesafe_sdk import AsyncTypeSafeClient

client = AsyncTypeSafeClient(http_client=httpx2.AsyncClient(http2=True))
```

**Sync**

```python
import httpx2

from typesafe_sdk import TypeSafeClient

client = TypeSafeClient(http_client=httpx2.Client(http2=True))
```

<a id="retries"></a>

## `Retries`

Pass a custom [`RetryPolicy`](retries.md) as `retry` on the client or per call. Invalid API keys raise `TypeSafeError` during client creation, before any request or retry.

On the client:

**Async**

```python
from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy

client = AsyncTypeSafeClient(
    retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0)
)
```

**Sync**

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

client = TypeSafeClient(retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0))
```

Per call:

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        await client.system_one(
            state,
            questions,
            retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0),
        )

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import RetryPolicy

client.system_one(
    state, questions, retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0)
)
```

<a id="error-handling"></a>

## Error handling

Handle [exceptions](exceptions.md) raised by the SDK:

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, TypeSafeAPIError

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        try:
            await client.system_one(state, questions)
        except TypeSafeAPIError as error:
            print(error.status, error.request_id)

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import TypeSafeAPIError

try:
    client.system_one(state, questions)
except TypeSafeAPIError as error:
    print(error.status, error.request_id)
```

<a id="logging"></a>

## `Logging`

The SDK logs to the `typesafe_sdk` logger. Configure it according to [standard logging](https://docs.python.org/3/library/logging.html) guide:

```python
import logging

logging.getLogger("typesafe_sdk").setLevel(logging.DEBUG)
```

Or set `TYPESAFE_LOG_LEVEL` to one of `debug`, `info`, `warning`, `error`, or `off` before importing the SDK.

`info` logs one summary line per request; `debug` also logs request and response headers and bodies. Secret headers — authorization, API keys, cookies, and any header whose name contains `token` or `secret` — are redacted from log output. Request and response bodies are **not** redacted.

<a id="environment-variables"></a>

## Environment variables

The SDK reads and uses the following environment variables:

| Variable | Configures | Default |
| - | - | - |
| `TYPESAFE_API_KEY` | API key (required) | — |
| `TYPESAFE_BASE_URL` | API root URL | `https://api.typesafe.ai` |
| `TYPESAFE_DEFAULT_MODEL` | Default model | `jev-latest` |
| `TYPESAFE_LOG_LEVEL` | `typesafe_sdk` logger level, applied once at import | unset |

See the [constants reference](constants.md) for SDK defaults.

API keys supplied through `api_key` or `TYPESAFE_API_KEY` have leading and trailing whitespace stripped, including newlines from key files. Empty keys, internal whitespace, control characters, and non-ASCII characters are rejected before sending a request. An explicitly empty key does not fall back to the environment.

<a id="forward-compatibility"></a>

## Forward compatibility

The SDK keeps working as the TypeSafe API evolves, so you can adopt new API features before an SDK release adds first-class support for them.

<a id="extra-request-fields"></a>

### Extra request fields

Send additional API request fields with [`extra_body`](sync-client.md). The `beam_width` field below is illustrative; only send fields supported by the API.

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Noul

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="About billing?")},
            extra_body={"beam_width": 4},
        )

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient() as client:
    client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="About billing?")},
        extra_body={"beam_width": 4},
    )
```

<a id="raw-question-dictionaries"></a>

### Raw question dictionaries

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        await client.system_one(
            "I was charged twice.",
            {
                "billing": {
                    "type": "noul",
                    "instructions": "About billing?",
                    "weight": 2,
                }
            },
        )

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import TypeSafeClient

with TypeSafeClient() as client:
    client.system_one(
        "I was charged twice.",
        {"billing": {"type": "noul", "instructions": "About billing?", "weight": 2}},
    )
```

> 💡 **Tip**
>
> **Tip**
>
> Unknown fields are a forward-compatibility escape hatch. Ignore their type-checking errors and prefer upgrading the SDK instead.

<a id="unknown-answer-kinds"></a>

### Unknown answer kinds

The SDK logs a warning and skips unrecognized answer kinds. Use `raw_http_response` to inspect the complete API response, including those answers:

**Async**

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Noul

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            "I was charged twice.",
            {"billing": Noul(instructions="Is this about billing?")},
        )
        print(result.raw_http_response.json()["answers"])

asyncio.run(main())
```

**Sync**

```python
from typesafe_sdk import Noul, TypeSafeClient

result = TypeSafeClient().system_one(
    "I was charged twice.",
    {"billing": Noul(instructions="Is this about billing?")},
)
raw_answers = result.raw_http_response.json()["answers"]
```

<a id="unknown-response-fields"></a>

### Unknown response fields

Unknown extra fields on recognized responses are ignored.
