# 15. FAQ & troubleshooting

[← Back to README](../README.md)

Answers collected from across the official docs, with a code fix for each.

### Is Jev a chat model? Can I plug it into Cursor or Claude Code?

No. Jev is a System One model: it returns typed decisions, not text. Use your coding agent to *write code that calls* Jev, and install the [agent skill](13-agent-skill.md) so the agent knows the API.

### Does the question ID matter?

No. The model never sees it. Put the whole question in `instructions`:

**Python**

```python
# ❌ relies on the key
{"refund": Noul(instructions="refund?")}
# ✅
{"refund": Noul(instructions="Does the customer explicitly ask for a refund or credit?")}
```

**TypeScript**

<!-- ts-check:
import { noul } from "@typesafe-ai/sdk";
-->
```ts
// ❌ relies on the key
const bad = { refund: noul("refund?") };
// ✅
const good = { refund: noul("Does the customer explicitly ask for a refund or credit?") };
```

### Should I make one request per question?

No. Questions run in parallel, so batching is about 12× cheaper and 10× faster, with identical answers. See [Parallel questions](cookbooks/parallel_questions.md).

**Python**

```python
# ❌ N round trips
answers = {k: client.system_one(state, {k: q}).answers[k] for k, q in QUESTIONS.items()}
# ✅ one round trip
answers = client.system_one(state, QUESTIONS).answers
```

**TypeScript**

<!-- ts-check run:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
const client = new TypeSafeClient();
const state = "I was charged twice. Please refund me.";
const QUESTIONS = { billing: noul("Is this about billing?"), refund: noul("Does the customer ask for a refund?") };
-->
```ts
// ❌ N round trips
const slow = await Promise.all(
  Object.entries(QUESTIONS).map(([k, q]) => client.systemOne({ state, questions: { [k]: q } })),
);
// ✅ one round trip
const { answers } = await client.systemOne({ state, questions: QUESTIONS });
```

### When do I really need two requests?

Only when you **can't build** the second request without the first answer: you need it to fetch new data, to change the state, or to pick the next options. Examples: [skill suggestion](cookbooks/skill_suggestion.md), [structure recovery](cookbooks/autoformat.md), [hierarchical classification](cookbooks/hierarchical_classification.md).

### My Noul hovers around 0.5. What's wrong?

The question is probably ambiguous, or it's really a question of degree. Tighten the boundary or switch to a Score:

**Python**

```python
# ❌ "strong" is undefined
Noul(instructions="Is the candidate strong in Python?")
# ✅ sharp yes/no
Noul(instructions="Does the resume state that the candidate has used Python at work?")
# ✅ or measure the degree
Score(instructions="How much Python experience does the candidate have?",
      criteria=["No experience", "Some familiarity", "Regular use in a job", "Deep expertise"])
```

**TypeScript**

<!-- ts-check:
import { noul, score } from "@typesafe-ai/sdk";
-->
```ts
// ❌ "strong" is undefined
noul("Is the candidate strong in Python?");
// ✅ sharp yes/no
noul("Does the resume state that the candidate has used Python at work?");
// ✅ or measure the degree
score("How much Python experience does the candidate have?", [
  "No experience", "Some familiarity", "Regular use in a job", "Deep expertise",
]);
```

### My Score keeps landing between two levels

The levels overlap, or the question measures more than one thing. Give the levels **structured descriptions with realistic examples**:

**Python**

```python
Score(
    instructions="How severe is the reported issue?",
    criteria=[
        {"what": "Cosmetic; no impact to functionality", "examples": ["typo in a label", "misaligned icon"]},
        {"what": "Broken or degraded feature, but workaround exists", "examples": ["export fails in one browser but works in another"]},
        {"what": "Blocking issue; no workaround exists", "examples": ["cannot log in", "data loss"]},
    ],
)
```

**TypeScript**

<!-- ts-check:
import { score } from "@typesafe-ai/sdk";
-->
```ts
score("How severe is the reported issue?", [
  { what: "Cosmetic; no impact to functionality", examples: ["typo in a label", "misaligned icon"] },
  { what: "Broken or degraded feature, but workaround exists", examples: ["export fails in one browser but works in another"] },
  { what: "Blocking issue; no workaround exists", examples: ["cannot log in", "data loss"] },
]);
```

### Two Choice options keep getting confused

Use contrastive `what`/`not_for`/`examples` objects. See [Choice → Structured criteria](04-primitives/choice.md#structured-contrastive-criteria).

### The answer changes when I reorder options

That's a known Jev 1.13 edge: it can lean toward the first option. Shuffle the options and compare. See [Models → Choice option order](12-models.md#8-choice-option-order).

### Can Jev count, do math, or compare dates?

Not reliably. Keep those in code: ask one Noul per item and add the results up yourself, or extract date **parts** with Choices and compare them in code. See [Jaggedness](12-models.md#known-failure-modes-jev-113) and [Date extraction](cookbooks/date_extraction_cookbook.md).

### Can Jev extract a value, like an email address or an amount?

Don't ask it to *generate* the value. Find candidates with regex and let it *pick* one:

**Python**

```python
criteria = {c: None for c in EMAIL_RE.findall(doc)} | {"none": "None of these is the requested value."}
pick = client.system_one(doc, {"pick": Choice(instructions="Which address should the receipt go to?", criteria=criteria)})
```

**TypeScript**

<!-- ts-check run:
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";
const client = new TypeSafeClient();
const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const doc = "Send the receipt to a@new.example, not b@old.example.";
-->
```ts
const criteria: Record<string, string | null> = {
  ...Object.fromEntries((doc.match(EMAIL_RE) ?? []).map((c) => [c, null])),
  none: "None of these is the requested value.",
};
const { answers } = await client.systemOne({
  state: doc,
  questions: { pick: choice("Which address should the receipt go to?", criteria) },
});
```

See [Pre-parsed value extraction](cookbooks/pre_parsed_value_extraction_cookbook.md).

### Do I always need a confidence threshold?

No. If you only need the best option, use `choice`. If you have a statistical method in mind, use `probabilities` directly.

### Why did my results change with no code change?

`jev-latest` is an alias that moves when a new version ships. Log `response.model`, and pin a version once your thresholds are tuned:

**Python**

```python
client = TypeSafeClient(model="jev-1.13.0")
```

**TypeScript**

<!-- ts-check:
import { TypeSafeClient } from "@typesafe-ai/sdk";
-->
```ts
const client = new TypeSafeClient({ defaultModel: "jev-1.13.0" });
```

### I'm getting 429s

You've hit the rate limit (tokens per second or requests per second). The SDKs retry automatically with backoff and honor `retry-after`. Tune the retries, or cap your concurrency:

**Python**

```python
client = TypeSafeClient(retry=RetryPolicy(max_retries=5, backoff_initial=1.0, backoff_max=20.0))
sem = asyncio.Semaphore(8)  # with AsyncTypeSafeClient
```

**TypeScript**

<!-- ts-check run:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
const messages = ["a", "b", "c"];
const QUESTIONS = { billing: noul("Is this about billing?") };
-->
```ts
const client = new TypeSafeClient({ retry: { maxRetries: 5, backoffInitialMs: 1_000, backoffMaxMs: 20_000 } });

// Cap concurrency yourself, e.g. with a small worker pool:
async function mapLimit<T, R>(items: T[], limit: number, fn: (x: T) => Promise<R>): Promise<R[]> {
  const out: R[] = new Array(items.length);
  let next = 0;
  const worker = async () => {
    while (next < items.length) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  };
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
}

const results = await mapLimit(messages, 8, (m) => client.systemOne({ state: m, questions: QUESTIONS }));
```

### I'm getting 422 Unprocessable Entity

The request body failed validation. Common causes are an empty `questions` map, a Score with fewer than 2 or more than 10 levels, more than 255 Choice options, or a missing `type`. Inspect the body:

**Python**

```python
except TypeSafeUnprocessableEntityError as e:
    print(e.body)        # names the offending field
```

**TypeScript**

<!-- ts-check:
import { noul, TypeSafeClient, UnprocessableEntityError } from "@typesafe-ai/sdk";
const client = new TypeSafeClient();
const state = "x";
const questions = { q: noul("y") };
-->
```ts
try {
  await client.systemOne({ state, questions });
} catch (err) {
  if (err instanceof UnprocessableEntityError) console.error(err.body); // names the offending field
  else throw err;
}
```

### Can I use Jev through OpenRouter, Vercel, or Pydantic AI Gateway?

Yes. Point `base_url` at the gateway. See [Python SDK → AI gateways](10-sdk-python.md#ai-gateways-custom-base_url).

### Can I call it from the browser?

The JS SDK refuses by default, because it would expose your API key. `dangerouslyAllowBrowser: true` overrides that. Prefer a server-side proxy.

### Is my data used for training? Can I fine-tune?

Jev isn't trained on customer requests or responses, and enterprise customers can get zero data retention. There's no per-account fine-tuning. Customize through `state`, `instructions`, `criteria`, and composition in code. See [Models](12-models.md#customizing-jev).

### Is non-English text supported?

Yes, but accuracy is best in English. Test on your own data and watch the confidence values.

### The agent invents request or response fields

The installed skill is stale. Update it:

```bash
claude plugin marketplace update typesafe-ai && claude plugin update typesafe@typesafe-ai
```

---

[← 14. Cheat sheet](14-cheatsheet.md) · [Back to README](../README.md)
