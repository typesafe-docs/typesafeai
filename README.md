# TypeSafe AI — Developer Guide

> Community documentation and code snippets for **TypeSafe AI**: the System One API and its flagship model, **Jev**.
> Everything here comes from the official docs at **<https://docs.typesafe.ai/>**. When this repo and the official docs disagree, the official docs are right.

TypeSafe's models don't generate text. You send a **state** (the content to judge) and a set of typed **questions**. You get back **typed answers**: a choice, a score, or a probability, along with the full probability distribution and a **confidence** value. Your code can branch on them, sort by them, and route with them directly. There's no prompt-to-JSON parsing.

```text
 state + questions ──(one request)──▶  Jev (evaluates every question in parallel)
                                          │
 your code ◀──(one response)── typed answers + probabilities + confidence
 (branch, sort, route)
```

---

## Table of contents

### Guide

| # | Section | What's inside |
|---|---------|---------------|
| 1 | [Introduction & concepts](docs/01-introduction.md) | System One, how Jev differs from an LLM, using it with coding agents, the RLCD primer, use cases |
| 2 | [Quick start](docs/02-quickstart.md) | Playground, cURL, raw HTTP, Python, TypeScript, agent skill |
| 3 | [State](docs/03-state.md) | Strings, objects, arrays, and pointing at nested fields |
| 4 | [Primitives (questions)](docs/04-primitives/README.md) | Picking a question type and asking many at once |
| 4.1 | [Choice](docs/04-primitives/choice.md) | Pick one option from a set |
| 4.2 | [Score](docs/04-primitives/score.md) | Place the state on ordered levels |
| 4.3 | [Noul](docs/04-primitives/noul.md) | Probability that a yes/no statement is true |
| 4.4 | [Advanced: structure](docs/04-primitives/advanced-structure.md) | JSON instructions, rubrics, walking a taxonomy, structured criteria |
| 5 | [Confidence](docs/05-confidence.md) | What confidence means, the formulas, thresholds that scale with risk |
| 6 | [How to build with TypeSafe](docs/06-building-with-typesafe.md) | Eight design steps, spam and tool-trace decomposition, a full triage workflow |
| 7 | [Patterns](docs/07-patterns.md) | Speculative fan-out, confidence-gated routing, composite scoring, intent routing |
| 8 | [Cookbooks overview](docs/08-cookbooks.md) | The 20 official recipes summarized, each with its core snippet |
| 9 | [HTTP API reference](docs/09-api-reference.md) | `POST /v1/systemone`, `GET /v1/models`, schemas, errors, DIY retries |
| 10 | [Python SDK guide](docs/10-sdk-python.md) | Sync and async, typed responses, retries, errors, gateways, HTTP/2 |
| 11 | [JavaScript / TypeScript SDK guide](docs/11-sdk-javascript.md) | `choice()`, `noul()`, `score()`, inferred types, `APIPromise`, errors |
| 12 | [Models, limits & jaggedness](docs/12-models.md) | Jev 1.13, aliases, pricing, rate limits, the 9 known failure modes |
| 13 | [Agent skill](docs/13-agent-skill.md) | Teaching Claude Code, Codex, and other agents to write TypeSafe code |
| 14 | [Cheat sheet](docs/14-cheatsheet.md) | Everything on one page |
| 15 | [FAQ & troubleshooting](docs/15-faq.md) | Common questions and pitfalls, each with a code fix |

### Full cookbooks (every code cell, output, and chart)

| Area | Recipes |
|---|---|
| LLMs and agents | [Function calling](docs/cookbooks/function_calling.md) · [Skill suggestion](docs/cookbooks/skill_suggestion.md) · [LLM guardrails](docs/cookbooks/llm_guardrails.md) · [Citation check](docs/cookbooks/citation_check.md) · [Classifying RAG passages](docs/cookbooks/classifying_rag_passages.md) · [Simple memory system](docs/cookbooks/basic_memory.md) |
| Classification | [Hierarchical](docs/cookbooks/hierarchical_classification.md) · [Using confidence](docs/cookbooks/classification_using_confidence.md) · [Twitch chat filter](docs/cookbooks/twitch_chat_filter.md) |
| Extraction | [SDE cascade](docs/cookbooks/sde_cascade.md) · [Date extraction](docs/cookbooks/date_extraction_cookbook.md) · [Pre-parsed values](docs/cookbooks/pre_parsed_value_extraction_cookbook.md) · [Structure recovery](docs/cookbooks/autoformat.md) |
| Search and matching | [Re-ranking](docs/cookbooks/rerank_typesafe.md) · [Line-by-line search](docs/cookbooks/semantic_find.md) · [Entity alignment](docs/cookbooks/entity_alignment.md) |
| Techniques | [Self-consistency: nouls](docs/cookbooks/consistency_noul_cookbook.md) · [Self-consistency: choices](docs/cookbooks/consistency_choice_cookbook.md) · [Parallel questions](docs/cookbooks/parallel_questions.md) · [Autoresearch features](docs/cookbooks/autoresearch_feature_discovery.md) |

### Full SDK API reference (generated from the official docs)

- **Python** (`typesafe-sdk`): [index](docs/reference/python/README.md) · [usage](docs/reference/python/usage.md) · [sync client](docs/reference/python/sync-client.md) · [async client](docs/reference/python/async-client.md) · [questions](docs/reference/python/questions.md) · [responses](docs/reference/python/responses.md) · [retries](docs/reference/python/retries.md) · [exceptions](docs/reference/python/exceptions.md) · [constants](docs/reference/python/constants.md) · [changelog](docs/reference/python/changelog.md)
- **JavaScript** (`@typesafe-ai/sdk`): [index](docs/reference/javascript/README.md) · [classes](docs/reference/javascript/classes.md) · [interfaces](docs/reference/javascript/interfaces.md) · [type aliases](docs/reference/javascript/type-aliases.md) · [functions](docs/reference/javascript/functions.md) · [variables](docs/reference/javascript/variables.md) · [changelog](docs/reference/javascript/changelog.md)

### Python and TypeScript, side by side

Every code example in the guide comes in **Python** and **TypeScript**, labeled and next to each other. The cookbook snippets also have TypeScript ports, marked as ports because the official cookbooks are Python-only. All 118 TypeScript snippets in the guide are **type-checked against the real `@typesafe-ai/sdk` in CI**, and the 47 self-contained ones also run against the offline mock ([`tools/check_doc_snippets.py`](tools/check_doc_snippets.py)).

### Runnable examples

[`examples/`](examples/) holds 2 cURL scripts, 14 Python scripts, and 4 TypeScript files, all **type-checked and run in CI** against an offline [mock API](examples/mock/mock_server.py). You can try them without a key.

---

## The three primitives at a glance

| Question type | Asks | Returns |
|---|---|---|
| [**Choice**](docs/04-primitives/choice.md) | Which of these options? | `choice`, `probabilities`, `confidence` |
| [**Score**](docs/04-primitives/score.md) | Which level on this rubric? | `score`, `legend`, `probabilities`, `confidence` |
| [**Noul**](docs/04-primitives/noul.md) | Is this statement true? | `noul` (probability of yes, 0–1) |

You can mix all three in one call. Each question is evaluated **independently and in parallel** against the same state, so adding questions barely changes latency.

---

## 60-second quick start

### 1. Get an API key

Create one at <https://console.typesafe.ai/keys>, then export it:

```bash
export TYPESAFE_API_KEY="your-key-here"
```

### 2. cURL

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this",
      "criteria": {
        "billing": "Payment or subscription issues",
        "technical": "Bugs or integration problems",
        "sales": "Pricing or account questions"
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated the customer appears",
      "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]
    },
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
EOF
```

Response:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "technical",
      "confidence": 0.78,
      "probabilities": { "technical": 0.85, "sales": 0.0, "billing": 0.15 }
    },
    "frustration": {
      "type": "score",
      "score": 1.0,
      "confidence": 1.0,
      "legend": { "0": "Calm, just stating facts", "1": "Frustrated but civil", "2": "Very angry, strong language" },
      "probabilities": { "0": 0.0, "1": 1.0, "2": 0.0 }
    },
    "is_urgent": { "type": "noul", "noul": 1.0 }
  },
  "usage": { "input_tokens": 392, "output_tokens": 65 }
}
```

### 3. Python (`pip install typesafe-sdk`)

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()  # reads TYPESAFE_API_KEY, defaults to jev-latest

response = client.system_one(
    state="Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    questions={
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "billing": "Payment or subscription issues",
                "technical": "Bugs or integration problems",
                "sales": "Pricing or account questions",
            },
        ),
        "frustration": Score(
            instructions="How frustrated the customer appears",
            criteria=["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
        ),
        "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
    },
)

print(response.answers["department"].choice)  # "technical"
print(response.answers["frustration"].score)  # 1.0
print(response.answers["is_urgent"].noul)     # 1.0
```

### 4. TypeScript (`npm install @typesafe-ai/sdk`)

```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const { answers } = await client.systemOne({
  state: "I was charged twice. Please fix this ASAP.",
  questions: {
    category: choice("What is this ticket about?", { billing: null, technical: null, other: null }),
    urgency: score("How urgent is this ticket?", ["can wait", "this week", "today"]),
    refund: noul("Does the customer ask for a refund?"),
  },
});

console.log(answers.category.choice, answers.urgency.score, answers.refund.noul);
```

---

## Core ideas in five bullets

1. **Ask atomic questions.** Each question should be a snap judgment that a knowledgeable person could make in a second. Break big judgments into parts and [combine them in code](docs/07-patterns.md#composite-scoring).
2. **Ask a lot of questions per call.** They run in parallel. [Speculative](docs/07-patterns.md#speculative-fan-out) questions cost almost nothing.
3. **Keep control flow in code.** Jev makes narrow decisions. Your code owns the workflow, the rules, and the side effects.
4. **Route on confidence.** Act automatically when confidence is high, confirm when it's medium, and escalate when it's low. [Scale your thresholds with risk](docs/05-confidence.md#thresholds-scale-with-risk).
5. **Don't ask Jev to do math, count, compare dates, or generate text.** Do those in code. See [Jaggedness](docs/12-models.md#known-failure-modes-jev-113).

---

## Repository layout

```text
.
├── README.md                       ← you are here
├── docs/
│   ├── 01-introduction.md … 15-faq.md   ← the guide (hand-written, curated)
│   ├── 04-primitives/                    ← Choice, Score, Noul, structure
│   ├── cookbooks/                        ← 20 full recipes (converted from the official notebooks)
│   ├── reference/
│   │   ├── python/                       ← full typesafe-sdk API reference
│   │   └── javascript/                   ← full @typesafe-ai/sdk API reference
│   └── assets/                           ← charts and figures used by the cookbooks
├── examples/
│   ├── curl/  python/  typescript/       ← runnable examples
│   ├── mock/mock_server.py               ← offline fake API for running examples
│   └── run_all.sh
├── tools/sync_docs.py                    ← regenerate cookbooks and reference from docs.typesafe.ai
├── tools/check_doc_snippets.py           ← type-check and run every TypeScript snippet in the guide
└── .github/workflows/examples.yml        ← type-check and run every example, check links
```

## Keeping it in sync

The cookbooks and SDK reference are generated from the official site. To pull the latest:

```bash
python3 tools/sync_docs.py            # fetch every page in docs.typesafe.ai/llms.txt and regenerate
python3 tools/sync_docs.py --offline  # reconvert from tools/.cache without fetching
git diff --stat docs/cookbooks docs/reference
```

The converter ([`tools/mdx_to_gfm.py`](tools/mdx_to_gfm.py)) turns Mintlify MDX into GitHub Markdown. It restores the interactive `<TypesafeExample>` requests as JSON, rebuilds `<SdkSignature>` blocks as code, turns callouts, tabs, accordions and steps into GitHub equivalents, downloads the charts into `docs/assets/`, and rewrites links to point inside this repo. The hand-written guide (`docs/01`–`15`) is never overwritten.

## Official links

- Docs: <https://docs.typesafe.ai/> · LLM-friendly index: <https://docs.typesafe.ai/llms.txt>
- Console & Playground: <https://console.typesafe.ai/playground>
- Python SDK: <https://github.com/typesafe-ai/typesafe-sdk-python> (`pip install typesafe-sdk`)
- JS SDK: <https://github.com/typesafe-ai/typesafe-sdk-js> (`npm install @typesafe-ai/sdk`)
- Agent skill: <https://github.com/typesafe-ai/skills>
- Discord: <https://discord.com/invite/WUujKYBp8s>

## Disclaimer

This is an unofficial, community-maintained guide. It isn't affiliated with or endorsed by TypeSafe. Request and response examples are copied from the official docs, and the responses are the recorded values published there. The full cookbook and SDK reference pages are converted mechanically from the official per-page Markdown, with the interactive request examples, signatures, and charts restored. Some glue code in the guide, such as router helpers and condensed cookbook code, is adapted and labeled illustrative. Your own results may differ by model version.
