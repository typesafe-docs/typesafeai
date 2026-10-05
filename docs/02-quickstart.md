# 2. Quick start

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/introduction/quickstart>

There are four ways in: **try** it in the Playground, **call** the HTTP API, **code** against an SDK, or **vibe** with the agent skill.

## Try it: the Playground

1. Open <https://console.typesafe.ai/playground> and log in.
2. Paste any text as the state:

   ```text
   Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.
   ```

3. Add a Noul question:

   ```json
   {
     "urgency": {
       "type": "noul",
       "instructions": "Does this message express urgency?"
     }
   }
   ```

4. Add more questions, mixing Noul, Choice, and Score, and see every result at once.

## Call it: the HTTP API

1. Get an API key at <https://console.typesafe.ai/keys>.
2. `POST` to the endpoint:

```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

### Minimal cURL

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
  {
    "state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    "model": "jev-latest",
    "questions": {
      "urgency": {
        "type": "noul",
        "instructions": "Does this message express urgency?"
      }
    }
  }
EOF
```

### Full request: all three types

```json
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
      "criteria": [
        "Calm, just stating facts",
        "Frustrated but civil",
        "Very angry, strong language"
      ]
    },
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```

### Response

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
      "legend": {
        "0": "Calm, just stating facts",
        "1": "Frustrated but civil",
        "2": "Very angry, strong language"
      },
      "probabilities": { "0": 0.0, "1": 1.0, "2": 0.0 }
    },
    "is_urgent": { "type": "noul", "noul": 1.0 }
  },
  "usage": { "input_tokens": 392, "output_tokens": 65 }
}
```

### Same call from Python with no SDK

```python
import os
import requests

resp = requests.post(
    "https://api.typesafe.ai/v1/systemone",
    headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
    json={
        "state": "Help! My payouts have been failing for 3 days.",
        "model": "jev-latest",
        "questions": {
            "is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"}
        },
    },
    timeout=10,
)
resp.raise_for_status()
print(resp.json()["answers"]["is_urgent"]["noul"])
```

### Same call from Node with plain `fetch`

```ts
const res = await fetch("https://api.typesafe.ai/v1/systemone", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.TYPESAFE_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    state: "Help! My payouts have been failing for 3 days.",
    model: "jev-latest",
    questions: { is_urgent: { type: "noul", instructions: "Does this convey urgency?" } },
  }),
});
const data = await res.json();
console.log(data.answers.is_urgent.noul);
```

## Code it: the Python SDK

Requires Python 3.10 or later.

```bash
pip install typesafe-sdk     # or: uv add typesafe-sdk
# optional HTTP/2 support:
pip install 'typesafe-sdk[http2]'
```

The client reads `TYPESAFE_API_KEY` from the environment and calls `jev-latest` by default.

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()

ticket = "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."

response = client.system_one(
    state=ticket,
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
            criteria=[
                "Calm, just stating facts",
                "Frustrated but civil",
                "Very angry, strong language",
            ],
        ),
        "is_urgent": Noul(
            instructions="The message conveys urgency or time-sensitivity",
        ),
    },
)

print(response.answers["department"].choice)  # "technical"
print(response.answers["frustration"].score)  # 1.0
print(response.answers["is_urgent"].noul)     # 1.0
```

Typed accessors by answer kind:

**Python**

```python
response.choices["department"].choice
response.scores["frustration"].score
response.nouls["is_urgent"].noul
```

**TypeScript**

<!-- ts-check:
import { choice, noul, score } from "@typesafe-ai/sdk";
declare const answers: import("@typesafe-ai/sdk").SystemOneResult<{
  department: ReturnType<typeof choice<{ billing: string; technical: string; sales: string }>>;
  frustration: ReturnType<typeof score<readonly [string, string, string]>>;
  is_urgent: ReturnType<typeof noul>;
}>["answers"];
-->
```ts
// In TypeScript every answer is already typed from its question, so no per-kind accessors are needed:
answers.department.choice;    // "billing" | "technical" | "sales"
answers.frustration.score;    // number
answers.is_urgent.noul;       // number
```

Full guide: [Python SDK](10-sdk-python.md).

## Code it: the JavaScript / TypeScript SDK

Requires Node.js 20 or later.

```bash
npm install @typesafe-ai/sdk
```

```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    category: choice("What is this ticket about?", {
      billing: null,
      technical: null,
      other: null,
    }),
  },
});

console.log(response.answers.category.choice); // typed as "billing" | "technical" | "other"
```

Full guide: [JavaScript SDK](11-sdk-javascript.md).

## Vibe it: the agent skill

**Claude Code:**

```bash
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai
```

**Other agents** (Codex and others):

```bash
npx skills add typesafe-ai/skills --skill typesafe-ai      # add -g to install globally
```

Then prompt your agent:

```text
Let's build a simple CLI that uses the TypeSafe API to evaluate a set of supplied documents
on multiple dimensions. Use the TypeSafe skill to understand how to use the TypeSafe API and
how to structure the system. Ask me questions about what kinds of documents I want to evaluate
and on what dimensions.
```

More in [Agent skill](13-agent-skill.md).

---

[← 1. Introduction](01-introduction.md) · Next: [3. State →](03-state.md)
