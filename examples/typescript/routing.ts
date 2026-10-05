// Intent routing with confidence gates and typed error handling.
import { APIError, choice, RateLimitError, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ retry: { maxRetries: 4 }, timeout: 5_000 });

const QUESTIONS = {
  intent: choice("The primary intent of this customer message", {
    order_status: "Asking about an existing order",
    product_question: "Asking about a product before buying",
    return_exchange: "Wants to return or exchange something",
    complaint: "Unhappy with experience, wants resolution",
  }),
  complexity: score("How complex is this request to resolve", [
    "Simple lookup or standard procedure",
    "Requires some judgment or multi-step process",
    "Unusual situation, edge case, or escalation needed",
  ]),
};

async function route(message: string): Promise<string> {
  const { answers } = await client.systemOne({ state: message, questions: QUESTIONS });
  const { intent, complexity } = answers;

  if (intent.confidence < 0.5) return "human_agent";

  switch (intent.choice) {
    case "order_status":
      return "order_lookup (deterministic)";
    case "product_question":
      return "llm:product_specialist";
    case "return_exchange":
      return "llm:returns_specialist";
    case "complaint":
      return complexity.score > 1 || complexity.confidence < 0.5 ? "human_agent" : "llm:complaint_resolution";
  }
}

const messages = [
  "Where is order #4471? It said it shipped Monday.",
  "Does the X200 blender come with a warranty?",
  "Your courier left my package in the rain, everything is ruined and I want compensation plus an apology from your CEO.",
];

for (const m of messages) {
  try {
    console.log((await route(m)).padEnd(32), m);
  } catch (err) {
    if (err instanceof RateLimitError) console.error("rate limited", err.requestId);
    else if (err instanceof APIError) console.error(err.status, err.requestId, err.body);
    else throw err;
  }
}
