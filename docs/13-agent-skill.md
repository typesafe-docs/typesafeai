# 13. Agent skill

[← Back to README](../README.md) · Source: <https://docs.typesafe.ai/agent-skill> · Skill: <https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md>

The TypeSafe agent skill gives your coding agent (Claude Code, Codex, and others) full context on the TypeSafe API: the question types, the architectural patterns, and best practices for structuring evaluations.

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

## Give the agent an API key

The skill itself needs no key: it's documentation your agent reads. Add a key only if you want the agent to **run** test queries. Both SDKs and the examples read `TYPESAFE_API_KEY`.

1. Create a key at <https://console.typesafe.ai/keys>.
2. Export it in the shell you start the agent from, so the agent and every process it spawns inherit it:

```bash
export TYPESAFE_API_KEY="your-key-here"   # or add it to ~/.zshrc / ~/.bashrc
claude                            # or codex, cursor-agent, ...
```

3. Or keep it per project, out of git. In Claude Code, `.claude/settings.local.json` isn't committed, and its `env` block applies to every command the agent runs:

```json
{
  "env": { "TYPESAFE_API_KEY": "your-key-here" }
}
```

4. Check that the agent can reach the API with a call that evaluates nothing:

```bash
curl -sS https://api.typesafe.ai/v1/models -H "Authorization: Bearer $TYPESAFE_API_KEY"
```

Then ask for experiments, for example: *"Using the TypeSafe skill, run some experiments using the TypeSafe API key that I've exported to `TYPESAFE_API_KEY`."* Never paste the key into the chat or commit it. Add `.env` to `.gitignore` if you keep it there.

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

Naming the skill in your prompt ("use the TypeSafe skill") works in any agent, so each prompt below does that. With the Claude Code plugin you can also invoke `/typesafe:typesafe-ai` directly.

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

Map your code to the cookbooks. Point the agent at a [specific cookbook](cookbooks/consistency_noul_cookbook.md) that solves a problem you have, or at the [cookbooks index](https://docs.typesafe.ai/cookbooks):

```text
Using the TypeSafe skill, analyze my code and see if there are any applicable
cookbooks (https://docs.typesafe.ai/cookbooks) that show how I could
refactor my code to be less fragile or complex.
```

## Good vibe coding principles

1. Talk it through with your agent, starting from the prompts above.
2. Review the plan before you implement it.
3. **Keep the constants (questions and thresholds) in one file** so they're easy to review. Agents aren't great at writing questions, so expect to edit them together.
4. Don't take assertions at face value. Ask the agent to validate its assumptions.

A layout that keeps reviews easy:

**Python**

```python
# typesafe_config.py: the only file reviewers need to read closely
from typesafe_sdk import Choice, Noul, Score

MODEL = "jev-1.14.0"           # pinned, because thresholds were tuned against it

TRIAGE_QUESTIONS = {
    "department": Choice(instructions="Which team should handle this?", criteria={...}),
    "any_team_fits": Noul(instructions="Does the message belong to the billing or technical team?"),  # companion Noul
    "is_urgent":  Noul(instructions="The message conveys urgency or time-sensitivity"),
    "frustration": Score(instructions="How frustrated is the customer?", criteria=[...]),
}

THRESHOLDS = {
    "department_min_probability": 0.7,  # probabilities[choice] of the team you route to
    "urgent_yes": 0.7,                  # the official Noul starting point
    "frustration_priority": 1.5,
}
```

**TypeScript**

```ts
// typesafeConfig.ts: the only file reviewers need to read closely
import { choice, noul, score } from "@typesafe-ai/sdk";

export const MODEL = "jev-1.14.0"; // pinned, because thresholds were tuned against it

export const TRIAGE_QUESTIONS = {
  department: choice("Which team should handle this?", { billing: "Charges, invoices", technical: "Bugs, outages" }),
  any_team_fits: noul("Does the message belong to the billing or technical team?"), // companion Noul
  is_urgent: noul("The message conveys urgency or time-sensitivity"),
  frustration: score("How frustrated is the customer?", ["Calm", "Frustrated but civil", "Very angry"]),
};

export const THRESHOLDS = {
  departmentMinProbability: 0.7, // probabilities[choice] of the team you route to
  urgentYes: 0.7, // the official Noul starting point
  frustrationPriority: 1.5,
} as const;
```

## Common issues

| Symptom | Fix |
|---|---|
| The agent isn't using the skill | Invoke `/typesafe:typesafe-ai` in Claude Code, or say "use the TypeSafe skill". Confirm the installer targeted the right agent, then restart it. |
| Routing doesn't behave as expected | Thresholds set too high cause false negatives, and too low cause false positives. Make the questions more specific. |
| Confidence thresholds are everywhere | If you only need the best option, take `choice` and don't threshold at all. If code has to decide whether to act, start with the probability: the Noul value itself, or `probabilities[choice]` for a Choice. Read a Score's level probabilities when its position could hide a split answer. `confidence` summarizes uncertainty and is often not the number to act on; for a Choice it's computed from the top probability, so it adds no second check. See [Confidence](05-confidence.md) and [Routing by probability](07-patterns.md#routing-by-probability). |
| TypeSafe code is hard to review | Keep the questions and thresholds in one file. |
| The agent invents request or response fields | The skill is probably stale, so update it. |

---

[← 12. Models](12-models.md) · Next: [14. Cheat sheet →](14-cheatsheet.md)
