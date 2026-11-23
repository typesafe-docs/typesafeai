# 11. JavaScript / TypeScript SDK

[← Back to README](../README.md) · 📚 **[Full generated API reference](reference/javascript/README.md)** · Sources: <https://docs.typesafe.ai/sdk/javascript> · <https://docs.typesafe.ai/sdk/javascript/api> · GitHub: <https://github.com/typesafe-ai/typesafe-sdk-js>

Ships ESM, CommonJS, and TypeScript declarations. **Answer types are inferred from your questions.** Requires Node.js 22 or later (since v0.7.0).

## Install

```bash
npm install @typesafe-ai/sdk
export TYPESAFE_API_KEY="..."
```

## Quick start

```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    category: choice("What is this ticket about?", {
      billing: null,
      technical: null,
      other: null,
    }),
  },
});

console.log(response.answers.category.choice); // "billing" | "technical" | "other"
```

## Question builders

```ts
import { box, choice, noul, score } from "@typesafe-ai/sdk";

// choice(instructions, criteria): criteria maps labels to descriptions, or null
choice("Which team should handle this?", {
  returns: "Exchanges, wrong or damaged items",
  shipping: "Delivery status, delays, lost packages",
  billing: null,
});

// score(instructions, criteria): an ordered list with at least 2 entries (entries may be null)
score("How severe is the reported issue?", [
  "Cosmetic; no impact to functionality",
  "Broken or degraded feature, but workaround exists",
  "Blocking issue; no workaround exists",
]);

// noul(instructions, criteria?): optional true/false descriptions
// (or noul(null, criteria) with criteria alone; a bare noul() doesn't type-check)
noul("Is the customer asking for a human agent?");
noul("Has the customer contacted support before?", {
  true: "Mentions a prior attempt, ticket, or that they have asked before",
  false: "No sign of any previous contact",
});

// box(instructions): where something is in an image (Jev 1.14, needs images turned on)
box("the coffee mug in `photo`");
```

`instructions` and criteria values are `EntryType`s: a string, an `Image`, `withAssets` text, a JSON object or array, or `null`.

<!-- ts-check:
import { noul } from "@typesafe-ai/sdk";
-->
```ts
noul({
  potential_duplicate: { name: "John Smith", location: "Oakland, California", last_employer: "Google" },
  question: "Is the resume for the same person as `potential_duplicate`?",
});
```

## Mixed request with inferred types

```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const { answers, model, usage } = await client.systemOne({
  state: {
    ticket_message: "My flight was cancelled. Can I get a refund?",
    refund_policy: "Cancelled flights are eligible for a full refund.",
  },
  questions: {
    refund_requested: noul("Does `ticket_message` request a refund?"),
    request_type: choice("What is the main request in `ticket_message`?", {
      refund: "The customer wants money returned.",
      rebooking: "The customer wants a replacement flight.",
      information: "The customer is asking for information only.",
    }),
    frustration: score("How frustrated does the customer appear in `ticket_message`?", [
      "Calm and neutral.",
      "Concerned but civil.",
      "Very angry or using strong language.",
    ]),
  },
});

answers.refund_requested.noul;          // number
answers.request_type.choice;            // "refund" | "rebooking" | "information"
answers.request_type.probabilities;     // Record<"refund" | "rebooking" | "information", number>
answers.request_type.confidence;        // number
answers.frustration.score;              // number
answers.frustration.legend;             // level -> description
console.log(model, usage.input_tokens, usage.output_tokens); // number | null (since v0.7.0)
```

## Routing by probability in TypeScript

Act on the probability of the option you're about to act on, with a higher bar for riskier actions. See [Routing by probability](07-patterns.md#routing-by-probability).

<!-- ts-check:
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient; declare const userMessage: string;
declare function routeToSupportAgent(): void; declare function showBalance(): void;
declare function showTransferForConfirmation(): void; declare function askUserToClarify(q: string): void;
-->
```ts
const { answers } = await client.systemOne({
  state: userMessage,
  questions: {
    intent: choice("What action is the user requesting?", {
      check_balance: "Check the balance of an account",
      approve_transfer: "Approve the pending transfer request",
      other: "Something else",
    }),
  },
});

const intent = answers.intent;
const likelihood = intent.probabilities[intent.choice];

if (likelihood < 0.7) routeToSupportAgent(); // the message didn't settle the intent
else if (intent.choice === "check_balance") showBalance(); // low stakes
else if (intent.choice === "approve_transfer") {
  // Identifying the intent starts confirmation; it never approves a transfer by itself.
  if (likelihood > 0.9) showTransferForConfirmation();
  else askUserToClarify("Would you like to review the pending transfer?");
} else routeToSupportAgent();
```

## Images

Images and `box` questions are experimental and need the `TypeSafe-Danger-Zone-Images: true` header, on the client or per call (`{ headers: ... }`). Requests with images are sent as `multipart/form-data`. See [Images](04-primitives/images.md) for formats and limits, and [Box](04-primitives/box.md).

<!-- ts-check -->
```ts
import { readFile } from "node:fs/promises";
import { openAsBlob } from "node:fs";
import { box, image, Image, noul, TypeSafeClient, withAssets } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultHeaders: { "TypeSafe-Danger-Zone-Images": "true" } });
const photo = image(await openAsBlob("returns/RMA-1042.jpg")); // also: ArrayBuffer, typed array, or Image.fromBase64(text)
const catalog = Image.fromBase64((await readFile("catalog/mug.png")).toString("base64"));

// 1. Directly in the content
await client.systemOne({
  state: { claim: "The mug arrived with a chipped rim.", photo },
  questions: { damaged: noul("Is the product in `photo` damaged?"), damage: box("The damaged area of the product in `photo`") },
});

// 2. Inside text: tag the template with withAssets (an image in an untagged template rejects before sending)
await client.systemOne({
  state: withAssets`A customer returned ${photo}. The catalog photo is ${catalog}.`,
  questions: { same: noul(withAssets`Does ${photo} show the same product as ${catalog}?`) },
});

// 3. Under names you choose; every name must appear in the request
await client.systemOne({
  state: "A customer returned <delivered>. The catalog photo is <catalog>.",
  questions: { matches: noul("Is <delivered> the product shown in <catalog>?") },
  assets: { "<delivered>": photo, "<catalog>": catalog },
});
```

For a list of images in text, `withAssets.join(images, ", ")` interpolates them with a separator.

## Listing models

<!-- ts-check:
import { TypeSafeClient } from "@typesafe-ai/sdk"; declare const client: TypeSafeClient;
-->
```ts
const models = await client.models.list();
for (const model of models) {
  console.log(model.name, model.release_date, model.description);
}
```

## Client configuration (`TypeSafeClientConfig`)

Explicit options win over environment variables, which win over SDK defaults.

<!-- ts-check:
import { TypeSafeClient } from "@typesafe-ai/sdk";
-->
```ts
const client = new TypeSafeClient({
  apiKey: process.env.TYPESAFE_API_KEY,     // falls back to TYPESAFE_API_KEY
  baseURL: "https://api.typesafe.ai",       // falls back to TYPESAFE_BASE_URL
  defaultModel: "jev-latest",               // falls back to TYPESAFE_DEFAULT_MODEL
  timeout: 10_000,                          // ms per attempt (default 10000)
  logLevel: "warn",                         // falls back to TYPESAFE_LOG_LEVEL; "info" | "debug" | ...
  defaultHeaders: { "x-app": "triage" },
  retry: { maxRetries: 4 },                 // Partial<RetryPolicy>
  // compression: false,                   // default: zstd for bodies ≥ 1 KiB on Node ≥ 22.15; an explicit "zstd" throws on older Node
  // fetch: customFetch,                    // custom transport or tests
  // logger: myLogger,                      // default: prefixed console
  // dangerouslyAllowBrowser: true,         // exposes your API key to page users!
});
```

## Per-request options (`RequestOptions`)

<!-- ts-check:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient; declare const traceId: string; declare const state: string;
const questions = { q: noul("x") };
-->
```ts
const controller = new AbortController();

const result = await client.systemOne(
  { state, questions, model: "jev-1.14.0" },   // per-request model override
  {
    timeout: 5_000,
    retry: { maxRetries: 0 },
    headers: { "x-trace-id": traceId },
    signal: controller.signal,                 // cancels the request and any pending retries
  },
);
```

## Retry policy (`RetryPolicy`)

| Field | Default |
|---|---|
| `maxRetries` | `2` (`0` disables retries) |
| `backoffInitialMs` | `500`, doubled up to `backoffMaxMs` |
| `backoffMaxMs` | `5000` |
| `backoffJitter` | `0.25` |
| `httpStatuses` | `408`, `429`, `500–599` |
| `respectRetryAfter` | `true` (honors `Retry-After` and `retry-after-ms`) |
| `maxRetryAfterMs` | `60000` |
| `apiConnectionError` | `true` |
| `apiTimeoutError` | `true` |

### Timeouts

`timeout` (default `10000` ms) limits **each attempt**. Unlike the Python SDK, there's no total retry budget, so with the defaults a call can take up to 3 attempts × 10 s plus backoff. To cap the whole call, pass an `AbortSignal`; aborting also cancels pending retries:

<!-- ts-check run:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
const client = new TypeSafeClient();
const state = "I was charged twice.";
const questions = { billing: noul("Is this about billing?") };
-->
```ts
// Interactive path: at most ~3 s end to end, however many retries that allows
const result = await client.systemOne(
  { state, questions },
  { timeout: 2_000, retry: { maxRetries: 1 }, signal: AbortSignal.timeout(3_000) },
);
console.log(result.answers.billing.noul);
```

## Raw HTTP response access (`APIPromise`)

`systemOne()` returns an `APIPromise`, a `Promise` with extra methods:

<!-- ts-check:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient; declare const state: string;
const questions = { q: noul("x") };
-->
```ts
// Parsed result, raw Response, and request ID
const { data, response, requestId } = await client
  .systemOne({ state, questions })
  .withResponse();

// Raw Response only (you own the body)
const raw = await client.systemOne({ state, questions }).asResponse();

// Transform while sharing a single parse
const noulValue = await client
  .systemOne({ state, questions: { billing: noul("Is this about billing?") } })
  .map((r) => r.answers.billing.noul);
```

## Errors

<!-- ts-check:
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
declare const client: TypeSafeClient; declare const state: string;
const questions = { q: noul("x") };
-->
```ts
import {
  TypeSafeError,             // base
  APIError,                  // .status .body .headers .requestId
  BadRequestError,           // 400
  AuthenticationError,       // 401
  PermissionDeniedError,     // 403
  NotFoundError,             // 404
  UnprocessableEntityError,  // 422
  RateLimitError,            // 429
  InternalServerError,       // 5xx
  APIConnectionError,
  APITimeoutError,
  APIUserAbortError,
} from "@typesafe-ai/sdk";

try {
  await client.systemOne({ state, questions });
} catch (err) {
  if (err instanceof RateLimitError) {
    console.warn("rate limited", err.requestId);
  } else if (err instanceof UnprocessableEntityError) {
    console.error("bad question", err.body);
  } else if (err instanceof APIError) {
    console.error(err.status, err.requestId);
  } else if (err instanceof APITimeoutError) {
    console.error("timed out");
  } else {
    throw err;
  }
}
```

`systemOne()` also rejects (since v0.7.0 it rejects the returned promise instead of throwing) before any request is sent, if `questions` is empty, a score's criteria aren't a list of at least two entries, a named asset isn't referenced, or an image sits in an untagged template.

## Typing tips

**Inline or `const` question maps get exact answer types.** `systemOne` infers each answer from its question, including the literal option names of a Choice:

<!-- ts-check run -->
```ts
import { choice, noul, TypeSafeClient } from "@typesafe-ai/sdk";

const QUESTIONS = {
  department: choice("Which team should handle this?", { billing: null, technical: null }),
  urgent: noul("Does the message convey urgency?"),
};

const { answers } = await new TypeSafeClient().systemOne({ state: "Payouts are failing!", questions: QUESTIONS });
answers.department.choice; // "billing" | "technical"
answers.urgent.noul;       // number
```

**Dynamic maps of one kind** (built in a loop) type as a record of that kind, so every answer has the same shape:

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient, type NoulQuestion } from "@typesafe-ai/sdk";

const checks: Record<string, NoulQuestion> = Object.fromEntries(
  ["is_spam", "is_urgent"].map((k) => [k, noul(`Does the message look ${k.slice(3)}?`)]),
);
const { answers } = await new TypeSafeClient().systemOne({ state: "Win a prize now!", questions: checks });
Object.values(answers).map((a) => a.noul); // NoulResponse for every key
```

**Mixed dynamic maps** (`Record<string, Question>`) produce a union, so narrow on `type` first:

```ts
import { TypeSafeClient, type Question } from "@typesafe-ai/sdk";

declare const questions: Record<string, Question>;
const { answers } = await new TypeSafeClient().systemOne({ state: "...", questions });

for (const [key, a] of Object.entries(answers)) {
  if (a.type === "noul") console.log(key, a.noul);
  else if (a.type === "choice") console.log(key, a.choice, a.confidence);
  else if (a.type === "score") console.log(key, a.score, a.legend);
  else console.log(key, a.box, a.confidence); // box: edges as fractions of the image
}
```

**Use `satisfies` to keep literal types while validating the shape:**

<!-- ts-check run -->
```ts
import { choice, score, type Question } from "@typesafe-ai/sdk";

const QUESTIONS = {
  tone: choice("What is the tone?", { calm: null, angry: null }),
  severity: score("How severe is it?", ["Cosmetic", "Degraded", "Blocking"]),
} satisfies Record<string, Question>;
```

**`state` must be JSON-shaped (`EntryType`).** Object literals and `type` aliases work. Values typed with an `interface` may be rejected because interfaces have no index signature. Spread them into a literal, or declare a `type` alias instead:

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

type Ticket = { id: string; message: string }; // ✅ a `type` alias is assignable to EntryType
const ticket: Ticket = { id: "T-1", message: "I was charged twice." };

await new TypeSafeClient().systemOne({
  state: { ticket }, // ✅
  questions: { billing: noul("Is `ticket.message` about billing?") },
});
```

## Concurrency

Each `systemOne` call is independent, so fan out with `Promise.all`. Cap the concurrency when you're processing large batches, to stay under rate limits:

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const QUESTIONS = { wants_human: noul("Is the customer asking for a human agent?") };
const messages = ["Thanks, that fixed it!", "Can I please talk to a real person?"];

// Small batches: everything at once
const all = await Promise.all(messages.map((m) => client.systemOne({ state: m, questions: QUESTIONS })));

// Large batches: at most `limit` requests in flight
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

const capped = await mapLimit(messages, 8, (m) => client.systemOne({ state: m, questions: QUESTIONS }));
console.log(capped.map((r) => r.answers.wants_human.noul));
```

## AI gateways (custom `baseURL`)

The JS SDK sends requests to `${baseURL}/v1/systemone` with a `Bearer` key, exactly like the Python SDK. That means the [gateway settings from the Python guide](10-sdk-python.md#ai-gateways-custom-base_url) carry over unchanged:

```ts
import { TypeSafeClient } from "@typesafe-ai/sdk";

// OpenRouter
const openrouter = new TypeSafeClient({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: "https://openrouter.ai/api",
  defaultModel: "~typesafe/jev-latest",
});

// Vercel AI Gateway
const vercel = new TypeSafeClient({
  apiKey: process.env.AI_GATEWAY_API_KEY,
  baseURL: "https://ai-gateway.vercel.sh/typesafe",
  defaultModel: "typesafe-ai/jev",
});

// Pydantic AI Gateway
const pydantic = new TypeSafeClient({
  apiKey: process.env.PYDANTIC_AI_GATEWAY_API_KEY,
  baseURL: "https://gateway-us.pydantic.dev/proxy/typesafe",
  defaultModel: "jev-latest",
});
```

## Logging

Set `logLevel` (or `TYPESAFE_LOG_LEVEL`) to `debug`, `info`, `warn` (the default), `error`, or `off`. `info` logs a summary per request, and `debug` adds headers and bodies. Known credential headers are redacted, but **bodies are not**. You can plug in your own logger:

```ts
import { TypeSafeClient, type Logger } from "@typesafe-ai/sdk";

const logger: Logger = {
  debug: (msg, ...args) => console.debug("[typesafe]", msg, ...args),
  info: (msg, ...args) => console.info("[typesafe]", msg, ...args),
  warn: (msg, ...args) => console.warn("[typesafe]", msg, ...args),
  error: (msg, ...args) => console.error("[typesafe]", msg, ...args),
};

const client = new TypeSafeClient({ logLevel: "info", logger });
```

## Environment variables

| Variable | Configures | Default |
|---|---|---|
| `TYPESAFE_API_KEY` | API key (required) | — |
| `TYPESAFE_BASE_URL` | API root | `https://api.typesafe.ai` |
| `TYPESAFE_DEFAULT_MODEL` | Default model | `jev-latest` |
| `TYPESAFE_LOG_LEVEL` | Log level | `warn` |

Explicit constructor options take precedence over environment variables. Empty or whitespace-only values are ignored. The names are exported as `ENV`:

```ts
import { ENV } from "@typesafe-ai/sdk";

ENV.apiKey;       // "TYPESAFE_API_KEY"
ENV.baseURL;      // "TYPESAFE_BASE_URL"
ENV.defaultModel; // "TYPESAFE_DEFAULT_MODEL"
ENV.logLevel;     // "TYPESAFE_LOG_LEVEL"
```

## Testing without the API

Point `baseURL` at the [offline mock server](../examples/mock/mock_server.py) in this repo. Or inject a `fetch` stub, which is handy in unit tests. Turn compression off so the stub sees plain JSON (bodies of 1 KiB or more are zstd-compressed by default, and image requests are multipart):

<!-- ts-check run -->
```ts
import { noul, TypeSafeClient, type Fetch } from "@typesafe-ai/sdk";

const fakeFetch: Fetch = async (_url, init) => {
  const body = JSON.parse(String(init?.body));
  const answers = Object.fromEntries(Object.keys(body.questions).map((k) => [k, { type: "noul", noul: 0.9 }]));
  return new Response(JSON.stringify({ model: "jev-1.14.0", answers, usage: { input_tokens: 1, output_tokens: 1 } }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
};

const client = new TypeSafeClient({ apiKey: "test", fetch: fakeFetch, compression: false });
const { answers } = await client.systemOne({ state: "x", questions: { billing: noul("Is this about billing?") } });
console.log(answers.billing.noul); // 0.9
```

## Exported utilities

```ts
import { ENV, LOG_LEVELS, VERSION } from "@typesafe-ai/sdk";
console.log(VERSION, ENV, LOG_LEVELS);
```

Type helpers include `ResultFor<Q>`, `ScoreOf<T>`, `ScoreLegend<T>`, `ChoiceCriteria`, `ScoreCriteria`, `EntryType`, `ContentValue`, `JsonValue`, `Asset`, `TextWithAssets`, `BoxQuestion`, `BoxResponse`, `BoxCoordinates`, `Compression`, `SystemOneRequest<Q>`, and `SystemOneResult<Q>`. Request payload types are no longer exported (v0.7.0).

## Changelog

| Version | Date | Change |
|---|---|---|
| v0.7.0 | 2026-10-14 | **Breaking:** requires Node.js 22; request payload types no longer exported. Experimental [images](04-primitives/images.md) (`image()`, `Image.fromBase64()`, `withAssets`, `assets`) and [`box()`](04-primitives/box.md) questions; zstd compression for bodies ≥ 1 KiB on Node ≥ 22.15 (`compression: false` to opt out). Fixes: null token counts allowed, more request validation, invalid requests reject instead of throwing, runtime-built score criteria accepted. |
| v0.6.0 | 2026-09-15 | **Breaking:** `score()` criteria is an ordered list, not an integer-keyed object |
| v0.5.7 | 2026-09-11 | Initial public release |

---

[← 10. Python SDK](10-sdk-python.md) · Next: [12. Models →](12-models.md)
