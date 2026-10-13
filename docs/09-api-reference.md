# 9. HTTP API reference

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/api> · OpenAPI: <https://api.typesafe.ai/docs/>

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `https://api.typesafe.ai/v1/systemone` | Evaluate a state against typed questions |
| `GET` | `https://api.typesafe.ai/v1/models` | List the model names your account can use |

Authentication on every call:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

---

## `POST /v1/systemone`

### Request body

| Field | Type | Description |
|---|---|---|
| `state` | `string \| object \| array` | The content to evaluate. See [State](03-state.md). |
| `model` | `string` | For example `"jev-latest"`. See [Models](12-models.md). |
| `questions` | `map<string, Question>` | Question IDs you choose, mapped to question objects. Answers come back under the same keys. **Keys aren't sent to the model.** |

```json
{
  "state": "Help! My payouts have been failing for 3 days.",
  "model": "jev-latest",
  "questions": {
    "is_urgent": { "type": "noul", "instructions": "Does this convey urgency?" }
  }
}
```

### Question types

Every question has `type` and `instructions` (`string | object | array`). Each type adds its own `criteria`.

#### Noul

| Field | Type | Notes |
|---|---|---|
| `type` | `"noul"` | |
| `instructions` | `string \| object \| array` | A yes/no question |
| `criteria` | `object` *(optional)* | `true`: what a yes (near 1) means. `false`: what a no (near 0) means. |

```json
"is_urgent": {
  "type": "noul",
  "instructions": "Does this convey urgency?",
  "criteria": {
    "true": "Explicitly time-sensitive",
    "false": "No urgency expressed"
  }
}
```

#### Choice

| Field | Type | Notes |
|---|---|---|
| `type` | `"choice"` | |
| `instructions` | `string \| object \| array` | |
| `criteria` | `map<string, string \| object \| array \| null>` | Option → description. **Max 255 options.** |

```json
"department": {
  "type": "choice",
  "instructions": "Which team should handle this?",
  "criteria": {
    "billing": "Payments, invoicing, refunds",
    "technical": "Bugs, outages, integrations",
    "sales": "Pricing, upgrades, new accounts"
  }
}
```

#### Score

| Field | Type | Notes |
|---|---|---|
| `type` | `"score"` | |
| `instructions` | `string \| object \| array` | |
| `criteria` | `array<string \| object \| array>` | Ordered level descriptions, low to high. **At least 2, at most 10.** |

```json
"frustration": {
  "type": "score",
  "instructions": "How frustrated is the customer?",
  "criteria": ["Calm", "Frustrated", "Very angry"]
}
```

#### Structured `instructions`

Put the question in one field and the data it refers to in others. Refer to the data fields by name in backticks:

```json
"instructions": {
  "potential_duplicate": {
    "name": "John Smith",
    "location": "Oakland, California",
    "last_employer": "Google"
  },
  "question": "Is the resume for the same person as `potential_duplicate`?"
}
```

### Response body

| Field | Type | Description |
|---|---|---|
| `model` | `string` | The **versioned** model that answered, for example `jev-1.13.0` |
| `answers` | `map<string, Answer>` | One answer per question ID |
| `usage` | `{ input_tokens: int \| null, output_tokens: int \| null }` | Token usage, when reported. The Python SDK types both counts as `int \| None`, so handle a missing count. |

### Answer types

#### Noul answer

```json
{ "type": "noul", "noul": 0.95 }
```

| Field | Type | Description |
|---|---|---|
| `noul` | `number` | 0 (no) to 1 (yes) |

#### Choice answer

```json
{
  "type": "choice",
  "choice": "billing",
  "probabilities": { "billing": 0.88, "technical": 0.12, "sales": 0.0 },
  "confidence": 0.81
}
```

| Field | Type | Description |
|---|---|---|
| `choice` | `string` | The highest-probability option |
| `probabilities` | `map<string, number>` | Sums to 1 |
| `confidence` | `number` | Derived from `probabilities`. See [Confidence](05-confidence.md#choice). |

#### Score answer

```json
{
  "type": "score",
  "score": 1.05,
  "legend": { "0": "Calm", "1": "Frustrated", "2": "Very angry" },
  "probabilities": { "0": 0.0, "1": 0.95, "2": 0.05 },
  "confidence": 0.92
}
```

| Field | Type | Description |
|---|---|---|
| `score` | `number` | Probability-weighted level; can fall between levels |
| `legend` | `map<string, string>` | Level number → description |
| `probabilities` | `map<string, number>` | Level number (string key) → probability |
| `confidence` | `number` | See [Confidence](05-confidence.md#score) |

---

## `GET /v1/models`

```bash
curl https://api.typesafe.ai/v1/models \
  -H "Authorization: Bearer $TYPESAFE_API_KEY"
```

Returns `{ "models": [ { "name", "description", "release_date" }, ... ] }`. It currently lists the aliases. Versioned IDs such as `jev-1.13.0` are accepted in `model` whether or not they're listed.

### Health check: list models, then confirm which version answers

TypeSafe doesn't document a dedicated health endpoint. `GET /v1/models` is a cheap probe: it checks connectivity and your API key without evaluating anything. To learn which concrete version an alias resolves to, read `model` from a real System One response; the models list shows aliases, not versions. *This is a suggested pattern, not official guidance.*

**Python**

```python
from typesafe_sdk import Noul, RetryPolicy, TypeSafeAPIError, TypeSafeClient, TypeSafeError

client = TypeSafeClient()
FAIL_FAST = RetryPolicy(max_retries=0)  # a health check should report problems, not wait them out


def health_check() -> dict[str, object]:
    try:
        names = [m.name for m in client.models.list(retry=FAIL_FAST, timeout=5).models]
        probe = client.system_one("ping", {"ok": Noul(instructions="Is this text non-empty?")}, retry=FAIL_FAST, timeout=5)
    except TypeSafeAPIError as err:  # reached the API, which answered with an error (401, 429, 529, ...)
        return {"ok": False, "status": err.status}
    except TypeSafeError as err:  # never reached it: network error or timeout
        return {"ok": False, "error": type(err).__name__}
    return {"ok": True, "models": names, "answered_by": probe.model}  # e.g. "jev-1.13.0"
```

**TypeScript**

<!-- ts-check run -->
```ts
import { APIError, noul, TypeSafeClient, TypeSafeError } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const FAIL_FAST = { retry: { maxRetries: 0 }, timeout: 5_000 }; // report problems, don't wait them out

async function healthCheck() {
  try {
    const models = await client.models.list(FAIL_FAST); // ModelCard[]: name, description, release_date
    const probe = await client.systemOne({ state: "ping", questions: { ok: noul("Is this text non-empty?") } }, FAIL_FAST);
    return { ok: true, models: models.map((m) => m.name), answeredBy: probe.model }; // e.g. "jev-1.13.0"
  } catch (err) {
    if (err instanceof APIError) return { ok: false, status: err.status }; // 401, 429, 529, ...
    if (err instanceof TypeSafeError) return { ok: false, error: err.name }; // network error or timeout
    throw err;
  }
}

console.log(await healthCheck());
```

The System One probe is billed like any request, but a one-word state costs a handful of tokens. Skip it if listing models is enough.

---

## Errors

| Status | Meaning |
|---|---|
| `401 Unauthorized` | Missing or invalid API key |
| `422 Unprocessable Entity` | Validation failed, for example a missing field or a malformed question. The body names the offending field. |
| `429 Too Many Requests` | Rate limit exceeded. Back off and retry. |
| `529 Overloaded` | Temporarily overloaded. Retry after a short delay. |

Both SDKs also retry `408` and `5xx` by default. Responses carry an `x-typesafe-request-id` header, which is worth logging.

### Handling rate limits yourself (no SDK)

On `429` or `529`, retry with exponential backoff and honor `Retry-After` when it's present. The SDKs do this automatically.

```python
import os
import random
import time

import requests

URL = "https://api.typesafe.ai/v1/systemone"
HEADERS = {"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}


def system_one(payload: dict, max_retries: int = 5) -> dict:
    delay = 0.5
    for attempt in range(max_retries + 1):
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        if r.status_code not in (408, 429, 529) and r.status_code < 500:
            r.raise_for_status()
            return r.json()
        if attempt == max_retries:
            r.raise_for_status()
        retry_after = r.headers.get("retry-after")
        wait = float(retry_after) if retry_after else delay * (1 - 0.25 * random.random())
        time.sleep(min(wait, 60))
        delay = min(delay * 2, 5)
```

```ts
async function systemOne(payload: unknown, maxRetries = 5): Promise<any> {
  let delay = 500;
  for (let attempt = 0; ; attempt++) {
    const res = await fetch("https://api.typesafe.ai/v1/systemone", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.TYPESAFE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const retryable = [408, 429, 529].includes(res.status) || res.status >= 500;
    if (res.ok) return res.json();
    if (!retryable || attempt === maxRetries) {
      throw new Error(`${res.status} ${await res.text()} (request ${res.headers.get("x-typesafe-request-id")})`);
    }
    const ra = res.headers.get("retry-after");
    await new Promise((r) => setTimeout(r, ra ? Number(ra) * 1000 : delay * (1 - 0.25 * Math.random())));
    delay = Math.min(delay * 2, 5000);
  }
}
```

---

[← 8. Cookbooks](08-cookbooks.md) · Next: [10. Python SDK →](10-sdk-python.md)
