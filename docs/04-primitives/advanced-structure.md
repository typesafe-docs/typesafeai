# 4.4 Advanced: structure

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/primitives/advanced>

System One models are trained to understand JSON structure. Every field below is an `EntryType`, meaning it can be `string | object | array | null`.

| Field | Applies to |
|---|---|
| `instructions` | Choice, Score, Noul |
| `criteria` values (option descriptions) | Choice |
| `criteria` entries (level descriptions) | Score |
| `criteria.true` / `criteria.false` | Noul |

## When to add structure

- **For clarity:** a question has several parts, and labeled keys make them explicit.
- **For supporting data:** a schema, taxonomy, or database row is already JSON. Pass it as JSON instead of pasting it into a string template.
- **For similar questions:** a shared question text with a per-question data field keeps the questions distinct.

Start with strings. Add structure when it separates guidance that would otherwise blur together.

## Structured instructions

A single `field` object describes the field being checked, and every question refers to it by key. The same shape drives a **Noul** that verifies a value, a **Choice** that picks the value from candidates, and two **Scores** that place a value on a scale. All of them go in one request:

```json
{
  "state": {
    "source_text": "Invoice #4471 issued March 3, 2026 to Beaver Dam Logistics for $12,840.00, net 30."
  },
  "model": "jev-latest",
  "questions": {
    "invoice_number_is_correct": {
      "type": "noul",
      "instructions": {
        "field": {
          "name": "invoice_number",
          "type": "string",
          "description": "The identifier printed on the invoice."
        },
        "extracted_value": "4471",
        "question": "Does `extracted_value` match the `field` as it appears in `source_text`?"
      }
    },
    "customer_name": {
      "type": "choice",
      "instructions": {
        "field": {
          "name": "customer_name",
          "type": "string",
          "description": "The organization the invoice was issued to."
        },
        "question": "Which option is the value of `field` in `source_text`?"
      },
      "criteria": {
        "Beaver Logistics": null,
        "Dam Logistics": null,
        "Beaver Dam Logistics": null,
        "Beaver": null,
        "Dam": null
      }
    },
    "amount_due": {
      "type": "score",
      "instructions": {
        "field": {
          "name": "amount_due",
          "type": "number",
          "unit": "USD",
          "description": "The total the invoice asks to be paid."
        },
        "question": "How large is the `field` value in `source_text`?"
      },
      "criteria": [
        "Under $1,000",
        "$1,000 to $10,000",
        "$10,000 to $100,000",
        "$100,000 to $1,000,000",
        "Over $1,000,000"
      ]
    },
    "payment_terms": {
      "type": "score",
      "instructions": {
        "field": {
          "name": "payment_terms",
          "type": "integer",
          "unit": "days",
          "description": "Days allowed for payment, from terms such as \"net 30\"."
        },
        "question": "How many days does the `field` in `source_text` allow for payment?"
      },
      "criteria": [
        "Due on receipt",
        "Net 10",
        "Net 30",
        "Net 60",
        "Net 90"
      ]
    }
  }
}
```

In code, you'd loop over the fields of an extracted record and build one of these questions per field, all sent in a single call. The [SDE cascade cookbook](../cookbooks/sde_cascade.md) does something similar.

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

SCHEMA = {
    "invoice_number": {"type": "string", "description": "The identifier printed on the invoice."},
    "customer_name": {"type": "string", "description": "The organization the invoice was issued to."},
}
extracted = {"invoice_number": "4471", "customer_name": "Beaver Dam Logistics"}

questions = {
    f"{name}_is_correct": Noul(
        instructions={
            "field": {"name": name, **spec},
            "extracted_value": extracted[name],
            "question": "Does `extracted_value` match the `field` as it appears in `source_text`?",
        }
    )
    for name, spec in SCHEMA.items()
}

with TypeSafeClient() as client:
    answers = client.system_one(
        state={"source_text": "Invoice #4471 issued March 3, 2026 to Beaver Dam Logistics for $12,840.00, net 30."},
        questions=questions,
    ).answers

suspicious = [k for k, a in answers.items() if a.noul < 0.5]
```

**TypeScript**

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient, type NoulQuestion } from "@typesafe-ai/sdk";

const SCHEMA = {
  invoice_number: { type: "string", description: "The identifier printed on the invoice." },
  customer_name: { type: "string", description: "The organization the invoice was issued to." },
};
const extracted: Record<keyof typeof SCHEMA, string> = {
  invoice_number: "4471",
  customer_name: "Beaver Dam Logistics",
};

const questions: Record<string, NoulQuestion> = {};
for (const [name, spec] of Object.entries(SCHEMA) as [keyof typeof SCHEMA, (typeof SCHEMA)[keyof typeof SCHEMA]][]) {
  questions[`${name}_is_correct`] = noul({
    field: { name, ...spec },
    extracted_value: extracted[name],
    question: "Does `extracted_value` match the `field` as it appears in `source_text`?",
  });
}

const { answers } = await new TypeSafeClient().systemOne({
  state: { source_text: "Invoice #4471 issued March 3, 2026 to Beaver Dam Logistics for $12,840.00, net 30." },
  questions,
});

const suspicious = Object.entries(answers).filter(([, a]) => a.noul < 0.5).map(([k]) => k);
```

Arrays work too. Use one when the instruction is a list of things to check or compare:

```json
"instructions": {
  "question": "Does the claimed sender identity conflict with the sending domain?",
  "compare": ["ticket.sender.display_name", "ticket.sender.email"],
  "focus": "Compare the named organization with the email domain."
}
```

And a record from your database, passed as is:

```json
"instructions": {
  "potential_duplicate": {
    "name": "John Smith",
    "location": "Oakland, California",
    "last_employer": "Google"
  },
  "question": "Is the resume for the same person as `potential_duplicate`?"
}
```

## Structured Choice options: a JSON rubric for clear boundaries

```json
{
  "state": "I ordered the standing desk two weeks ago and tracking still says label created. Was I even charged?",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": {
        "question": "Which team should handle this message?",
        "focus": "Classify the customer's primary request, not every topic mentioned."
      },
      "criteria": {
        "billing": {
          "what": "Charges, invoices, refunds, or subscriptions",
          "not_for": "Order tracking or account access",
          "examples": ["I was charged twice", "Where is my refund?"]
        },
        "orders": {
          "what": "Order status, delivery, cancellation, or returns",
          "not_for": "Charges or account access",
          "examples": ["Where is my package?", "Cancel my order"]
        },
        "account": {
          "what": "Login, password, profile, or security",
          "not_for": "Charges or delivery",
          "examples": ["I can't log in", "Change my email"]
        }
      }
    }
  }
}
```

The same approach applied to a disposable-card help topic:

```json
{
  "state": "How many disposable virtual cards can I make per day?",
  "model": "jev-latest",
  "questions": {
    "card_help_topic": {
      "type": "choice",
      "instructions": {
        "question": "Which disposable virtual card topic is the user asking about?",
        "focus": "Classify the information the user wants."
      },
      "criteria": {
        "get_disposable_virtual_card": {
          "what": "Purpose, eligibility, or setup",
          "not_for": "Quantity, transaction, or merchant restrictions",
          "examples": ["How can I get a disposable virtual card?", "What are disposable cards for?"]
        },
        "disposable_card_limits": {
          "what": "Quantity, transaction, or merchant restrictions",
          "not_for": "Purpose, eligibility, or setup",
          "examples": ["How many disposable cards can I make per day?", "Where can I use a disposable card?"]
        }
      }
    }
  }
}
```

## Walking a taxonomy

To classify into a deep taxonomy, ask one Choice per level and walk the tree in code. At each step the options are the children of the current node, and **each option's value is that child's subtree**. That way the model can see what lives under a branch before it commits.

The state is a product listing, and the first question picks a top-level department:

```json
{
  "state": "32oz plastic bottle with a flip straw lid. Fits most bike cages.",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which top-level department does this product belong to?",
      "criteria": {
        "Sporting Goods": {
          "Cycling": [
            "Bike Bottles & Cages",
            "Bike Lights",
            "Helmets"
          ],
          "Fitness": [
            "Yoga Mats",
            "Resistance Bands"
          ],
          "Outdoor": [
            "Tents",
            "Sleeping Bags",
            "Hydration Packs"
          ]
        },
        "Home & Kitchen": {
          "Drinkware": [
            "Water Bottles",
            "Travel Mugs",
            "Tumblers"
          ],
          "Cookware": [
            "Pots & Pans",
            "Bakeware"
          ]
        },
        "Baby & Toddler": [
          "Sippy Cups",
          "Bottle Warmers",
          "Bibs"
        ]
      }
    }
  }
}
```

The bottle plausibly fits under two departments. Showing the subtrees lets the model see that both `Sporting Goods > Cycling > Bike Bottles & Cages` and `Home & Kitchen > Drinkware > Water Bottles` exist, and weigh the listing's emphasis on bike cages against everyday drinkware. The `probabilities` tell you whether the split is close enough to explore both branches.

Walking the tree in code (greedy, with an optional second branch when it's close):

**Python**

```python
from typesafe_sdk import Choice, TypeSafeClient

TAXONOMY = {
    "Sporting Goods": {
        "Cycling": [
            "Bike Bottles & Cages",
            "Bike Lights",
            "Helmets"
        ],
        "Fitness": [
            "Yoga Mats",
            "Resistance Bands"
        ],
        "Outdoor": [
            "Tents",
            "Sleeping Bags",
            "Hydration Packs"
        ]
    },
    "Home & Kitchen": {
        "Drinkware": [
            "Water Bottles",
            "Travel Mugs",
            "Tumblers"
        ],
        "Cookware": [
            "Pots & Pans",
            "Bakeware"
        ]
    },
    "Baby & Toddler": [
        "Sippy Cups",
        "Bottle Warmers",
        "Bibs"
    ]
}


def children(node):
    return node if isinstance(node, dict) else {leaf: None for leaf in node}


def walk(client: TypeSafeClient, listing: str, node, path=()):
    if node is None:
        return [path]
    options = children(node)
    answer = client.system_one(
        state=listing,
        questions={"child": Choice(
            instructions="Which category does this product belong to?",
            criteria=options,  # option -> its subtree, so the model sees what lives below
        )},
    ).answers["child"]
    ranked = sorted(answer.probabilities.items(), key=lambda kv: -kv[1])
    branches = [ranked[0][0]] + [k for k, p in ranked[1:2] if p > 0.3]  # explore a close runner-up
    return [leaf for b in branches for leaf in walk(client, listing, options[b], path + (b,))]


with TypeSafeClient() as client:
    print(walk(client, "32oz plastic bottle with a flip straw lid. Fits most bike cages.", TAXONOMY))
    # e.g. [("Sporting Goods", "Cycling", "Bike Bottles & Cages")]
```

**TypeScript**

<!-- ts-check run -->
```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

type Node = { [child: string]: Node } | string[] | null;

const TAXONOMY: Node = {
  "Sporting Goods": {
    Cycling: ["Bike Bottles & Cages", "Bike Lights", "Helmets"],
    Fitness: ["Yoga Mats", "Resistance Bands"],
    Outdoor: ["Tents", "Sleeping Bags", "Hydration Packs"],
  },
  "Home & Kitchen": {
    Drinkware: ["Water Bottles", "Travel Mugs", "Tumblers"],
    Cookware: ["Pots & Pans", "Bakeware"],
  },
  "Baby & Toddler": ["Sippy Cups", "Bottle Warmers", "Bibs"],
};

const children = (node: Node): Record<string, Node> =>
  Array.isArray(node) ? Object.fromEntries(node.map((leaf) => [leaf, null])) : (node ?? {});

async function walk(client: TypeSafeClient, listing: string, node: Node, path: string[] = []): Promise<string[][]> {
  if (node === null) return [path];
  const options = children(node);
  const { answers } = await client.systemOne({
    state: listing,
    questions: {
      // option -> its subtree, so the model sees what lives below
      child: choice("Which category does this product belong to?", options),
    },
  });
  const ranked = Object.entries(answers.child.probabilities).sort(([, a], [, b]) => b - a);
  const branches = [ranked[0][0], ...ranked.slice(1, 2).filter(([, p]) => p > 0.3).map(([k]) => k)]; // close runner-up
  const leaves = await Promise.all(branches.map((b) => walk(client, listing, options[b], [...path, b])));
  return leaves.flat();
}

console.log(await walk(new TypeSafeClient(), "32oz plastic bottle with a flip straw lid. Fits most bike cages.", TAXONOMY));
// e.g. [["Sporting Goods", "Cycling", "Bike Bottles & Cages"]]
```

> 📝 Subtrees can get large. If a branch is too large, trim its value to the direct children plus a sample of leaves. The [Hierarchical classification cookbook](../cookbooks/hierarchical_classification.md) does a full beam search over the probabilities.

## Structured Score levels

```json
{
  "state": "Fixed the null check in the payment handler. Also refactored the retry loop while I was in there, and bumped the SDK version since the old one had that timeout bug.",
  "model": "jev-latest",
  "questions": {
    "pr_scope": {
      "type": "score",
      "instructions": {
        "question": "How focused is this pull request description on a single change?",
        "note": "Judge the number of independent changes, not the size of any one change."
      },
      "criteria": [
        {
          "summary": "One change, clearly stated",
          "signals": ["A single fix or feature", "Nothing described as \"also\" or \"while I was in there\""]
        },
        {
          "summary": "One main change plus a small related tweak",
          "signals": ["A primary change and one minor adjacent edit", "The tweak supports the main change"]
        },
        {
          "summary": "Several independent changes bundled together",
          "signals": ["Two or more unrelated fixes or features", "Changes that could each be their own PR"]
        }
      ]
    }
  }
}
```

## Structured Noul criteria

Noul `criteria` is optional. When the yes/no boundary is subtle, structured `true` and `false` descriptions pin it down with a definition and examples on each side:

```json
{
  "state": {
    "sender": {
      "display_name": "Beaver Dam Builders Ltd.",
      "email": "donotreply@payroll.example"
    },
    "message": "Your Q3 bonus is ready. Reply with your login password so we can verify your identity and release the funds."
  },
  "model": "jev-latest",
  "questions": {
    "requests_credentials": {
      "type": "noul",
      "instructions": {
        "question": "Does the `message` ask the recipient to disclose a sensitive credential?",
        "inspect": "message",
        "focus": "Look for a request to send the credential itself, not a request to change or reset it."
      },
      "criteria": {
        "true": {
          "what": "Asks the recipient to reply with, type, or send a password, PIN, one-time code, or other security sensitive answer",
          "examples": [
            "Reply with your password",
            "Send us the 6-digit code you just received"
          ]
        },
        "false": {
          "what": "No sensitive credential is requested",
          "examples": [
            "Reset your password from the settings page",
            "Your statement is ready"
          ]
        }
      }
    }
  }
}
```

The same question in Python:

```python
from typesafe_sdk import Noul, NoulCriteria

requests_credentials = Noul(
    instructions={
        "question": "Does the `message` ask the recipient to disclose a sensitive credential?",
        "inspect": "message",
        "focus": "Look for a request to send the credential itself, not a request to change or reset it.",
    },
    criteria=NoulCriteria(
        true={
            "what": "Asks the recipient to reply with, type, or send a password, PIN, one-time code, or other security sensitive answer",
            "examples": ["Reply with your password", "Send us the 6-digit code you just received"],
        },
        false={
            "what": "No sensitive credential is requested",
            "examples": ["Reset your password from the settings page", "Your statement is ready"],
        },
    ),
)
```

And in TypeScript:

```ts
import { noul } from "@typesafe-ai/sdk";

const requestsCredentials = noul(
  {
    question: "Does the `message` ask the recipient to disclose a sensitive credential?",
    inspect: "message",
    focus: "Look for a request to send the credential itself, not a request to change or reset it.",
  },
  {
    true: {
      what: "Asks the recipient to reply with, type, or send a password, PIN, one-time code, or other security sensitive answer",
      examples: ["Reply with your password", "Send us the 6-digit code you just received"],
    },
    false: {
      what: "No sensitive credential is requested",
      examples: ["Reset your password from the settings page", "Your statement is ready"],
    },
  },
);
```


## What examples in criteria cost, and whether they help

Examples in `criteria` (and anything else in a question) are part of the request:

- **Cost:** they're input tokens, billed like the state. A question's tokens are paid on every request that includes it.
- **Limits:** they count toward the 64k request limit, and the longest question counts toward the 32k limit together with the state ([Models](../12-models.md#current-model-jev-113-jev-1130)).
- **Accuracy:** examples that resemble real inputs help separate neighboring options or levels, especially at a subtle boundary. The docs don't give a recommended number, and more isn't automatically better: an example that sits near the boundary teaches more than several obvious ones. [Score → Structured level descriptions](score.md#structured-level-descriptions) shows a measured case: a matching example raised confidence from 0.35 to 0.96, while an unrelated one changed nothing.

So measure. Run the same labeled inputs with and without examples and compare accuracy against `usage.input_tokens`:

**Python**

```python
from typesafe_sdk import Score, TypeSafeClient

client = TypeSafeClient(model="jev-1.13.0")  # pin, so the comparison isn't split across versions
Q = "How severe is the reported issue?"
VARIANTS: dict[str, Score] = {
    "plain": Score(instructions=Q, criteria=["Cosmetic; no impact to functionality", "Broken or degraded, workaround exists", "Blocking; no workaround"]),
    "with examples": Score(instructions=Q, criteria=[
        {"what": "Cosmetic; no impact to functionality", "examples": ["typo in a label", "misaligned icon"]},
        {"what": "Broken or degraded, workaround exists", "examples": ["export fails in one browser but works in another"]},
        {"what": "Blocking; no workaround", "examples": ["cannot log in", "data loss"]},
    ]),
}
LABELED = [  # use a few dozen real, labeled inputs
    ("The Save button is slightly off-center on mobile.", 0),
    ("PDF export hangs, but CSV export still works.", 1),
    ("Nobody on our team can sign in since the update.", 2),
]

for name, severity in VARIANTS.items():
    correct = tokens = 0
    for text, level in LABELED:
        r = client.system_one(text, {"severity": severity})
        correct += round(r.scores["severity"].score) == level
        tokens += r.usage.input_tokens or 0
    print(f"{name:>14}: {correct}/{len(LABELED)} correct, {tokens / len(LABELED):.0f} input tokens per call")
```

**TypeScript**

<!-- ts-check run -->
```ts
import { score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultModel: "jev-1.13.0" }); // pin, so the comparison isn't split across versions
const Q = "How severe is the reported issue?";
const VARIANTS = {
  plain: score(Q, ["Cosmetic; no impact to functionality", "Broken or degraded, workaround exists", "Blocking; no workaround"]),
  "with examples": score(Q, [
    { what: "Cosmetic; no impact to functionality", examples: ["typo in a label", "misaligned icon"] },
    { what: "Broken or degraded, workaround exists", examples: ["export fails in one browser but works in another"] },
    { what: "Blocking; no workaround", examples: ["cannot log in", "data loss"] },
  ]),
};
const LABELED: [text: string, level: number][] = [
  // use a few dozen real, labeled inputs
  ["The Save button is slightly off-center on mobile.", 0],
  ["PDF export hangs, but CSV export still works.", 1],
  ["Nobody on our team can sign in since the update.", 2],
];

for (const [name, severity] of Object.entries(VARIANTS)) {
  let correct = 0;
  let tokens = 0;
  for (const [text, level] of LABELED) {
    const r = await client.systemOne({ state: text, questions: { severity } });
    if (Math.round(r.answers.severity.score) === level) correct++;
    tokens += r.usage.input_tokens;
  }
  console.log(`${name.padStart(14)}: ${correct}/${LABELED.length} correct, ${Math.round(tokens / LABELED.length)} input tokens per call`);
}
```

Keep the examples only if they move accuracy enough to be worth their tokens. Look at which inputs flipped: if the fix came from one boundary case, that example is the one to keep.

---

[← Noul](noul.md) · Next: [5. Confidence →](../05-confidence.md)
