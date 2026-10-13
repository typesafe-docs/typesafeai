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

## What goes in state vs. in the question

The **state** holds the content and supporting facts: the message, the records, the policy. The **question** holds only the judgment you want made, and it can name parts of the state by path. Keep the same split for a yes/no Noul as for Choice and Score questions:

| Put it in `state` | Put it in the question (`instructions`, `criteria`) |
|---|---|
| The text being judged (message, document, transcript) | The single yes/no judgment, phrased so "yes" is unambiguous |
| Reference material the judgment depends on (policy, product facts, prior messages) | What counts as yes and as no, including boundary cases (`criteria`) |
| Data that changes on every request | Wording that stays the same across requests |

Question IDs aren't sent to the model, so nothing you put in a key is seen.

**Python**

```python
from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient

client = TypeSafeClient()

# ❌ Content baked into the question: nothing is reusable, and the model can't tell data from the ask
client.system_one(
    state="",
    questions={"refund": Noul(instructions="The customer wrote 'I was charged twice for order A-104'. Our policy refunds duplicate charges. Is a refund due?")},
)

# ✅ Content in state, one judgment in the question, boundary cases in criteria
response = client.system_one(
    state={
        "message": "I was charged twice for order A-104.",
        "refund_policy": "Duplicate charges on the same order are refunded in full.",
    },
    questions={
        "refund_due": Noul(
            instructions="Does `refund_policy` entitle the customer to a refund for the problem described in `message`?",
            criteria=NoulCriteria(
                true="The message describes a case the policy explicitly covers",
                false="The policy doesn't cover it, or the message describes no charge problem",
            ),
        ),
    },
)
print(response.nouls["refund_due"].noul)  # P(yes): near 1 yes, near 0 no, near 0.5 unsure
```

**TypeScript**

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

// ❌ Content baked into the question: nothing is reusable, and the model can't tell data from the ask
await client.systemOne({
  state: "",
  questions: {
    refund: noul("The customer wrote 'I was charged twice for order A-104'. Our policy refunds duplicate charges. Is a refund due?"),
  },
});

// ✅ Content in state, one judgment in the question, boundary cases in criteria
const { answers } = await client.systemOne({
  state: {
    message: "I was charged twice for order A-104.",
    refund_policy: "Duplicate charges on the same order are refunded in full.",
  },
  questions: {
    refund_due: noul("Does `refund_policy` entitle the customer to a refund for the problem described in `message`?", {
      true: "The message describes a case the policy explicitly covers",
      false: "The policy doesn't cover it, or the message describes no charge problem",
    }),
  },
});
console.log(answers.refund_due.noul); // P(yes): near 1 yes, near 0 no, near 0.5 unsure
```

**Where do examples go?** There's no separate few-shot field. TypeSafe's guidance is to encode domain rules and boundary cases in `instructions` and `criteria`, so describe the borderline cases there (as in the `criteria` above). Put reference material that the judgment is *about* in `state`. See [Models → Customizing Jev](12-models.md#customizing-jev).

**A Noul near 0.5** means yes and no are about equally likely: the model can't decide from what it was given. It doesn't mean "partly yes". Usually the question is ambiguous or a matter of degree, or the state lacks the evidence. See [FAQ: What does a Noul probability near 0.5 mean?](15-faq.md#what-does-a-noul-probability-near-05-mean)

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
