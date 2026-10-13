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

## The three question types

| | Choice | Score | Noul |
|---|---|---|---|
| Asks | Which option? | Which level? | Is it true? |
| `criteria` | `{option: description \| null}` (≤ 255) | `[level0, level1, ...]` (2–10, ordered) | optional `{true, false}` |
| Returns | `choice`, `probabilities`, `confidence` | `score`, `legend`, `probabilities`, `confidence` | `noul` (0–1) |
| Maps to | a `switch` | a threshold or a sort | an `if` |

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
r.model, r.usage.input_tokens, r.request_id

TypeSafeClient(model="jev-1.13.0", timeout=10.0, retry=RetryPolicy(max_retries=3), base_url=...)
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
| [Confidence-gated routing](07-patterns.md#confidence-gated-routing) | `if conf < floor: human; elif risky and conf < high: confirm; else act` |
| [Composite scoring](07-patterns.md#composite-scoring) | `sum(w_k * score_k / top_level_k)`: weights live in code. |
| [Intent routing](07-patterns.md#intent-routing) | A fast Choice in front of deterministic code, specialist LLMs, and humans. |

## Do and don't

| ✅ Do | ❌ Don't |
|---|---|
| Ask one snap judgment per question | Ask "analyze this and decide what to do" |
| Send many questions per request | Make one round trip per question |
| Describe levels as situations | Use `["0", "1", "2"]` as levels |
| Add `other` or `none` options | Force a fit with no escape hatch |
| Phrase a Noul so high means yes | Invert `true`/`false` against the instruction |
| Filter the state down to what's relevant | Dump the whole database into `state` |
| Do math, counting, and date comparison in code | Ask Jev to count or compare dates |
| Extract candidates with regex, then let Jev **pick** | Ask Jev to generate text |
| Pin `jev-1.13.0` once thresholds are tuned | Tune against `jev-latest` and forget |
| Keep questions and thresholds in one file | Scatter prompts across the codebase |

## Limits & pricing (Jev 1.13)

| | |
|---|---|
| Price | $0.042 per million input tokens; output is free |
| Rate limits | 100K tokens/s and 80 requests/s (dynamic) |
| Context | 64k per request; 32k for state plus the longest question |
| Options | Choice ≤ 255; Score 2–10 levels |
| Questions per request | No documented count limit; the token limits above apply |
| Errors | 401 · 422 · 429 · 529 (the SDKs retry 408, 429, and 5xx) |

[→ Models](12-models.md)

---

[← 13. Agent skill](13-agent-skill.md) · Next: [15. FAQ →](15-faq.md)
