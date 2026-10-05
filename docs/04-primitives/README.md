# 4. Primitives (questions)

[← Back to README](../../README.md) · Source: <https://docs.typesafe.ai/primitives>

Primitives come in pairs: a **question** defines one judgment about a [state](../03-state.md), and its **answer** is the typed value that comes back. You compose the answers in code.

| Type | What it answers | Returns | Page |
|---|---|---|---|
| **Choice** | Which of these options? | `choice`, `probabilities`, `confidence` | [choice.md](choice.md) |
| **Score** | Which level? | `score`, `legend`, `probabilities`, `confidence` | [score.md](score.md) |
| **Noul** | Is this true? | `noul` (0 to 1) | [noul.md](noul.md) |

See also: [Advanced: structure](advanced-structure.md).

## Ask for one snap judgment per question

- ✅ "Does this message convey urgency?"
- ❌ "Analyze this message and determine the best course of action"

The second one needs slow reasoning. That's your cue to break the task into small questions and combine the answers in code.

## Anatomy of a question

| Field | Meaning |
|---|---|
| **ID** (map key) | A key you choose, like `refund_requested`. It's **never sent to the model**. |
| `type` | `choice`, `score`, or `noul` |
| `instructions` | The question itself, or a statement to judge. A string, object, or array. |
| `criteria` | Choice: a map of options. Score: an ordered list of levels. Noul: optional `{true, false}` descriptions. |

**Python**

```python
from typesafe_sdk import Noul

questions = {
    "refund_requested": Noul(
        instructions="Does the customer request a refund?",
    ),
}
```

**TypeScript**

```ts
import { noul } from "@typesafe-ai/sdk";

const questions = {
  refund_requested: noul("Does the customer request a refund?"),
};
```

> **Tip:** The question ID exists only for your code. Write the complete question in `instructions`, even when the ID seems to say it all.

## Choosing a question type

- **Choice:** the answer is one of a known set of options with no order between them, such as a department, a document type, or a programming language. Add an `other` or `none of the above` option when the list might not cover every input.
- **Score:** the answer sits on a spectrum and you can describe each point, such as bug severity, frustration, or skill level.
- **Noul:** a clean yes/no where the probability itself is the useful signal, such as "contains PII?", "requests a refund?", or "mentions distributed systems?".

> A Noul of 0.5 means yes and no are equally likely. It does **not** mean "medium". To measure *how much* Python someone knows, use a Score with levels like no experience → some familiarity → daily use → deep expertise.

When two types both seem to fit, pick the one your code can **act on directly**: a Choice maps to code paths, a Score maps to a threshold, and a Noul maps to an `if`.

## What comes back

| Type | Fields | How to read it |
|---|---|---|
| Choice | `choice`, `probabilities`, `confidence` | The selected option, the distribution over all options, and how peaked that distribution is |
| Score | `score`, `legend`, `probabilities`, `confidence` | A position along your levels (it can fall between two), the levels by number, and the distribution |
| Noul | `noul` | P(yes). Near 1 is a strong yes, near 0 a strong no, near 0.5 unsure. There's no separate confidence. |

Two properties make answers composable:

1. **Constrained:** answers are always distributions over *your* options. Nothing has to be recovered from prose.
2. **Independent:** one answer is never hidden context for another, so you can add or remove questions without changing the other results.

## Ask several questions together

Mix types freely. Questions are evaluated in parallel, so adding more barely changes latency and costs only the extra question tokens.

```json
{
  "state": "Our API integration started returning 500 errors on every request about 20 minutes ago, and we can't process any customer orders until this is fixed.",
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
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated the customer appears",
      "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]
    }
  }
}
```

The same idea with the Python SDK and a structured state:

**Python**

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

state = {
    "ticket_message": "My flight was cancelled. Can I get a refund?",
    "refund_policy": "Cancelled flights are eligible for a full refund.",
}

with TypeSafeClient() as client:
    response = client.system_one(
        state=state,
        questions={
            "refund_requested": Noul(
                instructions="Does `ticket_message` request a refund?",
            ),
            "request_type": Choice(
                instructions="What is the main request in `ticket_message`?",
                criteria={
                    "refund": "The customer wants money returned.",
                    "rebooking": "The customer wants a replacement flight.",
                    "information": "The customer is asking for information only.",
                },
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear in `ticket_message`?",
                criteria=[
                    "Calm and neutral.",
                    "Concerned but civil.",
                    "Very angry or using strong language.",
                ],
            ),
        },
    )

print(response.answers["refund_requested"].noul)
print(response.answers["request_type"].choice)
print(response.answers["frustration"].score)
```

**TypeScript**

<!-- ts-check run -->
```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const state = {
  ticket_message: "My flight was cancelled. Can I get a refund?",
  refund_policy: "Cancelled flights are eligible for a full refund.",
};

const client = new TypeSafeClient();
const { answers } = await client.systemOne({
  state,
  questions: {
    refund_requested: noul("Does `ticket_message` request a refund?"),
    request_type: choice("What is the main request in `ticket_message`?", {
      refund: "The customer wants money returned.",
      rebooking: "The customer wants a replacement flight.",
      information: "The customer is asking for information only.",
    }),
    frustration: score("How frustrated does the customer appear in `ticket_message`?", [
      "Calm and neutral.",
      "Concerned but civil.",
      "Very angry or using strong language.",
    ]),
  },
});

console.log(answers.refund_requested.noul);
console.log(answers.request_type.choice); // "refund" | "rebooking" | "information"
console.log(answers.frustration.score);
```

### Speculative questions

Ask every question your code *might* need, including ones that only matter for some inputs, and let the code ignore the rest. In the [Parallel questions cookbook](../08-cookbooks.md#parallel-questions), batching 13 questions into one call was about **12× cheaper** and **10× faster** than 13 separate calls, with identical answers. See [Speculative fan-out](../07-patterns.md#speculative-fan-out).

### Split complex judgments

One question per factor, weighted in code. See [Composite scoring](../07-patterns.md#composite-scoring) and the [Score page](score.md#splitting-a-complex-judgment).

### When one question really depends on another

Questions in the same request never see each other's answers. Make a **second request** only when your code *can't build it* without the first answer: it needs that answer to fetch more data, to decide what the state is made of, or to pick the next question's options. Otherwise, ask everything at once.

**Python**

```python
# Request 1: rank all candidates broadly
first = client.system_one(state=state, questions={"which": Choice(instructions=..., criteria=ALL_SKILLS)})
top3 = sorted(first.answers["which"].probabilities.items(), key=lambda kv: -kv[1])[:3]

# Request 2: fetch the full text for only the top 3 and re-judge (impossible before request 1)
second = client.system_one(state=state, questions=rerank_questions([name for name, _ in top3]))
```

**TypeScript**

<!-- ts-check:
import { choice, noul, TypeSafeClient, type NoulQuestion } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient;
declare const state: string;
declare const ALL_SKILLS: Record<string, string>;
declare function rerankQuestions(names: string[]): Record<string, NoulQuestion>;
-->
```ts
// Request 1: rank all candidates broadly
const first = await client.systemOne({
  state,
  questions: { which: choice("Which skill, if any, should be loaded?", ALL_SKILLS) },
});
const top3 = Object.entries(first.answers.which.probabilities)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 3)
  .map(([name]) => name);

// Request 2: fetch the full text for only the top 3 and re-judge (impossible before request 1)
const second = await client.systemOne({ state, questions: rerankQuestions(top3) });
```

The cookbooks that legitimately chain requests are [Skill suggestion](../08-cookbooks.md#skill-suggestion), [Structure recovery](../08-cookbooks.md#structure-recovery), and [Hierarchical classification](../08-cookbooks.md#hierarchical-classification).

---

[← 3. State](../03-state.md) · Next: [Choice →](choice.md)
