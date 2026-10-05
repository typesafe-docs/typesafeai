# 3. State

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/concepts/state>

**State** is the content you ask a System One model to evaluate: a support message, a passage of text, or the current state of your application. It goes in the `state` field next to your questions. Every question in a request sees the **same** state and is evaluated **independently**.

## Formats

| Format | Useful for | Example |
|---|---|---|
| String | A single message, article, or passage | `"My card was charged twice."` |
| Object | Named fields, related records, application state | `{"message": "My card was charged twice.", "order_id": "A-104"}` |
| Array | A sequence of messages or records | `["Hi", "My customer number is TS1337.", "My card was charged twice."]` |

**Use an object for most requests.** Named fields keep each part of the state labeled and keep the relationships between parts clear.

**Python**

```python
# String
state = "My card was charged twice."

# Object
state = {"message": "My card was charged twice.", "order_id": "A-104"}

# Array
state = ["Hi", "My customer number is TS1337.", "My card was charged twice."]

client.system_one(state=state, questions=...)
```

**TypeScript**

<!-- ts-check:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient;
const questions = { q: noul("Is this about billing?") };
-->
```ts
// String
const text = "My card was charged twice.";

// Object
const record = { message: "My card was charged twice.", order_id: "A-104" };

// Array
const messages = ["Hi", "My customer number is TS1337.", "My card was charged twice."];

await client.systemOne({ state: record, questions });
```

> **Text only.** State must be a string, a JSON object, or an array of text values. Images, audio, and video aren't supported yet. English is the primary training language. Other languages, including CJK scripts, work but are currently less accurate.

## A structured state

Think of the state as the briefing you'd hand a panel of experts before asking for their judgment.

```json
{
  "ticket": {
    "subject": "Duplicate charge",
    "messages": [
      {"from": "customer", "text": "I was charged twice for order A-104. Please refund the duplicate."},
      {"from": "support",  "text": "We are checking the charges."}
    ]
  },
  "order": {
    "id": "A-104",
    "charges": [
      {"amount_usd": 49, "status": "captured"},
      {"amount_usd": 49, "status": "captured"}
    ]
  },
  "refund_policy": "Duplicate charges are eligible for a refund."
}
```

That's **one** state, even though it holds a conversation, an order, and a policy. Keep related information together when the decision depends on comparing the parts.

## Point questions at specific fields

To aim a question at one part of the state, reference it with a **backticked dot-and-index path**:

**Python**

```python
questions = {
    "refund_requested": {
        "type": "noul",
        "instructions": "Does `ticket.messages[0].text` request a refund?",
    },
    "policy_supports_refund": {
        "type": "noul",
        "instructions": (
            "Does `refund_policy` support the refund requested "
            "in `ticket.messages[0].text`, given `order.charges`?"
        ),
    },
}
```

**TypeScript**

```ts
import { noul } from "@typesafe-ai/sdk";

const questions = {
  refund_requested: noul("Does `ticket.messages[0].text` request a refund?"),
  policy_supports_refund: noul(
    "Does `refund_policy` support the refund requested in `ticket.messages[0].text`, given `order.charges`?",
  ),
};
```

## Keep content separate from questions

The **state** holds the content and supporting facts. The **questions** define the judgments. For example, put the refund request and the policy in the state, then ask whether a refund was requested and whether the policy supports it.

## Send only what the question needs

Accuracy drops as the state fills up with material unrelated to the decision. Jev suffers from context rot. Filter in code first:

**Python**

```python
def triage(ticket, customer):
    open_orders = [o for o in customer["orders"] if o["status"] != "delivered"]

    state = {
        "ticket":   {"message": ticket["message"], "sender": ticket["sender"]},
        "customer": {"plan": customer["plan"], "open_orders": open_orders},
    }
    return client.system_one(state=state, questions=QUESTIONS)
```

**TypeScript**

<!-- ts-check:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient;
const QUESTIONS = { q: noul("x") };
type Ticket = { message: string; sender: string };
type Customer = { plan: string; orders: { id: string; status: string }[] };
-->
```ts
async function triage(ticket: Ticket, customer: Customer) {
  const openOrders = customer.orders.filter((o) => o.status !== "delivered");

  const state = {
    ticket: { message: ticket.message, sender: ticket.sender },
    customer: { plan: customer.plan, open_orders: openOrders },
  };
  return client.systemOne({ state, questions: QUESTIONS });
}
```

Limits: 64k tokens per request (state plus all questions), and 32k tokens for the state plus the single longest question. See [Models](12-models.md).

---

[← 2. Quick start](02-quickstart.md) · Next: [4. Primitives →](04-primitives/README.md)
