# 4.3 Noul

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/primitives/noul>

A **Noul** asks a yes/no question and returns **the probability that the answer is yes**: 0 means no and 1 means yes. Examples: does this message ask for a refund, does this resume mention distributed systems, does this comment contain personal data?

Example Noul questions:

```text
"Is the customer requesting a refund?"
"Does this resume mention experience with distributed systems?"
"Does the message contain personally identifiable information?"
"Does the room have a minifridge?"
```

## Request

| Field | Value |
|---|---|
| `type` | `"noul"` |
| `instructions` | A yes/no question or a statement to judge |
| `criteria` | *Optional* `{ "true": "...", "false": "..." }` describing what yes and no mean |

```json
{
  "state": "I have asked three times now. Can I please just talk to a real person?",
  "model": "jev-latest",
  "questions": {
    "is_human_escalation": {
      "type": "noul",
      "instructions": "Is the customer asking for a human agent?"
    },
    "is_repeat_contact": {
      "type": "noul",
      "instructions": "Has the customer contacted support about this before?",
      "criteria": {
        "true": "Mentions a prior attempt, ticket, or that they have asked before",
        "false": "No sign of any previous contact"
      }
    }
  }
}
```

Python:

```python
from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        model="jev-latest",
        state="I have asked three times now. Can I please just talk to a real person?",
        questions={
            "is_human_escalation": Noul(
                instructions="Is the customer asking for a human agent?",
            ),
            "is_repeat_contact": Noul(
                instructions="Has the customer contacted support about this before?",
                criteria=NoulCriteria(
                    true="Mentions a prior attempt, ticket, or that they have asked before",
                    false="No sign of any previous contact",
                ),
            ),
        },
    )

    print(response.answers["is_human_escalation"].noul)  # 0.99
    print(response.answers["is_repeat_contact"].noul)    # 0.93
```

TypeScript:

```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const { answers } = await new TypeSafeClient().systemOne({
  state: "I have asked three times now. Can I please just talk to a real person?",
  questions: {
    is_human_escalation: noul("Is the customer asking for a human agent?"),
    is_repeat_contact: noul("Has the customer contacted support about this before?", {
      true: "Mentions a prior attempt, ticket, or that they have asked before",
      false: "No sign of any previous contact",
    }),
  },
});
console.log(answers.is_human_escalation.noul, answers.is_repeat_contact.noul);
```

## Response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "is_human_escalation": { "type": "noul", "noul": 0.99 },
    "is_repeat_contact":   { "type": "noul", "noul": 0.93 }
  },
  "usage": { "input_tokens": 360, "output_tokens": 39 }
}
```

## Reading a Noul

The single number holds both the answer and the certainty. Recorded `jev-1.13.0` values for `is_human_escalation`:

| State | noul |
|---|---|
| Thanks, that fixed it! | 0.02 |
| How do I reset my password? | 0.07 |
| I need this sorted today, whatever it takes. | 0.26 |
| Are you a bot? | 0.40 |
| Is there any way to speak to someone about my invoice? | 0.84 |
| I have asked three times now. Can I please just talk to a real person? | 0.99 |

A Noul has **no separate `confidence`**: two outcomes are fully described by one probability. If you want a confidence-style value anyway, use `abs(2 * p - 1)`.

Thresholding:

**Python**

```python
wants_human = response.answers["is_human_escalation"].noul > 0.9

if wants_human:
    route_to_agent(ticket)
else:
    route_to_bot(ticket)
```

**TypeScript**

<!-- ts-check:
import type { NoulResponse } from "@typesafe-ai/sdk";
declare const answers: { is_human_escalation: NoulResponse };
declare const ticket: string;
declare function routeToAgent(t: string): void;
declare function routeToBot(t: string): void;
-->
```ts
const wantsHuman = answers.is_human_escalation.noul > 0.9;

if (wantsHuman) routeToAgent(ticket);
else routeToBot(ticket);
```

Picking a threshold:

- **0.5:** yes and no are equally cheap to act on.
- **Higher:** a false yes is expensive, such as paging someone or issuing a refund.
- **Lower:** a missed yes is expensive, such as failing to flag a safety issue.
- **Middle band → a human.**

### Noul vs. Score for degree questions

A Noul gives a probability, **not** a measure of degree:

| Candidate | Noul: "Is the candidate strong in Python?" | Score: "How much Python experience does the candidate have?" |
|---|---|---|
| My experience is in Java and Go. I have not used Python. | 0.03 | 0.0 (No experience) |
| I have used Python occasionally for small scripts alongside my main Java work. | 0.14 | 1.0 (Some familiarity) |
| I used Python every day for two years in my last job, mostly data pipelines. | 0.81 | 2.05 (Regular use in a job) |
| I have written Python daily for eight years, including maintaining a large Django codebase. | 0.92 | 2.89 (Deep expertise) |

## Writing a Noul

- **One condition per Noul.** Split "angry *and* asking for a refund?" into two questions and combine them in code.
- **Phrase it so high means yes.** "Contains personal data?" is better than "Is free of personal data?".
- **A statement works too.** For "The customer is requesting a refund", a value near 1 means the statement is true.
- **Make the boundary sharp.** "Does this candidate have *any* Python experience?" Add `criteria` when the boundary is subtle.
- **Don't invert** `true` and `false` relative to the instruction. Jev 1.13 handles contradictions poorly.

## Several Nouls with a review band

**Python**

```python
from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient

SUPPORT_QUESTIONS = {
    "is_human_escalation": Noul(
        instructions="Is the customer asking for a human agent?",
    ),
    "is_repeat_contact": Noul(
        instructions="Has the customer contacted support about this before?",
        criteria=NoulCriteria(
            true="Mentions a prior attempt, ticket, or that they have asked before",
            false="No sign of any previous contact",
        ),
    ),
}

YES = 0.8
NO = 0.2


def route(message: str) -> None:
    with TypeSafeClient() as client:
        response = client.system_one(
            model="jev-latest",
            state=message,
            questions=SUPPORT_QUESTIONS,
        )
    answers = response.answers

    wants_human = answers["is_human_escalation"].noul
    repeat = answers["is_repeat_contact"].noul

    if NO < wants_human < YES or NO < repeat < YES:
        # The model isn't sure either way. Let a person decide.
        send_to_review(message)
        return

    priority = "high" if repeat > YES else "normal"
    if wants_human > YES:
        route_to_agent(message, priority=priority)
    else:
        route_to_bot(message, priority=priority)
```

**TypeScript**

<!-- ts-check:
declare function sendToReview(m: string): void;
declare function routeToAgent(m: string, p: "high" | "normal"): void;
declare function routeToBot(m: string, p: "high" | "normal"): void;
-->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const SUPPORT_QUESTIONS = {
  is_human_escalation: noul("Is the customer asking for a human agent?"),
  is_repeat_contact: noul("Has the customer contacted support about this before?", {
    true: "Mentions a prior attempt, ticket, or that they have asked before",
    false: "No sign of any previous contact",
  }),
};

const YES = 0.8;
const NO = 0.2;
const client = new TypeSafeClient();

async function route(message: string): Promise<void> {
  const { answers } = await client.systemOne({ model: "jev-latest", state: message, questions: SUPPORT_QUESTIONS });

  const wantsHuman = answers.is_human_escalation.noul;
  const repeat = answers.is_repeat_contact.noul;

  if ((NO < wantsHuman && wantsHuman < YES) || (NO < repeat && repeat < YES)) {
    // The model isn't sure either way. Let a person decide.
    return sendToReview(message);
  }

  const priority = repeat > YES ? "high" : "normal";
  if (wantsHuman > YES) routeToAgent(message, priority);
  else routeToBot(message, priority);
}
```

## Structured instructions: questions built in code

Compare an incoming resume against records in a candidate database that might be the same person. Each record goes into a `potential_duplicate` field as it is, the `question` is the same for every record, and every record is checked in **one** request. The question keys are generated in code and contain each record's database ID:

```json
{
  "state": {
    "resume": {
      "name": "John Smith",
      "location": "Oakland, CA",
      "summary": "Backend engineer with eight years of Python and Go experience.",
      "experience": [
        {
          "employer": "Google",
          "title": "Senior Backend Engineer",
          "years": "2021-2025"
        },
        {
          "employer": "Microsoft",
          "title": "Software Engineer",
          "years": "2017-2021"
        }
      ]
    }
  },
  "model": "jev-latest",
  "questions": {
    "same_as_record_18": {
      "type": "noul",
      "instructions": {
        "potential_duplicate": {
          "name": "Jon Smith",
          "location": "Oakland, CA",
          "last_employer": "Google"
        },
        "question": "Is the resume for the same person as `potential_duplicate`?"
      }
    },
    "same_as_record_42": {
      "type": "noul",
      "instructions": {
        "potential_duplicate": {
          "name": "John Smith",
          "location": "Austin, TX",
          "last_employer": "Lone Star Freight"
        },
        "question": "Is the resume for the same person as `potential_duplicate`?"
      }
    },
    "same_as_record_77": {
      "type": "noul",
      "instructions": {
        "potential_duplicate": {
          "name": "John Smithers",
          "location": "Oakland, CA",
          "last_employer": "Bay Health Clinic"
        },
        "question": "Is the resume for the same person as `potential_duplicate`?"
      }
    }
  }
}
```

Response:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "same_as_record_18": {
      "type": "noul",
      "noul": 0.74
    },
    "same_as_record_42": {
      "type": "noul",
      "noul": 0.09
    },
    "same_as_record_77": {
      "type": "noul",
      "noul": 0.08
    }
  },
  "usage": {
    "input_tokens": 535,
    "output_tokens": 58
  }
}
```

Record 18 spells the name differently but matches on location and employer (0.74). Record 42 has the same name in a different city with a different employer (0.09). Record 77 has a similar name at the same location with a different employer (0.08). Threshold each value in code and send the middle values to a person.

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

SAME_PERSON = "Is the resume for the same person as `potential_duplicate`?"


def duplicate_questions(candidates: list[dict]) -> dict[str, Noul]:
    """One Noul per candidate record, all asking the same question."""
    return {
        f"same_as_record_{candidate['id']}": Noul(
            instructions={
                "potential_duplicate": {
                    "name": candidate["name"],
                    "location": candidate["location"],
                    "last_employer": candidate["last_employer"],
                },
                "question": SAME_PERSON,
            },
        )
        for candidate in candidates
    }


def find_duplicates(resume: dict, candidates: list[dict]) -> list[str]:
    with TypeSafeClient() as client:
        response = client.system_one(
            model="jev-latest",
            state={"resume": resume},
            questions=duplicate_questions(candidates),
        )
    return [
        question_id
        for question_id, answer in response.answers.items()
        if answer.noul > 0.7
    ]
```

**TypeScript**

```ts
import { noul, TypeSafeClient, type NoulQuestion } from "@typesafe-ai/sdk";

const SAME_PERSON = "Is the resume for the same person as `potential_duplicate`?";

type Candidate = { id: number; name: string; location: string; last_employer: string };

/** One Noul per candidate record, all asking the same question. */
function duplicateQuestions(candidates: Candidate[]): Record<string, NoulQuestion> {
  return Object.fromEntries(
    candidates.map((c) => [
      `same_as_record_${c.id}`,
      noul({
        potential_duplicate: { name: c.name, location: c.location, last_employer: c.last_employer },
        question: SAME_PERSON,
      }),
    ]),
  );
}

async function findDuplicates(resume: Record<string, string>, candidates: Candidate[]): Promise<string[]> {
  const { answers } = await new TypeSafeClient().systemOne({
    model: "jev-latest",
    state: { resume },
    questions: duplicateQuestions(candidates),
  });
  return Object.entries(answers)
    .filter(([, answer]) => answer.noul > 0.7)
    .map(([questionId]) => questionId);
}
```

## Counting with Nouls (don't make Jev count)

Jev doesn't count reliably. Ask one Noul per item and add them up in code:

**Python**

```python
from typesafe_sdk import Noul, TypeSafeClient

client = TypeSafeClient(model="jev-1.13")
YES = 0.5

items = ["typesafe", "apple", "california", "banana", "likes", "calibration", "orange", "vertex"]

result = client.system_one(
    {"items": items},
    {
        f"item_{i}": Noul(instructions=f"Is `items[{i}]` the name of a fruit?")
        for i in range(len(items))
    },
)

count = sum(result.nouls[f"item_{i}"].noul > YES for i in range(len(items)))
```

**TypeScript**

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultModel: "jev-1.13" });
const YES = 0.5;

const items = ["typesafe", "apple", "california", "banana", "likes", "calibration", "orange", "vertex"];

const { answers } = await client.systemOne({
  state: { items },
  questions: Object.fromEntries(items.map((_, i) => [`item_${i}`, noul(`Is \`items[${i}]\` the name of a fruit?`)])),
});

const count = items.filter((_, i) => answers[`item_${i}`].noul > YES).length;
```

---

[← Score](score.md) · Next: [Advanced: structure →](advanced-structure.md)
