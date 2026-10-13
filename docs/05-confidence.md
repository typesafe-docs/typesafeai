# 5. Confidence

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/confidence>

Every Choice and Score answer includes `probabilities`, the distribution over your options or levels. The **shape** of that distribution shows how certain the model is. `confidence` boils that shape down to a single number from 0 to 1:

- **1:** all the probability is on one outcome.
- **0:** the probability is spread evenly.

Noul answers have no `confidence` field, because the `noul` value already carries the uncertainty.

> "If an intelligent system, whether human or machine, cannot express honest uncertainty, the system cannot be trusted."

## Three paths for using confidence

| Range | Behavior |
|---|---|
| **High** | Act automatically. |
| **Medium** | Proceed carefully: confirm with the user, flag for review, or gather more information. |
| **Low** | Don't act. Route to a human, ask for clarification, or fall back to another system. |

## Thresholds scale with risk

A threshold isn't a single number. Riskier actions need higher confidence.

**Python**

```python
from typesafe_sdk import Choice

response = client.system_one(
    state=user_message,
    questions={
        "action": Choice(
            instructions="What is the user trying to do?",
            criteria={
                "check_balance": "View account balance",
                "approve_transfer": "Approve the pending withdrawal request",
                "support": "Get help with an issue",
            },
        ),
    },
)

action = response.answers["action"]
confidence = action.confidence

if confidence < 0.5:
    # Model is genuinely unsure. Don't guess.
    route_to_human(user_message)

elif action.choice == "check_balance":
    # Low stakes. Showing the wrong screen is recoverable.
    show_balance(account_id)

elif action.choice == "approve_transfer":
    if confidence > 0.9:
        # High stakes, high confidence. Proceed with confirmation.
        confirm_then_execute(account_id)
    else:
        # High stakes, moderate confidence. Verify first.
        ask_user_to_confirm(account_id)
```

**TypeScript**

<!-- ts-check:
import { TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient;
declare const userMessage: string;
declare const accountId: string;
declare function routeToHuman(m: string): void;
declare function showBalance(a: string): void;
declare function confirmThenExecute(a: string): void;
declare function askUserToConfirm(a: string): void;
-->
```ts
import { choice } from "@typesafe-ai/sdk";

const { answers } = await client.systemOne({
  state: userMessage,
  questions: {
    action: choice("What is the user trying to do?", {
      check_balance: "View account balance",
      approve_transfer: "Approve the pending withdrawal request",
      support: "Get help with an issue",
    }),
  },
});

const { choice: action, confidence } = answers.action;

if (confidence < 0.5) {
  // Model is genuinely unsure. Don't guess.
  routeToHuman(userMessage);
} else if (action === "check_balance") {
  // Low stakes. Showing the wrong screen is recoverable.
  showBalance(accountId);
} else if (action === "approve_transfer") {
  if (confidence > 0.9) confirmThenExecute(accountId); // High stakes, high confidence.
  else askUserToConfirm(accountId); // High stakes, moderate confidence. Verify first.
}
```

> Start with conservative thresholds, test on your own data, and adjust. You can calibrate by plotting confidence against accuracy.

## How confidence is calculated

The formulas are exact, and every answer includes its full `probabilities`, so you can recompute confidence or substitute your own statistic.

### Noul

No `confidence` is returned. For a value on the same scale as Choice confidence:

$$\text{confidence} = |2p - 1|$$

**Python**

```python
def noul_confidence(p: float) -> float:
    return abs(2 * p - 1)
```

**TypeScript**

```ts
const noulConfidence = (p: number): number => Math.abs(2 * p - 1);
```

### Choice

For `n` options, where `p_max` is the top probability:

$$\text{confidence} = \frac{p_{\max} - \frac{1}{n}}{1 - \frac{1}{n}}$$

Only the top probability counts, so `(0.6, 0.3, 0.1)` and `(0.6, 0.2, 0.2)` both give confidence `0.4`.

**Python**

```python
def choice_confidence(probabilities: list[float]) -> float:
    n = len(probabilities)
    return (max(probabilities) - 1 / n) / (1 - 1 / n)


choice_confidence(list(answer.probabilities.values()))
```

**TypeScript**

<!-- ts-check:
import type { ChoiceResponse } from "@typesafe-ai/sdk";
declare const answer: ChoiceResponse;
-->
```ts
function choiceConfidence(probabilities: number[]): number {
  const n = probabilities.length;
  return (Math.max(...probabilities) - 1 / n) / (1 - 1 / n);
}

choiceConfidence(Object.values(answer.probabilities));
```

Two simpler alternatives that often work well:

**Python**

```python
probs = sorted(answer.probabilities.values(), reverse=True)

top_probability = probs[0]                    # "how likely is the selected option" (set per question)
top_to_second   = probs[0] / max(probs[1], 1e-9)  # how clearly #1 beats the runner-up
```

**TypeScript**

<!-- ts-check:
import type { ChoiceResponse } from "@typesafe-ai/sdk";
declare const answer: ChoiceResponse;
-->
```ts
const probs = Object.values(answer.probabilities).sort((a, b) => b - a);

const topProbability = probs[0];                         // set the threshold per question
const topToSecond = probs[0] / Math.max(probs[1], 1e-9); // how clearly #1 beats the runner-up
```

### Score

Levels are ordered, so probability on a level far from the most likely level `m` lowers confidence more than probability on a neighbor:

$$\text{confidence} = \max\left(0,\ 1 - \frac{\sum_i p_i\,|i - m|}{\text{MAD}_{\text{unif}}}\right),\qquad \text{MAD}_{\text{unif}} = \frac{1}{n}\sum_i\left|i - \frac{n-1}{2}\right|$$

With three levels, `(0, 0.5, 0.5)` gives 0.25 (torn between neighbors) and `(0.5, 0, 0.5)` gives 0 (torn between the two ends).

**Python**

```python
def score_confidence(probabilities: list[float]) -> float:
    n = len(probabilities)
    m = probabilities.index(max(probabilities))
    spread = sum(p * abs(i - m) for i, p in enumerate(probabilities))
    even_spread = sum(abs(i - (n - 1) / 2) for i in range(n)) / n
    return max(0.0, 1 - spread / even_spread)


levels = sorted(answer.probabilities)
score_confidence([answer.probabilities[level] for level in levels])
```

**TypeScript**

<!-- ts-check:
import type { ScoreResponse } from "@typesafe-ai/sdk";
declare const answer: ScoreResponse;
-->
```ts
function scoreConfidence(probabilities: number[]): number {
  const n = probabilities.length;
  const m = probabilities.indexOf(Math.max(...probabilities));
  const spread = probabilities.reduce((sum, p, i) => sum + p * Math.abs(i - m), 0);
  let evenSpread = 0;
  for (let i = 0; i < n; i++) evenSpread += Math.abs(i - (n - 1) / 2);
  evenSpread /= n;
  return Math.max(0, 1 - spread / evenSpread);
}

const levels = Object.keys(answer.probabilities).map(Number).sort((a, b) => a - b);
scoreConfidence(levels.map((level) => answer.probabilities[level]));
```

Worked example: `bug_severity` has probabilities `(0, 0.57, 0.43)`. Then `m = 1`, the spread is `0.43`, and `MAD_unif = 2/3`, so confidence is `1 - 0.43 / (2/3) ≈ 0.35`.

## Diagnosing low confidence

Low confidence is information about your question or your state, not noise. Look at **where** the probability went:

| What `probabilities` looks like | Likely cause | Fix |
|---|---|---|
| Two options share most of the mass | The options overlap | Sharpen both descriptions so their boundary is explicit |
| Mass spread over every option | None of them fits, or the state lacks the evidence | Add an `other` / `none` option; put the evidence in `state` and name it in the question |
| Score mass on both ends | The question measures two things at once | Split it into two questions |
| Score mass on two neighboring levels | The levels are vague | Give each level a structured description with examples |
| Noul near 0.5 | Ambiguous or degree-type question | Tighten the yes/no boundary, or use a Score |

**Python**

```python
from typesafe_sdk import Choice, TypeSafeClient

client = TypeSafeClient()

response = client.system_one(
    state={"message": "The app crashes when I try to pay my invoice."},
    questions={
        "team": Choice(
            instructions="Which team should handle `message`?",
            criteria={
                "billing": "Payments, invoices, refunds",
                "technical": "Bugs, crashes, outages",
                "other": "Anything that fits neither team",
            },
        ),
    },
)

answer = response.choices["team"]
ranked = sorted(answer.probabilities.items(), key=lambda kv: kv[1], reverse=True)
(top, p1), (runner_up, p2) = ranked[0], ranked[1]

if answer.confidence < 0.5:
    if p1 + p2 > 0.9:
        print(f"Torn between {top!r} and {runner_up!r}: make their boundary explicit in criteria")
    elif top == "other":
        print("No option fits: add the missing option")
    else:
        print("Mass is spread out: check that the state contains the evidence the question needs")
```

**TypeScript**

<!-- ts-check run -->
```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const { answers } = await client.systemOne({
  state: { message: "The app crashes when I try to pay my invoice." },
  questions: {
    team: choice("Which team should handle `message`?", {
      billing: "Payments, invoices, refunds",
      technical: "Bugs, crashes, outages",
      other: "Anything that fits neither team",
    }),
  },
});

const answer = answers.team;
const [[top, p1], [runnerUp, p2]] = Object.entries(answer.probabilities).sort((a, b) => b[1] - a[1]);

if (answer.confidence < 0.5) {
  if (p1 + p2 > 0.9) console.log(`Torn between "${top}" and "${runnerUp}": make their boundary explicit in criteria`);
  else if (top === "other") console.log("No option fits: add the missing option");
  else console.log("Mass is spread out: check that the state contains the evidence the question needs");
}
```

## What confidence does and doesn't tell you

- **It measures how concentrated the distribution is,** not whether the answer is correct. A confidently wrong answer is possible, typically when the question is written ambiguously or the state is adversarial.
- **Thresholds don't transfer.** A threshold tuned on one question, model version, or language doesn't carry over to another. Calibrate per question on labeled examples, and pin the model version you tuned against ([Models → Aliases](12-models.md#aliases)).
- **English gives the best calibration.** For other languages, measure accuracy against confidence on your own data before trusting a threshold ([Models → Language support](12-models.md#language-support-and-calibrating-thresholds)).
- **It isn't authorization.** A confident "approve_transfer" is a reading of the text, not permission. Keep permission checks in code.

## When *not* to use confidence thresholds

If you only need the best option, take `choice` (the argmax). If you have a particular statistical method in mind, work from `probabilities` directly. Not every answer needs a confidence gate.

---

[← Advanced: structure](04-primitives/advanced-structure.md) · Next: [6. How to build →](06-building-with-typesafe.md)
