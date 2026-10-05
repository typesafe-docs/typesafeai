# 13. Agent skill

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/agent-skill> · Skill: <https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md>

The TypeSafe agent skill gives your coding agent (Claude Code, Codex, and others) full context on the TypeSafe API: the three question types, the architectural patterns, and best practices for structuring evaluations.

## Installation

Pick **one** method so you don't end up with duplicate copies.

### Claude Code

```bash
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai
```

You can then invoke it directly with `/typesafe:typesafe-ai`.

### Other agents

```bash
npx skills add typesafe-ai/skills --skill typesafe-ai
# project-local by default; add -g to install globally
```

### Copy-paste prompt

```text
Install the TypeSafe skill. If you're in Claude Code, run `claude plugin marketplace add typesafe-ai/skills`,
then `claude plugin install typesafe@typesafe-ai`. If you're in another agent, run
`npx skills add typesafe-ai/skills --skill typesafe-ai` and select your agent. Use one installation method.
You can read the skill directly at https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md
(raw: https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md).
Then use the TypeSafe skill when working on this project.
```

### Manual

Copy the whole `skills/typesafe-ai` directory, including its reference files, into your agent's skills directory.

## Updating

```bash
# Claude Code plugin
claude plugin marketplace update typesafe-ai
claude plugin update typesafe@typesafe-ai
# then restart Claude Code, or run /reload-plugins
# auto-update: /plugin → Marketplaces → typesafe-ai → Enable auto-update

# skills.sh
npx skills update
```

## Example prompts

Find opportunities:

```text
Using the TypeSafe skill, explore the project and find opportunities for using
intelligent judgement to stand in for complex parsing or other fragile code.
```

Experiment with a real key:

```text
Using the TypeSafe skill, run some experiments using the TypeSafe API key that I've
exported to `TYPESAFE_API_KEY`. Propose changes based on the most promising results.
```

Map your code to the cookbooks:

```text
Using the TypeSafe skill, analyze my code and see if there are any applicable
cookbooks (https://console.typesafe.ai/docs/cookbooks) that show how I could
refactor my code to be less fragile or complex.
```

Build something:

```text
Let's build a simple CLI that uses the TypeSafe API to evaluate a set of supplied documents
on multiple dimensions. Use the TypeSafe skill to understand how to use the TypeSafe API and
how to structure the system. Ask me questions about what kinds of documents I want to evaluate
and on what dimensions.
```

## Principles for vibe coding

1. Talk it through with your agent, starting from the prompts above.
2. Review the plan before you implement it.
3. **Keep the constants (questions and thresholds) in one file** so they're easy to review. Agents aren't great at writing questions, so expect to edit them together.
4. Don't take assertions at face value. Ask the agent to validate its assumptions.

A layout that keeps reviews easy:

**Python**

```python
# typesafe_config.py: the only file reviewers need to read closely
from typesafe_sdk import Choice, Noul, Score

MODEL = "jev-1.13.0"           # pinned, because thresholds were tuned against it

TRIAGE_QUESTIONS = {
    "department": Choice(instructions="Which team should handle this?", criteria={...}),
    "is_urgent":  Noul(instructions="The message conveys urgency or time-sensitivity"),
    "frustration": Score(instructions="How frustrated is the customer?", criteria=[...]),
}

THRESHOLDS = {
    "department_min_confidence": 0.5,
    "urgent_yes": 0.8,
    "frustration_priority": 1.5,
}
```

**TypeScript**

```ts
// typesafeConfig.ts: the only file reviewers need to read closely
import { choice, noul, score } from "@typesafe-ai/sdk";

export const MODEL = "jev-1.13.0"; // pinned, because thresholds were tuned against it

export const TRIAGE_QUESTIONS = {
  department: choice("Which team should handle this?", { billing: "Charges, invoices", technical: "Bugs, outages", other: null }),
  is_urgent: noul("The message conveys urgency or time-sensitivity"),
  frustration: score("How frustrated is the customer?", ["Calm", "Frustrated but civil", "Very angry"]),
};

export const THRESHOLDS = {
  departmentMinConfidence: 0.5,
  urgentYes: 0.8,
  frustrationPriority: 1.5,
} as const;
```

## Common issues

| Symptom | Fix |
|---|---|
| The agent isn't using the skill | Invoke `/typesafe:typesafe-ai` in Claude Code, or say "use the TypeSafe skill". Confirm the installer targeted the right agent, then restart it. |
| Routing doesn't behave as expected | Thresholds set too high cause false negatives, and too low cause false positives. Make the questions more specific. |
| Confidence thresholds are everywhere | If you only need the best option, take the highest-probability `choice`. For statistical methods, work from `probabilities`. |
| TypeSafe code is hard to review | Keep the questions and thresholds in one file. |
| The agent invents request or response fields | The skill is probably stale, so update it. |

---

[← 12. Models](12-models.md) · Next: [14. Cheat sheet →](14-cheatsheet.md)
