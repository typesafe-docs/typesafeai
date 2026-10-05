# 4.2 Score

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/primitives/score>

Use a **Score** when the answer is a position on a spectrum you can describe in steps: bug severity, customer happiness, years of Python experience.

Example Score questions and their levels:

```text
"How severe is the bug being reported?"
  → 0: Cosmetic; no impact to functionality
  → 1: Broken or degraded feature, but workaround exists
  → 2: Blocking issue; no workaround exists

"How formal is this outfit based on the description"
  → 0: gym clothes
  → 1: casual
  → 2: business casual
  → 3: formal
  → 4: black tie

"How relevant is this candidate's experience to the job posting"
  → 0: completely unrelated
  → 1: adjacent field
  → 2: some direct experience
  → 3: deep, direct experience
```

The same three as SDK objects:

**Python**

```python
from typesafe_sdk import Score

SCALES = {
    "bug_severity": Score(
        instructions="How severe is the bug being reported?",
        criteria=[
            "Cosmetic; no impact to functionality",
            "Broken or degraded feature, but workaround exists",
            "Blocking issue; no workaround exists",
        ],
    ),
    "outfit_formality": Score(
        instructions="How formal is this outfit based on the description",
        criteria=["gym clothes", "casual", "business casual", "formal", "black tie"],
    ),
    "candidate_relevance": Score(
        instructions="How relevant is this candidate's experience to the job posting",
        criteria=["completely unrelated", "adjacent field", "some direct experience", "deep, direct experience"],
    ),
}
```

**TypeScript**

```ts
import { score } from "@typesafe-ai/sdk";

const SCALES = {
  bug_severity: score("How severe is the bug being reported?", [
    "Cosmetic; no impact to functionality",
    "Broken or degraded feature, but workaround exists",
    "Blocking issue; no workaround exists",
  ]),
  outfit_formality: score("How formal is this outfit based on the description", [
    "gym clothes", "casual", "business casual", "formal", "black tie",
  ]),
  candidate_relevance: score("How relevant is this candidate's experience to the job posting", [
    "completely unrelated", "adjacent field", "some direct experience", "deep, direct experience",
  ]),
};
```

## Request

| Field | Value |
|---|---|
| `type` | `"score"` |
| `instructions` | What's being rated |
| `criteria` | An **ordered array** of level descriptions, low to high. At least 2 levels, at most **10**. |

A level's number is its **index** in `criteria` (0, 1, 2, …).

```json
{
  "state": "The export button crashes the settings page in Safari. It works in Chrome, but a few of our customers only use Safari.",
  "model": "jev-latest",
  "questions": {
    "bug_severity": {
      "type": "score",
      "instructions": "How severe is the reported issue?",
      "criteria": [
        "Cosmetic; no impact to functionality",
        "Broken or degraded feature, but workaround exists",
        "Blocking issue; no workaround exists"
      ]
    }
  }
}
```

Python:

```python
from typesafe_sdk import Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state="The export button crashes the settings page in Safari. It works in Chrome, but a few of our customers only use Safari.",
        questions={
            "bug_severity": Score(
                instructions="How severe is the reported issue?",
                criteria=[
                    "Cosmetic; no impact to functionality",
                    "Broken or degraded feature, but workaround exists",
                    "Blocking issue; no workaround exists",
                ],
            ),
        },
    )
    print(response.answers["bug_severity"].score)  # 1.43
```

TypeScript:

```ts
import { score, TypeSafeClient } from "@typesafe-ai/sdk";

const { answers } = await new TypeSafeClient().systemOne({
  state: "The export button crashes the settings page in Safari...",
  questions: {
    bug_severity: score("How severe is the reported issue?", [
      "Cosmetic; no impact to functionality",
      "Broken or degraded feature, but workaround exists",
      "Blocking issue; no workaround exists",
    ]),
  },
});
console.log(answers.bug_severity.score, answers.bug_severity.confidence);
```

## Response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "bug_severity": {
      "type": "score",
      "score": 1.43,
      "confidence": 0.35,
      "legend": {
        "0": "Cosmetic; no impact to functionality",
        "1": "Broken or degraded feature, but workaround exists",
        "2": "Blocking issue; no workaround exists"
      },
      "probabilities": { "0": 0.0, "1": 0.57, "2": 0.43 }
    }
  },
  "usage": { "input_tokens": 332, "output_tokens": 18 }
}
```

- `score` is the probability-weighted mean of the level numbers: `0×0.0 + 1×0.57 + 2×0.43 = 1.43`.
- `probabilities` is keyed by level number. Over HTTP the keys are strings. The Python SDK uses integer keys.
- `legend` maps each level number back to its description.
- `confidence` summarizes the spread. See [Confidence → Score](../05-confidence.md#score).

## Reading a Score

The same question run against different bug reports:

| State | score | confidence | P(0) | P(1) | P(2) |
|---|---|---|---|---|---|
| The export button is misaligned by a few pixels on the settings page. | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| The PDF export button does nothing when clicked. I can still export to CSV and convert it myself, but that takes ages. | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| Export to PDF fails with a spinner that never finishes. Some of our team say CSV export still works for them, others say it fails too. | 1.11 | 0.84 | 0.0 | 0.89 | 0.11 |
| The export button crashes the settings page in Safari. It works in Chrome, but a few of our customers only use Safari. | 1.43 | 0.35 | 0.0 | 0.57 | 0.43 |
| Nobody on our team can log in since this morning. We get a 500 error on every attempt. | 2.0 | 1.0 | 0.0 | 0.0 | 1.0 |

> Different distributions can give the **same** score. A 1.0 can mean everything on level 1, or half on level 0 and half on level 2. Read `probabilities` and `confidence` along with the score. Use fractional scores to **rank** or to **threshold**, or round them to the nearest level.

## Writing good levels

- **Describe situations, not degrees.** "Broken or degraded feature, but workaround exists" works. "Moderately severe" doesn't.
- **Each level is judged on its own.** The model never sees level numbers or neighboring levels. Numbers-only levels fail:

  ```text
  instructions: "Rate severity from 0 to 2, where 2 is worst"
  criteria: ["0", "1", "2"]
  → score 0.55, confidence 0.33   (vs. 0.0 at confidence 1.0 with descriptive levels)
  ```

- **One dimension per Score.** "Punctual and smart and experienced" is three questions.
- **Give rare extremes their own level**, for example adding "abusive or threatening" above "very angry".
- **No in-between at all?** Use a Choice, or several Nouls.

## Splitting a complex judgment

Ticket priority built from three Scores in **one** request:

```json
{
  "state": "Export to PDF fails with a spinner that never finishes. Some of our team say CSV export still works for them, others say it fails too. This is the third time I'm writing in and honestly I'm done. Steps: open any report, click Export, choose PDF. Chrome 128 on macOS.",
  "model": "jev-latest",
  "questions": {
    "severity": {
      "type": "score",
      "instructions": "How severe is the reported issue?",
      "criteria": [
        "Cosmetic; no impact to functionality",
        "Broken or degraded feature, but workaround exists",
        "Blocking issue; no workaround exists"
      ]
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated is the customer?",
      "criteria": [
        "Calm, just stating facts",
        "Frustrated but civil",
        "Very angry, strong language or threatening to leave"
      ]
    },
    "report_quality": {
      "type": "score",
      "instructions": "How much does the report give an engineer to work with?",
      "criteria": [
        "No detail; just says something is broken",
        "Names the feature but no steps or environment",
        "Steps to reproduce or environment, but not both",
        "Steps to reproduce and environment"
      ]
    }
  }
}
```

Results: `severity 1.24 (conf 0.64)`, `frustration 1.28 (conf 0.58)`, `report_quality 3.0 (conf 1.0)`.

**Normalize before you weight.** Divide each score by its top level number (`len(criteria) - 1`) so every score is on a 0–1 scale:

**Python**

```python
from typesafe_sdk import Score, TypeSafeClient

TRIAGE_QUESTIONS = {
    "severity": Score(
        instructions="How severe is the reported issue?",
        criteria=[
            "Cosmetic; no impact to functionality",
            "Broken or degraded feature, but workaround exists",
            "Blocking issue; no workaround exists",
        ],
    ),
    "frustration": Score(
        instructions="How frustrated is the customer?",
        criteria=[
            "Calm, just stating facts",
            "Frustrated but civil",
            "Very angry, strong language or threatening to leave",
        ],
    ),
    "report_quality": Score(
        instructions="How much does the report give an engineer to work with?",
        criteria=[
            "No detail; just says something is broken",
            "Names the feature but no steps or environment",
            "Steps to reproduce or environment, but not both",
            "Steps to reproduce and environment",
        ],
    ),
}


def normalized(answers, question_id: str) -> float:
    """Put a score on 0 to 1 by dividing by its top level number."""
    top_level = len(TRIAGE_QUESTIONS[question_id].criteria) - 1
    return answers[question_id].score / top_level


def priority(ticket: str) -> float:
    with TypeSafeClient() as client:
        response = client.system_one(state=ticket, questions=TRIAGE_QUESTIONS)
    answers = response.answers

    severity = normalized(answers, "severity")
    frustration = normalized(answers, "frustration")
    report_quality = normalized(answers, "report_quality")

    # A detailed report helps an engineer investigate, so it raises priority a little.
    return 0.6 * severity + 0.3 * frustration + 0.1 * report_quality
```

**TypeScript**

```ts
import { score, TypeSafeClient } from "@typesafe-ai/sdk";

const TRIAGE_QUESTIONS = {
  severity: score("How severe is the reported issue?", [
    "Cosmetic; no impact to functionality",
    "Broken or degraded feature, but workaround exists",
    "Blocking issue; no workaround exists",
  ]),
  frustration: score("How frustrated is the customer?", [
    "Calm, just stating facts",
    "Frustrated but civil",
    "Very angry, strong language or threatening to leave",
  ]),
  report_quality: score("How much does the report give an engineer to work with?", [
    "No detail; just says something is broken",
    "Names the feature but no steps or environment",
    "Steps to reproduce or environment, but not both",
    "Steps to reproduce and environment",
  ]),
};
type Id = keyof typeof TRIAGE_QUESTIONS;

async function priority(ticket: string): Promise<number> {
  const { answers } = await new TypeSafeClient().systemOne({ state: ticket, questions: TRIAGE_QUESTIONS });

  // Put a score on 0 to 1 by dividing by its top level number.
  const normalized = (id: Id) => answers[id].score / (TRIAGE_QUESTIONS[id].criteria.length - 1);

  // A detailed report helps an engineer investigate, so it raises priority a little.
  return 0.6 * normalized("severity") + 0.3 * normalized("frustration") + 0.1 * normalized("report_quality");
}
```

`0.6 × 0.62 + 0.3 × 0.64 + 0.1 × 1.0 ≈ 0.66`

## Structured level descriptions

If the model keeps landing between two neighboring levels on inputs you think are clear, turn each level into an object with the same field names throughout:

```json
{
  "state": "Export to PDF fails with a spinner that never finishes. Some of our team say CSV export still works for them, others say it fails too.",
  "model": "jev-latest",
  "questions": {
    "bug_severity": {
      "type": "score",
      "instructions": "How severe is the reported issue?",
      "criteria": [
        { "what": "Cosmetic; no impact to functionality",              "examples": ["typo in a label", "misaligned icon"] },
        { "what": "Broken or degraded feature, but workaround exists", "examples": ["export fails in one browser but works in another"] },
        { "what": "Blocking issue; no workaround exists",               "examples": ["cannot log in", "data loss"] }
      ]
    }
  }
}
```

Examples only help when they **resemble your real inputs**. On the Safari report:

| Level description | score | confidence |
|---|---|---|
| Plain strings | 1.43 | 0.35 |
| With a matching example ("export fails in one browser but works in another") | 1.03 | 0.96 |
| With an unrelated example ("search fails, but browsing categories still works") | 1.43 | 0.35 |

> Higher confidence alone doesn't prove an answer is correct. Test revised levels on held-out inputs with known labels.

> **Jaggedness note:** don't interpolate between levels to reconstruct an exact number. Score levels are weakly calibrated numerically. Thresholds are fine, exact magnitudes aren't.

---

[← Choice](choice.md) · Next: [Noul →](noul.md)
