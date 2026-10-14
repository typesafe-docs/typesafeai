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

## Field order and size

**Order.** Both SDKs send object keys in the order you build them (Python dicts and JavaScript objects keep insertion order; integer-like keys in JavaScript come first). The docs don't name state key order as a known failure mode; the documented ordering effect is [Choice option order](12-models.md#8-choice-option-order). Two habits still help:

- Build the state in the **same order on every request**, so answers stay comparable across runs and thresholds you tune keep meaning the same thing.
- Keep related fields together, and refer to them by name in backticks rather than by position ("the second field").

To check whether order moves your answers, send the same state with its keys reversed:

**Python**

```python
from typesafe_sdk import JSONValue, Noul, TypeSafeClient

client = TypeSafeClient()
QUESTIONS = {"refund_due": Noul(instructions="Does `refund_policy` cover the problem in `message`?")}
state: dict[str, JSONValue] = {
    "message": "I was charged twice for order A-104.",
    "order": {"id": "A-104", "charges": [49, 49]},
    "refund_policy": "Duplicate charges on the same order are refunded in full.",
}

forward = client.system_one(state, QUESTIONS).nouls["refund_due"].noul
reverse = client.system_one(dict(reversed(state.items())), QUESTIONS).nouls["refund_due"].noul
print(f"forward {forward:.2f}, reversed {reverse:.2f}, shift {abs(forward - reverse):.2f}")
```

**TypeScript**

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const QUESTIONS = { refund_due: noul("Does `refund_policy` cover the problem in `message`?") };
const state = {
  message: "I was charged twice for order A-104.",
  order: { id: "A-104", charges: [49, 49] },
  refund_policy: "Duplicate charges on the same order are refunded in full.",
};

const reversed = Object.fromEntries(Object.entries(state).reverse());
const [forward, reverse] = await Promise.all(
  [state, reversed].map(async (s) => (await client.systemOne({ state: s, questions: QUESTIONS })).answers.refund_due.noul),
);
console.log(`forward ${forward.toFixed(2)}, reversed ${reverse.toFixed(2)}, shift ${Math.abs(forward - reverse).toFixed(2)}`);
```

Run it over a handful of real examples. A shift that would cross your threshold means the question or criteria are too loose; tighten them rather than relying on order.

**Size.** The limits are in tokens, not characters: **64k per request** (state plus all questions) and **32k for the state plus the single longest question** ([Models](12-models.md)). Stay well under them: even inside the limits, irrelevant material costs accuracy. For a document too long for one request, split it and ask the same question about each part, then combine the answers in code:

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

client = TypeSafeClient()
QUESTION = {"mentions_refund": Noul(instructions="Does `text` mention a refund?")}


def chunks(text: str, size: int = 20_000, overlap: int = 500) -> list[str]:
    return [text[i : i + size] for i in range(0, max(len(text) - overlap, 1), size - overlap)]


def any_part_mentions_refund(document: str) -> float:
    answers = [client.system_one({"text": part}, QUESTION).nouls["mentions_refund"].noul for part in chunks(document)]
    return max(answers)  # "anywhere in the document" = the strongest part
```

**TypeScript**

<!-- ts-check run:
const document = "Order A-104 was charged twice. ".repeat(1000) + "Please refund the duplicate.";
-->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const QUESTION = { mentions_refund: noul("Does `text` mention a refund?") };

function chunks(text: string, size = 20_000, overlap = 500): string[] {
  const out: string[] = [];
  for (let i = 0; i < Math.max(text.length - overlap, 1); i += size - overlap) out.push(text.slice(i, i + size));
  return out;
}

async function anyPartMentionsRefund(document: string): Promise<number> {
  const answers = await Promise.all(
    chunks(document).map(async (text) => (await client.systemOne({ state: { text }, questions: QUESTION })).answers.mentions_refund.noul),
  );
  return Math.max(...answers); // "anywhere in the document" = the strongest part
}

console.log(await anyPartMentionsRefund(document));
```

Chunk size is in characters here; check `usage.input_tokens` on a sample to pick one that fits ([counting tokens](15-faq.md#how-do-i-count-tokens-before-sending-a-request)). To find *where* in a document something is, rather than whether, see [Semantic find](cookbooks/semantic_find.md).

---

[← 2. Quick start](02-quickstart.md) · Next: [4. Primitives →](04-primitives/README.md)
