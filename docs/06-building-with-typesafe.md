# 6. How to build with TypeSafe

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/concepts/how-to-build-with-system-one>

System One is for building **AI-powered software**, not agents. It doesn't generate code or pick its own next step. It's a set of AI primitives that embed into your software: code stays in control, and the model handles common-sense judgments over unstructured data.

> **Summary:** build a normal software workflow and insert System One only where you need AI.
> - Keep control flow, deterministic rules, and side effects in code.
> - Break broad judgments into narrow, typed questions with explicit instructions and criteria.
> - Give each question only the context it needs.
> - Use probabilities and confidence to decide whether to act, request review, or escalate.
> - Ask independent questions together, then combine their answers in code.

## What makes System One composable

| Property | Why it matters |
|---|---|
| **Structured** | Outputs conform to your types, so nothing is parsed out of prose |
| **Parallel** | Questions are evaluated independently, with no hidden cross-talk |
| **Comparable** | Outputs can be sorted and plugged into `if` statements and thresholds |
| **Fast** | About 100 ms for most queries |
| **Calibrated** | RLCD probabilities express uncertainty instead of overconfidence |
| **Self-consistent** | Answers stay stable across repeated runs |

## The eight steps

### 1. Use code when you can

**Python**

```python
days_overdue = (today - invoice.due_date).days

if days_overdue > 30:
    route_to_collections(invoice)
```

**TypeScript**

<!-- ts-check:
declare const today: Date;
declare const invoice: { dueDate: Date };
declare function routeToCollections(i: unknown): void;
-->
```ts
const MS_PER_DAY = 24 * 60 * 60 * 1000;
const daysOverdue = Math.floor((today.getTime() - invoice.dueDate.getTime()) / MS_PER_DAY);

if (daysOverdue > 30) routeToCollections(invoice);
```

Avoid agent `while` loops when an ordinary workflow can express the same behavior.

### 2. Decompose the input state

Send only the context that's relevant. Don't rely on knowledge in the model's weights when your own knowledge base can supply current information.

```json
{
  "state": {
    "ticket_message": "My flight was cancelled. Can I get a refund?",
    "refund_policy": "Cancelled flights are eligible for a full refund."
  },
  "model": "jev-latest",
  "questions": {
    "policy_supports_refund": {
      "type": "noul",
      "instructions": "Does the refund policy support the refund requested in the ticket?"
    }
  }
}
```

### 3. Use structure in the input state

Use nested JSON for both `state` and `questions`. Point a question at one specific value with a **backticked dot-and-index path**, such as `` `support.tickets[0].message` ``. Include the backticks inside the question text.

```json
{
  "state": {
    "support": {
      "tickets": [
        {
          "message": "I was charged twice for order A-104."
        },
        {
          "message": "How do I reset my password?"
        }
      ]
    },
    "commerce": {
      "orders": [
        {
          "id": "A-104",
          "charges": [
            {
              "amount_usd": 49,
              "status": "captured"
            },
            {
              "amount_usd": 49,
              "status": "captured"
            }
          ]
        }
      ]
    },
    "account": {
      "security": {
        "password_reset": "Email a reset link to the address on file."
      }
    }
  },
  "model": "jev-latest",
  "questions": {
    "duplicate_charge": {
      "type": "noul",
      "instructions": "Do `support.tickets[0].message` and `commerce.orders[0].charges` indicate a duplicate charge?"
    },
    "password_reset_supported": {
      "type": "noul",
      "instructions": "Can `account.security.password_reset` resolve the request in `support.tickets[1].message`?"
    }
  }
}
```

The same request with the Python SDK:

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

state = {
    "support": {
        "tickets": [
            {
                "message": "I was charged twice for order A-104."
            },
            {
                "message": "How do I reset my password?"
            }
        ]
    },
    "commerce": {
        "orders": [
            {
                "id": "A-104",
                "charges": [
                    {
                        "amount_usd": 49,
                        "status": "captured"
                    },
                    {
                        "amount_usd": 49,
                        "status": "captured"
                    }
                ]
            }
        ]
    },
    "account": {
        "security": {
            "password_reset": "Email a reset link to the address on file."
        }
    }
}

with TypeSafeClient() as client:
    answers = client.system_one(
        state=state,
        questions={
            "duplicate_charge": Noul(
                instructions="Do `support.tickets[0].message` and `commerce.orders[0].charges` indicate a duplicate charge?",
            ),
            "password_reset_supported": Noul(
                instructions="Can `account.security.password_reset` resolve the request in `support.tickets[1].message`?",
            ),
        },
    ).answers

if answers["duplicate_charge"].noul > 0.8:
    open_refund_case("A-104")
```

**TypeScript**

<!-- ts-check run:
declare function openRefundCase(id: string): void;
-->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const state = {
  support: {
    tickets: [{ message: "I was charged twice for order A-104." }, { message: "How do I reset my password?" }],
  },
  commerce: {
    orders: [{ id: "A-104", charges: [{ amount_usd: 49, status: "captured" }, { amount_usd: 49, status: "captured" }] }],
  },
  account: { security: { password_reset: "Email a reset link to the address on file." } },
};

const { answers } = await new TypeSafeClient().systemOne({
  state,
  questions: {
    duplicate_charge: noul(
      "Do `support.tickets[0].message` and `commerce.orders[0].charges` indicate a duplicate charge?",
    ),
    password_reset_supported: noul(
      "Can `account.security.password_reset` resolve the request in `support.tickets[1].message`?",
    ),
  },
});

if (answers.duplicate_charge.noul > 0.8) openRefundCase("A-104");
```

### 4. Decompose the questions ⭐ (the most important step)

Ask the most explicit, narrow, specific, atomic questions you can. Break a complex or loosely defined question into separate questions that each evaluate one property.

> ℹ️ **This is probably the most important idea in this guide.** A broad question hides several judgments behind one answer. Atomic questions expose those judgments so you can inspect them, tune them, and combine them in code.

#### Example: decompose spam detection

**One broad question (bad)**

```json
{
  "state": {
    "message": {
      "sender": {
        "display_name": "Acme Payroll",
        "email": "rewards@claim-bonus.example"
      },
      "subject": "Urgent: claim your employee bonus",
      "body": "You have been selected for a $1,000 bonus. Confirm your payroll password today to receive it.",
      "links": [
        {
          "text": "Claim bonus",
          "url": "http://claim-bonus.example/acme"
        }
      ]
    }
  },
  "model": "jev-latest",
  "questions": {
    "is_spam": {
      "type": "noul",
      "instructions": "Is `message` spam?"
    }
  }
}
```

**Decomposed questions (good)**: the same state, six atomic Nouls

```json
{
  "questions": {
    "requests_credentials": {
      "type": "noul",
      "instructions": "Does `message.body` ask the recipient to provide a password or other login credential?"
    },
    "offers_unexpected_reward": {
      "type": "noul",
      "instructions": "Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"
    },
    "creates_time_pressure": {
      "type": "noul",
      "instructions": "Does `message.subject` or `message.body` pressure the recipient to act quickly?"
    },
    "sender_identity_mismatch": {
      "type": "noul",
      "instructions": "Does the organization named in `message.sender.display_name` conflict with the domain in `message.sender.email`?"
    },
    "link_domain_mismatch": {
      "type": "noul",
      "instructions": "Does the domain in `message.links[0].url` conflict with the organization named in `message.sender.display_name`?"
    },
    "disguises_link_destination": {
      "type": "noul",
      "instructions": "Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"
    }
  }
}
```

In Python, with the weights in code:

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

SPAM_QUESTIONS = {
    "requests_credentials": Noul(instructions="Does `message.body` ask the recipient to provide a password or other login credential?"),
    "offers_unexpected_reward": Noul(instructions="Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"),
    "creates_time_pressure": Noul(instructions="Does `message.subject` or `message.body` pressure the recipient to act quickly?"),
    "sender_identity_mismatch": Noul(instructions="Does the organization named in `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
    "link_domain_mismatch": Noul(instructions="Does the domain in `message.links[0].url` conflict with the organization named in `message.sender.display_name`?"),
    "disguises_link_destination": Noul(instructions="Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"),
}

SPAM_WEIGHTS = {
    "requests_credentials": 0.30,
    "sender_identity_mismatch": 0.20,
    "link_domain_mismatch": 0.20,
    "offers_unexpected_reward": 0.10,
    "creates_time_pressure": 0.10,
    "disguises_link_destination": 0.10,
}


def spam_risk(message: dict) -> tuple[float, dict[str, float]]:
    with TypeSafeClient() as client:
        answers = client.system_one(state={"message": message}, questions=SPAM_QUESTIONS).answers
    signals = {k: answers[k].noul for k in SPAM_QUESTIONS}
    return sum(SPAM_WEIGHTS[k] * v for k, v in signals.items()), signals  # keep the signals for review
```

**TypeScript**

<!-- ts-check:
import type { JsonValue } from "@typesafe-ai/sdk";
-->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const SPAM_QUESTIONS = {
  requests_credentials: noul("Does `message.body` ask the recipient to provide a password or other login credential?"),
  offers_unexpected_reward: noul("Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"),
  creates_time_pressure: noul("Does `message.subject` or `message.body` pressure the recipient to act quickly?"),
  sender_identity_mismatch: noul("Does the organization named in `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
  link_domain_mismatch: noul("Does the domain in `message.links[0].url` conflict with the organization named in `message.sender.display_name`?"),
  disguises_link_destination: noul("Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"),
};
type Signal = keyof typeof SPAM_QUESTIONS;

const SPAM_WEIGHTS: Record<Signal, number> = {
  requests_credentials: 0.3,
  sender_identity_mismatch: 0.2,
  link_domain_mismatch: 0.2,
  offers_unexpected_reward: 0.1,
  creates_time_pressure: 0.1,
  disguises_link_destination: 0.1,
};

async function spamRisk(message: Record<string, JsonValue>): Promise<[number, Record<Signal, number>]> {
  const { answers } = await new TypeSafeClient().systemOne({ state: { message }, questions: SPAM_QUESTIONS });
  const signals = Object.fromEntries(
    (Object.keys(SPAM_QUESTIONS) as Signal[]).map((k) => [k, answers[k].noul]),
  ) as Record<Signal, number>;
  const risk = (Object.keys(signals) as Signal[]).reduce((sum, k) => sum + SPAM_WEIGHTS[k] * signals[k], 0);
  return [risk, signals]; // keep the signals for review
}
```

#### Example: verify a tool-call trace

**One broad question (bad)**

```json
{
  "state": {
    "request": {
      "text": "What's the weather in Seattle tomorrow in Fahrenheit?",
      "location": "Seattle, WA",
      "date": "2026-09-03",
      "unit": "fahrenheit"
    },
    "available_tools": {
      "geocode_city": {
        "description": "Resolve a city to latitude and longitude.",
        "parameters": {
          "city": "string"
        }
      },
      "get_weather": {
        "description": "Get the forecast for coordinates and a date.",
        "parameters": {
          "latitude": "number",
          "longitude": "number",
          "date": "YYYY-MM-DD",
          "unit": [
            "fahrenheit",
            "celsius"
          ]
        }
      }
    },
    "trace": {
      "tool_calls": [
        {
          "id": "call_1",
          "name": "geocode_city",
          "arguments": {
            "city": "Seattle, WA"
          }
        },
        {
          "id": "call_2",
          "name": "get_weather",
          "arguments": {
            "latitude": 47.6062,
            "longitude": -122.3321,
            "date": "2026-09-03",
            "unit": "celsius"
          }
        }
      ],
      "tool_results": [
        {
          "tool_call_id": "call_1",
          "output": {
            "latitude": 47.6062,
            "longitude": -122.3321
          }
        }
      ]
    }
  },
  "model": "jev-latest",
  "questions": {
    "tool_calls_are_correct": {
      "type": "noul",
      "instructions": "Is `trace.tool_calls` correct for `request` and `available_tools`?"
    }
  }
}
```

**Decomposed questions (good)**: the same state, nine atomic checks

```json
{
  "questions": {
    "geocode_tool_is_relevant": {
      "type": "noul",
      "instructions": "Is `trace.tool_calls[0].name` an appropriate tool for resolving `request.location`?"
    },
    "geocode_location_matches": {
      "type": "noul",
      "instructions": "Does `trace.tool_calls[0].arguments.city` match `request.location`?"
    },
    "geocode_arguments_match_schema": {
      "type": "noul",
      "instructions": "Does `trace.tool_calls[0].arguments` conform to `available_tools.geocode_city.parameters`?"
    },
    "geocode_result_matches_call": {
      "type": "noul",
      "instructions": "Does `trace.tool_results[0].tool_call_id` match `trace.tool_calls[0].id`?"
    },
    "weather_tool_is_relevant": {
      "type": "noul",
      "instructions": "Is `trace.tool_calls[1].name` an appropriate tool for answering `request.text`?"
    },
    "weather_arguments_match_schema": {
      "type": "noul",
      "instructions": "Does `trace.tool_calls[1].arguments` conform to `available_tools.get_weather.parameters`?"
    },
    "weather_uses_geocoded_coordinates": {
      "type": "noul",
      "instructions": "Do the coordinates in `trace.tool_calls[1].arguments` match those in `trace.tool_results[0].output`?"
    },
    "weather_date_matches": {
      "type": "noul",
      "instructions": "Does `trace.tool_calls[1].arguments.date` match `request.date`?"
    },
    "weather_unit_matches": {
      "type": "noul",
      "instructions": "Does `trace.tool_calls[1].arguments.unit` match `request.unit`?"
    }
  }
}
```

> In this trace, `get_weather` was called with `"unit": "celsius"` but the user asked for Fahrenheit. The broad question has to fold that one defect into a single number. The decomposed version tells you exactly which check failed (`weather_unit_matches`).

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

TRACE_CHECKS = {
    "geocode_tool_is_relevant": Noul(instructions="Is `trace.tool_calls[0].name` an appropriate tool for resolving `request.location`?"),
    "geocode_location_matches": Noul(instructions="Does `trace.tool_calls[0].arguments.city` match `request.location`?"),
    "geocode_arguments_match_schema": Noul(instructions="Does `trace.tool_calls[0].arguments` conform to `available_tools.geocode_city.parameters`?"),
    "geocode_result_matches_call": Noul(instructions="Does `trace.tool_results[0].tool_call_id` match `trace.tool_calls[0].id`?"),
    "weather_tool_is_relevant": Noul(instructions="Is `trace.tool_calls[1].name` an appropriate tool for answering `request.text`?"),
    "weather_arguments_match_schema": Noul(instructions="Does `trace.tool_calls[1].arguments` conform to `available_tools.get_weather.parameters`?"),
    "weather_uses_geocoded_coordinates": Noul(instructions="Do the coordinates in `trace.tool_calls[1].arguments` match those in `trace.tool_results[0].output`?"),
    "weather_date_matches": Noul(instructions="Does `trace.tool_calls[1].arguments.date` match `request.date`?"),
    "weather_unit_matches": Noul(instructions="Does `trace.tool_calls[1].arguments.unit` match `request.unit`?"),
}


def failed_checks(trace_state: dict, threshold: float = 0.5) -> list[str]:
    with TypeSafeClient() as client:
        answers = client.system_one(state=trace_state, questions=TRACE_CHECKS).answers
    return [k for k in TRACE_CHECKS if answers[k].noul < threshold]


# -> e.g. ["weather_unit_matches"]: re-run the tool call with unit="fahrenheit"
```

**TypeScript**

```ts
import { noul, TypeSafeClient, type EntryType } from "@typesafe-ai/sdk";

const TRACE_CHECKS = {
  geocode_tool_is_relevant: noul("Is `trace.tool_calls[0].name` an appropriate tool for resolving `request.location`?"),
  geocode_location_matches: noul("Does `trace.tool_calls[0].arguments.city` match `request.location`?"),
  geocode_arguments_match_schema: noul("Does `trace.tool_calls[0].arguments` conform to `available_tools.geocode_city.parameters`?"),
  geocode_result_matches_call: noul("Does `trace.tool_results[0].tool_call_id` match `trace.tool_calls[0].id`?"),
  weather_tool_is_relevant: noul("Is `trace.tool_calls[1].name` an appropriate tool for answering `request.text`?"),
  weather_arguments_match_schema: noul("Does `trace.tool_calls[1].arguments` conform to `available_tools.get_weather.parameters`?"),
  weather_uses_geocoded_coordinates: noul("Do the coordinates in `trace.tool_calls[1].arguments` match those in `trace.tool_results[0].output`?"),
  weather_date_matches: noul("Does `trace.tool_calls[1].arguments.date` match `request.date`?"),
  weather_unit_matches: noul("Does `trace.tool_calls[1].arguments.unit` match `request.unit`?"),
};

async function failedChecks(traceState: EntryType, threshold = 0.5): Promise<string[]> {
  const { answers } = await new TypeSafeClient().systemOne({ state: traceState, questions: TRACE_CHECKS });
  return (Object.keys(TRACE_CHECKS) as (keyof typeof TRACE_CHECKS)[]).filter((k) => answers[k].noul < threshold);
}

// -> e.g. ["weather_unit_matches"]: re-run the tool call with unit: "fahrenheit"
```

### 5. Use structure in the questions

Put the question in one field and the supporting data in others. This helps when:

- The question needs context or examples.
- Part of the question comes from your code, such as a value from a database row.
- Several questions share similar wording.

**Python**

```python
Noul(
    instructions={
        "potential_duplicate": {"name": "John Smith", "location": "Oakland, California", "last_employer": "Google"},
        "question": "Is the resume for the same person as `potential_duplicate`?",
    }
)
```

**TypeScript**

<!-- ts-check:
import { noul } from "@typesafe-ai/sdk";
-->
```ts
noul({
  potential_duplicate: { name: "John Smith", location: "Oakland, California", last_employer: "Google" },
  question: "Is the resume for the same person as `potential_duplicate`?",
});
```

### 6. Ask a lot of questions

Ask many narrow, independent questions about the same state in **one** request. That's how you get the most intelligence per dollar. See [Speculative fan-out](07-patterns.md#speculative-fan-out).

### 7. Combine outputs in code, or feed them to a classical ML model

**Python**

```python
answers = response.answers

# Combine independent signals into one application-specific score.
quality = (
    0.4 * answers["answers_request"].noul
    + 0.4 * answers["citations_are_supported"].noul
    + 0.2 * (1 - answers["contradicts_context"].noul)
)
```

**TypeScript**

<!-- ts-check:
import type { NoulResponse } from "@typesafe-ai/sdk";
declare const answers: { answers_request: NoulResponse; citations_are_supported: NoulResponse; contradicts_context: NoulResponse };
-->
```ts
// Combine independent signals into one application-specific score.
const quality =
  0.4 * answers.answers_request.noul +
  0.4 * answers.citations_are_supported.noul +
  0.2 * (1 - answers.contradicts_context.noul);
```

For learned composition, use the probabilities as features in a downstream model. See the [Autoresearch cookbook](08-cookbooks.md#autoresearch-feature-discovery).

### 8. Route on uncertainty

**Python**

```python
answer = response.answers["card_help_topic"]

if answer.confidence < 0.8:
    route_to_human_review(ticket)
else:
    route_to_handler(answer.choice, ticket)
```

**TypeScript**

<!-- ts-check:
import type { ChoiceResponse } from "@typesafe-ai/sdk";
declare const answers: { card_help_topic: ChoiceResponse<{ get_disposable_virtual_card: string; disposable_card_limits: string }> };
declare const ticket: string;
declare function routeToHumanReview(t: string): void;
declare function routeToHandler(topic: "get_disposable_virtual_card" | "disposable_card_limits", t: string): void;
-->
```ts
const answer = answers.card_help_topic;

if (answer.confidence < 0.8) routeToHumanReview(ticket);
else routeToHandler(answer.choice, ticket);
```

> Decomposing doesn't cost extra round trips. Questions over the same state run in parallel.

---

## Putting it all together: a complete ticket triage workflow

This combines deterministic shortcuts, a minimal structured state, seven atomic questions in one request, a weighted spam score, and confidence gates.

**Python**

```python
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient


def triage_ticket(ticket, customer):
    # Handle deterministic states without calling a model.
    if ticket["status"] == "closed":
        return "no_action"

    open_orders = [
        order for order in customer["orders"] if order["status"] != "delivered"
    ]

    # Include only the structured context needed by the questions below.
    state = {
        "ticket": {
            "message": ticket["message"],
            "sender": ticket["sender"],
            "links": ticket["links"],
        },
        "customer": {
            "plan": customer["plan"],
            "open_orders": open_orders,
        },
        "policy": {
            "sensitive_credentials": ["password", "security code", "API key"],
        },
    }

    # Ask structured, atomic questions together so they run in parallel.
    questions = {
        "topic": Choice(
            instructions={
                "question": "Which team should handle `ticket.message`?",
                "focus": "Classify the customer's primary request.",
            },
            criteria={
                "billing": {
                    "what": "Charges, invoices, refunds, or subscriptions",
                    "not_for": "Order tracking or account access",
                    "examples": ["I was charged twice", "Where is my refund?"],
                },
                "orders": {
                    "what": "Order status, delivery, cancellation, or returns",
                    "not_for": "Charges or account access",
                    "examples": ["Where is my order?", "Cancel my shipment"],
                },
                "account": {
                    "what": "Login, profile, permissions, or security",
                    "not_for": "Charges or order tracking",
                    "examples": ["Reset my password", "I cannot sign in"],
                },
            },
        ),
        "requests_credentials": Noul(
            instructions={
                "question": "Does the message request a sensitive credential?",
                "compare": ["`ticket.message`", "`policy.sensitive_credentials`"],
                "focus": "Look for a request to disclose the credential itself.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Asks the recipient to disclose a listed credential",
                    "examples": ["Reply with your password", "Send us your API key"],
                },
                false={
                    "what": "Does not ask the recipient to disclose a credential",
                    "not_for": "A legitimate instruction to reset a credential",
                    "examples": ["Use this link to reset your password"],
                },
            ),
        ),
        "sender_identity_mismatch": Noul(
            instructions={
                "question": "Does the claimed sender identity conflict with its domain?",
                "compare": ["`ticket.sender.display_name`", "`ticket.sender.email`"],
                "focus": "Compare the named organization with the email domain.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Claims an organization unrelated to the email domain",
                    "examples": ["Acme Payroll sent from claim-bonus.example"],
                },
                false={
                    "what": "The identity and domain agree or make no conflicting claim",
                    "examples": ["Acme Payroll sent from acme.example"],
                },
            ),
        ),
        "unexpected_reward": Noul(
            instructions={
                "question": "Does the message announce an unexpected reward?",
                "inspect": "`ticket.message`",
                "focus": "Look for an unsolicited prize, payment, or reward claim.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Announces an unrequested prize, payment, or reward",
                    "examples": ["You were selected for a $1,000 bonus"],
                },
                false={
                    "what": "Contains no reward claim or discusses an expected payment",
                    "not_for": "A customer asking about a known refund or payroll deposit",
                    "examples": ["When will my approved refund arrive?"],
                },
            ),
        ),
        "refund_requested": Noul(
            instructions={
                "question": "Does the customer explicitly request a refund or credit?",
                "inspect": "`ticket.message`",
                "focus": "Require a requested remedy, not a billing complaint alone.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Directly asks for money back or an account credit",
                    "examples": ["Please refund the duplicate charge"],
                },
                false={
                    "what": "Does not ask for a refund or credit",
                    "not_for": "A complaint or billing question without a requested remedy",
                    "examples": ["Why was I charged twice?"],
                },
            ),
        ),
        "mentions_open_order": Noul(
            instructions={
                "question": "Does the message refer to a supplied open order?",
                "compare": ["`ticket.message`", "`customer.open_orders`"],
                "focus": "Match an order id or other identifying details.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Refers to an open order by id or identifying details",
                    "examples": ["Where is order A-104?"],
                },
                false={
                    "what": "Does not identify any supplied open order",
                    "not_for": "A generic order question with no matching details",
                    "examples": ["How long does shipping usually take?"],
                },
            ),
        ),
        "frustration": Score(
            instructions={
                "question": "How frustrated does the customer appear?",
                "inspect": "`ticket.message`",
                "focus": "Judge expressed frustration, not issue severity.",
            },
            criteria=[
                {"what": "Calm and matter-of-fact", "signals": ["Neutral wording", "No complaint about the experience"]},
                {"what": "Frustrated but civil", "signals": ["Expresses annoyance", "Remains constructive"]},
                {"what": "Very angry or threatening to leave", "signals": ["Hostile language", "Threatens cancellation or churn"]},
            ],
        ),
    }

    with TypeSafeClient() as client:
        response = client.system_one(state=state, questions=questions)

    # Compose independent spam signals with weights controlled by code.
    answers = response.answers
    spam_risk = (
        0.45 * answers["requests_credentials"].noul
        + 0.30 * answers["sender_identity_mismatch"].noul
        + 0.25 * answers["unexpected_reward"].noul
    )

    # Escalate uncertain judgments instead of guessing.
    spam_is_uncertain = 0.4 < spam_risk < 0.6
    if spam_is_uncertain or answers["topic"].confidence < 0.75:
        return route_to_human_review(ticket)
    if spam_risk >= 0.6:
        return quarantine_as_spam(ticket)

    # Let code decide which speculative answers matter on this path.
    if answers["topic"].choice == "billing":
        return route_to_billing(
            ticket,
            refund_requested=answers["refund_requested"].noul >= 0.7,
        )
    if answers["topic"].choice == "orders":
        return route_to_orders(
            ticket,
            mentions_open_order=answers["mentions_open_order"].noul >= 0.7,
        )

    priority = (
        "high"
        if answers["frustration"].confidence >= 0.7
        and answers["frustration"].score >= 1.5
        else "normal"
    )
    return route_to_account_support(ticket, priority=priority)
```

**TypeScript**

<!-- ts-check:
declare function routeToHumanReview(t: unknown): string;
declare function quarantineAsSpam(t: unknown): string;
declare function routeToBilling(t: unknown, o: { refundRequested: boolean }): string;
declare function routeToOrders(t: unknown, o: { mentionsOpenOrder: boolean }): string;
declare function routeToAccountSupport(t: unknown, o: { priority: "high" | "normal" }): string;
-->
```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

type Ticket = {
  status: "open" | "closed";
  message: string;
  sender: { display_name: string; email: string };
  links: string[];
};
type Order = { id: string; status: string };
type Customer = { plan: string; orders: Order[] };

const client = new TypeSafeClient();

export async function triageTicket(ticket: Ticket, customer: Customer) {
  // Handle deterministic states without calling a model.
  if (ticket.status === "closed") return "no_action";

  const openOrders = customer.orders.filter((order) => order.status !== "delivered");

  // Include only the structured context needed by the questions below.
  const state = {
    ticket: { message: ticket.message, sender: ticket.sender, links: ticket.links },
    customer: { plan: customer.plan, open_orders: openOrders },
    policy: { sensitive_credentials: ["password", "security code", "API key"] },
  };

  // Ask structured, atomic questions together so they run in parallel.
  const { answers } = await client.systemOne({
    state,
    questions: {
      topic: choice(
        { question: "Which team should handle `ticket.message`?", focus: "Classify the customer's primary request." },
        {
          billing: {
            what: "Charges, invoices, refunds, or subscriptions",
            not_for: "Order tracking or account access",
            examples: ["I was charged twice", "Where is my refund?"],
          },
          orders: {
            what: "Order status, delivery, cancellation, or returns",
            not_for: "Charges or account access",
            examples: ["Where is my order?", "Cancel my shipment"],
          },
          account: {
            what: "Login, profile, permissions, or security",
            not_for: "Charges or order tracking",
            examples: ["Reset my password", "I cannot sign in"],
          },
        },
      ),
      requests_credentials: noul(
        {
          question: "Does the message request a sensitive credential?",
          compare: ["`ticket.message`", "`policy.sensitive_credentials`"],
          focus: "Look for a request to disclose the credential itself.",
        },
        {
          true: {
            what: "Asks the recipient to disclose a listed credential",
            examples: ["Reply with your password", "Send us your API key"],
          },
          false: {
            what: "Does not ask the recipient to disclose a credential",
            not_for: "A legitimate instruction to reset a credential",
            examples: ["Use this link to reset your password"],
          },
        },
      ),
      sender_identity_mismatch: noul(
        {
          question: "Does the claimed sender identity conflict with its domain?",
          compare: ["`ticket.sender.display_name`", "`ticket.sender.email`"],
          focus: "Compare the named organization with the email domain.",
        },
        {
          true: {
            what: "Claims an organization unrelated to the email domain",
            examples: ["Acme Payroll sent from claim-bonus.example"],
          },
          false: {
            what: "The identity and domain agree or make no conflicting claim",
            examples: ["Acme Payroll sent from acme.example"],
          },
        },
      ),
      unexpected_reward: noul(
        {
          question: "Does the message announce an unexpected reward?",
          inspect: "`ticket.message`",
          focus: "Look for an unsolicited prize, payment, or reward claim.",
        },
        {
          true: {
            what: "Announces an unrequested prize, payment, or reward",
            examples: ["You were selected for a $1,000 bonus"],
          },
          false: {
            what: "Contains no reward claim or discusses an expected payment",
            not_for: "A customer asking about a known refund or payroll deposit",
            examples: ["When will my approved refund arrive?"],
          },
        },
      ),
      refund_requested: noul(
        {
          question: "Does the customer explicitly request a refund or credit?",
          inspect: "`ticket.message`",
          focus: "Require a requested remedy, not a billing complaint alone.",
        },
        {
          true: {
            what: "Directly asks for money back or an account credit",
            examples: ["Please refund the duplicate charge"],
          },
          false: {
            what: "Does not ask for a refund or credit",
            not_for: "A complaint or billing question without a requested remedy",
            examples: ["Why was I charged twice?"],
          },
        },
      ),
      mentions_open_order: noul(
        {
          question: "Does the message refer to a supplied open order?",
          compare: ["`ticket.message`", "`customer.open_orders`"],
          focus: "Match an order id or other identifying details.",
        },
        {
          true: {
            what: "Refers to an open order by id or identifying details",
            examples: ["Where is order A-104?"],
          },
          false: {
            what: "Does not identify any supplied open order",
            not_for: "A generic order question with no matching details",
            examples: ["How long does shipping usually take?"],
          },
        },
      ),
      frustration: score(
        {
          question: "How frustrated does the customer appear?",
          inspect: "`ticket.message`",
          focus: "Judge expressed frustration, not issue severity.",
        },
        [
          { what: "Calm and matter-of-fact", signals: ["Neutral wording", "No complaint about the experience"] },
          { what: "Frustrated but civil", signals: ["Expresses annoyance", "Remains constructive"] },
          { what: "Very angry or threatening to leave", signals: ["Hostile language", "Threatens cancellation or churn"] },
        ],
      ),
    },
  });

  // Compose independent spam signals with weights controlled by code.
  const spamRisk =
    0.45 * answers.requests_credentials.noul +
    0.3 * answers.sender_identity_mismatch.noul +
    0.25 * answers.unexpected_reward.noul;

  // Escalate uncertain judgments instead of guessing.
  const spamIsUncertain = spamRisk > 0.4 && spamRisk < 0.6;
  if (spamIsUncertain || answers.topic.confidence < 0.75) return routeToHumanReview(ticket);
  if (spamRisk >= 0.6) return quarantineAsSpam(ticket);

  // Let code decide which speculative answers matter on this path.
  if (answers.topic.choice === "billing") {
    return routeToBilling(ticket, { refundRequested: answers.refund_requested.noul >= 0.7 });
  }
  if (answers.topic.choice === "orders") {
    return routeToOrders(ticket, { mentionsOpenOrder: answers.mentions_open_order.noul >= 0.7 });
  }

  const priority =
    answers.frustration.confidence >= 0.7 && answers.frustration.score >= 1.5 ? "high" : "normal";
  return routeToAccountSupport(ticket, { priority });
}
```

## Pairing TypeSafe with an LLM (from the smart-home demo)

Source: <https://docs.typesafe.ai/demos/smart-home>

- **Splitting compound requests:** a Noul detects requests with more than one action ("turn off the lights and lock the door"). An LLM splits them into atomic commands, then TypeSafe evaluates each one.
- **Conversational fallback:** when TypeSafe classifies a request as general conversation, the app calls an LLM to write the reply. TypeSafe answers so much faster than the LLM that it adds almost no latency.

*Illustrative sketch:*

**Python**

```python
answers = client.system_one(state=request, questions=SMART_HOME_QUESTIONS).answers

if answers["is_compound"].noul > 0.7:
    for sub_request in llm_split_into_atomic_commands(request):   # LLM generates text
        handle(sub_request)                                        # TypeSafe decides each
elif answers["category"].choice == "conversation":
    return llm_chat_reply(request)
else:
    execute(device=answers["device"].choice, action=answers["light_action"].choice, room=answers["room"].choice)
```

**TypeScript**

<!-- ts-check:
import { choice, noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient;
const SMART_HOME_QUESTIONS = {
  is_compound: noul("Does the request ask for more than one distinct action?"),
  category: choice("What category of request is this?", { smarthome_command: null, conversation: null }),
  device: choice("What type of device is this request targeting?", { lights: null, thermostat: null }),
  light_action: choice("What action should be taken on the lights?", { on: null, off: null }),
  room: choice("Which room is this request targeting?", { kitchen: null, whole_house: null }),
};
declare function llmSplitIntoAtomicCommands(r: string): Promise<string[]>;
declare function llmChatReply(r: string): string;
declare function execute(c: { device: string; action: string; room: string }): void;
-->
```ts
async function handle(request: string): Promise<string | void> {
  const { answers } = await client.systemOne({ state: request, questions: SMART_HOME_QUESTIONS });

  if (answers.is_compound.noul > 0.7) {
    // An LLM splits the text; TypeSafe then decides each atomic command
    for (const subRequest of await llmSplitIntoAtomicCommands(request)) await handle(subRequest);
  } else if (answers.category.choice === "conversation") {
    return llmChatReply(request);
  } else {
    execute({ device: answers.device.choice, action: answers.light_action.choice, room: answers.room.choice });
  }
}
```

---

[← 5. Confidence](05-confidence.md) · Next: [7. Patterns →](07-patterns.md)
