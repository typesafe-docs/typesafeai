# 14. Cheat sheet

[← Back to README](../README.md)

Everything on one page. Each section links to the full chapter.

## Endpoint

```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json
```

```json
{ "state": "<string | object | array>", "model": "jev-latest", "questions": { "<id>": { "type": "...", "instructions": "...", "criteria": "..." } } }
```

[→ API reference](09-api-reference.md)

## The four question types

| | Choice | Score | Noul | Box |
|---|---|---|---|---|
| Asks | Which option? | Which level? | Is it true? | Where is it in this image? |
| `criteria` | `{option: description \| null}` (≤ 255) | `[level0, level1, ...]` (2–10, ordered) | optional `{true, false}` | none |
| Returns | `choice`, `probabilities`, `confidence` | `score`, `legend`, `probabilities`, `confidence` | `noul` (0–1) | `box` (`top`, `bottom`, `left`, `right` as fractions), `confidence` |
| Maps to | a `switch` | a threshold or a sort | an `if` | a crop or a highlight |

Box needs Jev 1.14 and the `TypeSafe-Danger-Zone-Images: true` header; pair it with a Noul that asks whether the thing is there. Any question can read PNG/JPEG [images](04-primitives/images.md).

```json
{
  "department": { "type": "choice", "instructions": "Which team should handle this?",
                  "criteria": { "billing": "Charges, invoices", "technical": "Bugs, outages", "other": null } },
  "severity":   { "type": "score",  "instructions": "How severe is the reported issue?",
                  "criteria": ["Cosmetic", "Broken but workaround exists", "Blocking, no workaround"] },
  "is_urgent":  { "type": "noul",   "instructions": "Does the message convey urgency?",
                  "criteria": { "true": "Explicitly time-sensitive", "false": "No urgency expressed" } }
}
```

[→ Primitives](04-primitives/README.md)

## Python

```python
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient, AsyncTypeSafeClient, RetryPolicy

client = TypeSafeClient()                                   # TYPESAFE_API_KEY, jev-latest
r = client.system_one(state, {"q": Noul(instructions="...")})

r.nouls["q"].noul                    # float 0..1
r.choices["q"].choice                # str
r.choices["q"].probabilities         # dict[str, float]
r.choices["q"].confidence            # float 0..1
r.scores["q"].score                  # float, 0..len(criteria)-1
r.scores["q"].legend                 # dict[int, ...]
r.boxes["q"].box                     # BoxCoordinates: top, bottom, left, right
r.model, r.usage.input_tokens, r.request_id   # usage counts are int | None

TypeSafeClient(model="jev-1.14.0", timeout=10.0, retry=RetryPolicy(max_retries=3), base_url=...)
client.system_one(state, questions, model=..., retry=..., timeout=..., extra_headers=..., extra_body=..., response_model=...)
client.models.list().models
```

[→ Python guide](10-sdk-python.md) · [→ Full Python reference](reference/python/README.md)

## TypeScript

<!-- ts-check:

declare const state: string; declare const signal: AbortSignal;
-->
```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultModel: "jev-latest", timeout: 10_000, retry: { maxRetries: 2 } });
const { answers, model, usage } = await client.systemOne(
  { state, questions: { q: choice("Which?", { a: null, b: "desc" }), s: score("How?", ["low", "high"]), n: noul("Is it?") } },
  { timeout: 5_000, signal },
);
answers.q.choice;  answers.q.probabilities;  answers.q.confidence;
answers.s.score;   answers.s.legend;         answers.n.noul;

const { data, response, requestId } = await client.systemOne({ state, questions: { n: noul("Is it?") } }).withResponse();
```

[→ JS guide](11-sdk-javascript.md) · [→ Full JS reference](reference/javascript/README.md)

## Confidence at a glance

| Type | Field | Range | Formula |
|---|---|---|---|
| Noul | none (use `noul`) | 0–1 | `abs(2p − 1)` if you need one |
| Choice | `confidence` | 0–1 | top probability, rescaled so uniform = 0 |
| Score | `confidence` | 0–1 | 1 − spread around the top level ÷ spread of a uniform distribution |

Code for all three: [→ How confidence is calculated](05-confidence.md#how-confidence-is-calculated)

| Confidence | Do |
|---|---|
| High | Act automatically |
| Medium | Confirm, review, or gather more information |
| Low | Route to a human or a fallback system |

Thresholds should **scale with the cost of being wrong**. [→ Confidence](05-confidence.md)

## Patterns in one line each

| Pattern | One-liner |
|---|---|
| [Speculative fan-out](07-patterns.md#speculative-fan-out) | Ask every question you *might* need in one call, and ignore the irrelevant answers. |
| [Screen with a Noul first](07-patterns.md#screen-with-a-noul-first) | One cheap yes/no first; run the expensive step only on a clear yes. |
| [Companion Noul](07-patterns.md#companion-noul) | Pair a Choice with "does any option fit?" and trust the Choice only on a clear yes. |
| [Routing by confidence](07-patterns.md#routing-by-confidence) | `if score.confidence < 0.5: person; else route on score.score` |
| [Routing by probability](07-patterns.md#routing-by-probability) | `p = probabilities[choice]`; higher bar for riskier actions (e.g. 0.7, 0.9) |
| [Composite scoring](07-patterns.md#composite-scoring) | `sum(w_k * score_k / top_level_k)`: weights live in code. |

## Do and don't

| ✅ Do | ❌ Don't |
|---|---|
| Ask one snap judgment per question | Ask "analyze this and decide what to do" |
| Send many questions per request | Make one round trip per question |
| Describe levels as situations | Use `["0", "1", "2"]` as levels |
| Add a companion Noul ("does any option fit?") | Force a fit with no escape hatch |
| Phrase a Noul so high means yes | Invert `true`/`false` against the instruction |
| Filter the state down to what's relevant | Dump the whole database into `state` |
| Do math, counting, and date comparison in code | Ask Jev to count or compare dates |
| Extract candidates with regex, then let Jev **pick** | Ask Jev to generate text |
| Pin `jev-1.14.0` once thresholds are tuned | Tune against `jev-latest` and forget |
| Keep questions and thresholds in one file | Scatter prompts across the codebase |

## Limits & pricing (Jev 1.14 and 1.13)

| | |
|---|---|
| Price | $0.042 per million input tokens; output is free |
| Rate limits | Per organization, in tokens/s and requests/s; see console.typesafe.ai/rate-limits |
| Context | 64k per request; 32k for state plus any one question. `TypeSafe-Danger-Zone-Long-Context: true` raises both to 262k (slower, less accurate) |
| Input | Text, plus PNG/JPEG images (280–1568 px per side, 16 MiB each, 32 MiB body) |
| Options | Choice ≤ 255; Score 2–10 levels |
| Questions per request | No separate limit; the context limits above apply |
| Latency | About 100 ms for most requests; extra questions barely add to it |
| SDK timeouts | 10 s per attempt, 2 retries; Python also caps the whole call at 30 s (`RetryPolicy.timeout`) |
| Errors | 400 · 401 · 413 · 415 · 422 · 429 · 529 (the SDKs retry 408, 429, and 5xx) |

[→ Models](12-models.md)

---

[← 13. Agent skill](13-agent-skill.md) · Next: [15. FAQ →](15-faq.md)
