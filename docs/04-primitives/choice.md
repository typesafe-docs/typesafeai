# 4.1 Choice

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/primitives/choice>

Use a **Choice** when the answer is one of a fixed set of options with no order: which team handles a ticket, which category a product belongs to, which language a snippet is written in.

```text
"What programming language is this code written in"
  → options: python, javascript, typescript, go, rust, other

"What type of meeting is this based on the title and description"
  → options: standup, planning, retrospective, one on one, brainstorm, none of the above
```

## Request

| Field | Value |
|---|---|
| `type` | `"choice"` |
| `instructions` | The question (string, object, or array) |
| `criteria` | Map of `option → description`. Use `null` when the name says it all. **Up to 255 options.** |

```json
{
  "state": "My running shoes arrived in the wrong size. Can I swap them for a size 10?",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "returns": "Exchanges, wrong or damaged items",
        "shipping": "Delivery status, delays, lost packages",
        "billing": "Charges, invoices, payment problems"
      }
    }
  }
}
```

Python:

```python
from typesafe_sdk import Choice, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state="My running shoes arrived in the wrong size. Can I swap them for a size 10?",
        questions={
            "department": Choice(
                instructions="Which team should handle this?",
                criteria={
                    "returns": "Exchanges, wrong or damaged items",
                    "shipping": "Delivery status, delays, lost packages",
                    "billing": "Charges, invoices, payment problems",
                },
            ),
        },
    )
    print(response.answers["department"].choice)  # "returns"
```

TypeScript:

```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const { answers } = await client.systemOne({
  state: "My running shoes arrived in the wrong size. Can I swap them for a size 10?",
  questions: {
    department: choice("Which team should handle this?", {
      returns: "Exchanges, wrong or damaged items",
      shipping: "Delivery status, delays, lost packages",
      billing: "Charges, invoices, payment problems",
    }),
  },
});
console.log(answers.department.choice); // "returns" | "shipping" | "billing"
```

## Response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "returns",
      "confidence": 1.0,
      "probabilities": { "shipping": 0.0, "returns": 1.0, "billing": 0.0 }
    }
  },
  "usage": { "input_tokens": 328, "output_tokens": 34 }
}
```

- `choice` is the option with the highest probability.
- `probabilities` is the full distribution and sums to 1.
- `confidence` (0–1) summarizes the spread. A single peak means high confidence and a flat distribution means low. See [Confidence](../05-confidence.md#choice).

> The model sees the option **names and their descriptions**, but never the question ID. Write descriptions that tell the options apart.

## Good practice

- Ask **many** Choice questions in one request.
- Give the **full** list of options rather than a shortlist. Each extra option costs only a few tokens.
- Add an `other` or `none_of_the_above` escape hatch.
- For deep taxonomies, chain Choices level by level. See [Hierarchical classification](../08-cookbooks.md#hierarchical-classification).
- Jev 1.13 can lean toward the **first** option. Reorder the options to check that answers stay consistent.

## A more complex example: five Choices in one call

```json
{
  "state": "Shoes arrived two weeks late and in the wrong size. Also I see two charges of $120 on my card. What are you going to do about this?",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "returns": "Exchanges, wrong or damaged items",
        "shipping": "Delivery status, delays, lost packages",
        "billing": "Charges, invoices, payment problems"
      }
    },
    "return_reason": {
      "type": "choice",
      "instructions": "If the customer wants to return something, why?",
      "criteria": {
        "wrong_size": "The item doesn't fit",
        "wrong_item": "A different product was delivered",
        "damaged": "The item arrived broken or faulty",
        "changed_mind": "The item is fine, the customer no longer wants it",
        "other": "A return reason that fits none of the above"
      }
    },
    "shipping_issue": {
      "type": "choice",
      "instructions": "If this is a shipping problem, which kind is it?",
      "criteria": {
        "not_delivered": "The package never arrived",
        "delayed": "The package is late but still on its way",
        "wrong_address": "The package went to the wrong place",
        "damaged_in_transit": "The package arrived damaged",
        "other": "A shipping problem that fits none of the above"
      }
    },
    "requested_resolution": {
      "type": "choice",
      "instructions": "What does the customer want to happen?",
      "criteria": {
        "exchange": "Swap the item for a different one",
        "refund": "Money back",
        "replacement": "The same item sent again",
        "information": "Just an answer, no action needed"
      }
    },
    "tone": {
      "type": "choice",
      "instructions": "What is the customer's tone?",
      "criteria": { "calm": null, "frustrated": null, "angry": null }
    }
  }
}
```

Response:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department":           { "type": "choice", "choice": "returns",    "confidence": 0.42, "probabilities": { "shipping": 0.04, "billing": 0.35, "returns": 0.61 } },
    "return_reason":        { "type": "choice", "choice": "wrong_size", "confidence": 1.0,  "probabilities": { "other": 0.0, "wrong_size": 1.0, "changed_mind": 0.0, "damaged": 0.0, "wrong_item": 0.0 } },
    "shipping_issue":       { "type": "choice", "choice": "delayed",    "confidence": 0.67, "probabilities": { "wrong_address": 0.0, "other": 0.26, "not_delivered": 0.0, "damaged_in_transit": 0.0, "delayed": 0.74 } },
    "requested_resolution": { "type": "choice", "choice": "refund",     "confidence": 0.2,  "probabilities": { "replacement": 0.34, "refund": 0.4, "information": 0.02, "exchange": 0.24 } },
    "tone":                 { "type": "choice", "choice": "frustrated", "confidence": 0.76, "probabilities": { "frustrated": 0.84, "angry": 0.16, "calm": 0.0 } }
  },
  "usage": { "input_tokens": 589, "output_tokens": 212 }
}
```

Routing code that reads what it needs and treats low confidence as a reason to **ask rather than act**:

**Python**

```python
from typesafe_sdk import Choice, TypeSafeClient

TRIAGE_QUESTIONS = {
    "department": Choice(
        instructions="Which team should handle this?",
        criteria={
            "returns": "Exchanges, wrong or damaged items",
            "shipping": "Delivery status, delays, lost packages",
            "billing": "Charges, invoices, payment problems",
        },
    ),
    "return_reason": Choice(
        instructions="If the customer wants to return something, why?",
        criteria={
            "wrong_size": "The item doesn't fit",
            "wrong_item": "A different product was delivered",
            "damaged": "The item arrived broken or faulty",
            "changed_mind": "The item is fine, the customer no longer wants it",
            "other": "A return reason that fits none of the above",
        },
    ),
    "shipping_issue": Choice(
        instructions="If this is a shipping problem, which kind is it?",
        criteria={
            "not_delivered": "The package never arrived",
            "delayed": "The package is late but still on its way",
            "wrong_address": "The package went to the wrong place",
            "damaged_in_transit": "The package arrived damaged",
            "other": "A shipping problem that fits none of the above",
        },
    ),
    "requested_resolution": Choice(
        instructions="What does the customer want to happen?",
        criteria={
            "exchange": "Swap the item for a different one",
            "refund": "Money back",
            "replacement": "The same item sent again",
            "information": "Just an answer, no action needed",
        },
    ),
    "tone": Choice(
        instructions="What is the customer's tone?",
        criteria={"calm": None, "frustrated": None, "angry": None},
    ),
}


def triage(ticket: str) -> None:
    with TypeSafeClient() as client:
        response = client.system_one(state=ticket, questions=TRIAGE_QUESTIONS)
    answers = response.answers

    department = answers["department"]
    if department.confidence < 0.3:
        # Not clear which team to send to. Let a person decide.
        send_to_manual_triage(ticket)
        return

    if department.choice == "returns":
        assign(ticket, team="returns", issue=answers["return_reason"].choice)
    elif department.choice == "shipping":
        assign(ticket, team="shipping", issue=answers["shipping_issue"].choice)
    else:
        assign(ticket, team="billing")

    # A second team with a real share of the probability gets a copy
    for team, probability in department.probabilities.items():
        if team != department.choice and probability > 0.25:
            notify(ticket, team=team)

    resolution = answers["requested_resolution"]
    if resolution.confidence < 0.5:
        # The customer hasn't said what they want. Ask, don't guess.
        ask_customer_what_they_want(ticket)
    elif resolution.choice == "refund":
        flag_for_refund_approval(ticket)

    if answers["tone"].choice == "angry":
        flag_for_senior_agent(ticket)
```

**TypeScript**

<!-- ts-check:
declare function sendToManualTriage(t: string): void;
declare function assign(t: string, o: { team: string; issue?: string }): void;
declare function notify(t: string, o: { team: string }): void;
declare function askCustomerWhatTheyWant(t: string): void;
declare function flagForRefundApproval(t: string): void;
declare function flagForSeniorAgent(t: string): void;
-->
```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const TRIAGE_QUESTIONS = {
  department: choice("Which team should handle this?", {
    returns: "Exchanges, wrong or damaged items",
    shipping: "Delivery status, delays, lost packages",
    billing: "Charges, invoices, payment problems",
  }),
  return_reason: choice("If the customer wants to return something, why?", {
    wrong_size: "The item doesn't fit",
    wrong_item: "A different product was delivered",
    damaged: "The item arrived broken or faulty",
    changed_mind: "The item is fine, the customer no longer wants it",
    other: "A return reason that fits none of the above",
  }),
  shipping_issue: choice("If this is a shipping problem, which kind is it?", {
    not_delivered: "The package never arrived",
    delayed: "The package is late but still on its way",
    wrong_address: "The package went to the wrong place",
    damaged_in_transit: "The package arrived damaged",
    other: "A shipping problem that fits none of the above",
  }),
  requested_resolution: choice("What does the customer want to happen?", {
    exchange: "Swap the item for a different one",
    refund: "Money back",
    replacement: "The same item sent again",
    information: "Just an answer, no action needed",
  }),
  tone: choice("What is the customer's tone?", { calm: null, frustrated: null, angry: null }),
};

const client = new TypeSafeClient();

async function triage(ticket: string): Promise<void> {
  const { answers } = await client.systemOne({ state: ticket, questions: TRIAGE_QUESTIONS });

  const department = answers.department;
  if (department.confidence < 0.3) {
    // Not clear which team to send to. Let a person decide.
    return sendToManualTriage(ticket);
  }

  if (department.choice === "returns") {
    assign(ticket, { team: "returns", issue: answers.return_reason.choice });
  } else if (department.choice === "shipping") {
    assign(ticket, { team: "shipping", issue: answers.shipping_issue.choice });
  } else {
    assign(ticket, { team: "billing" });
  }

  // A second team with a real share of the probability gets a copy
  for (const [team, probability] of Object.entries(department.probabilities)) {
    if (team !== department.choice && probability > 0.25) notify(ticket, { team });
  }

  const resolution = answers.requested_resolution;
  if (resolution.confidence < 0.5) {
    // The customer hasn't said what they want. Ask, don't guess.
    askCustomerWhatTheyWant(ticket);
  } else if (resolution.choice === "refund") {
    flagForRefundApproval(ticket);
  }

  if (answers.tone.choice === "angry") flagForSeniorAgent(ticket);
}
```

For this ticket, the code assigns to **returns** with issue `wrong_size`, copies **billing** (its 0.35 share is above 0.25), and **asks the customer** what they want because resolution confidence is 0.20, below 0.5. The `shipping_issue` answer goes unused, as speculative answers often do.

## Structured (contrastive) criteria

When two options keep getting mixed up, describe each one with an object: what it covers, what it's **not** for, and some examples.

```json
{
  "state": "I sent the shoes back a week ago. When do I get my money?",
  "model": "jev-latest",
  "questions": {
    "return_topic": {
      "type": "choice",
      "instructions": {
        "question": "Which returns topic is the customer asking about?",
        "focus": "Classify the information the customer wants."
      },
      "criteria": {
        "return_policy": {
          "what": "Whether and how an item can be returned",
          "not_for": "Progress of a return already sent",
          "examples": ["Can I return shoes I've worn once?", "How long do I have to return an order?"]
        },
        "return_status": {
          "what": "Progress of a return already sent",
          "not_for": "Whether and how an item can be returned",
          "examples": ["Has my return arrived yet?", "When will my refund be paid?"]
        }
      }
    }
  }
}
```

→ `return_status` with confidence `1.0`.

> Field names like `question`, `focus`, `what`, `not_for`, and `examples` aren't reserved. You choose them. The model reads the names along with the values, so keep them short and descriptive, and use the same names on every option.

---

[← Primitives](README.md) · Next: [Score →](score.md)
