// npm install && TYPESAFE_API_KEY=... npm run quickstart
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient(); // reads TYPESAFE_API_KEY, defaults to jev-latest

const { answers, model, usage } = await client.systemOne({
  state:
    "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
  questions: {
    department: choice("Which team should handle this", {
      billing: "Payment or subscription issues",
      technical: "Bugs or integration problems",
      sales: "Pricing or account questions",
    }),
    frustration: score("How frustrated the customer appears", [
      "Calm, just stating facts",
      "Frustrated but civil",
      "Very angry, strong language",
    ]),
    is_urgent: noul("The message conveys urgency or time-sensitivity"),
  },
});

// answers.department.choice is typed as "billing" | "technical" | "sales"
console.log("model:      ", model);
console.log("department: ", answers.department.choice, answers.department.confidence);
console.log("frustration:", answers.frustration.score, answers.frustration.confidence);
console.log("is_urgent:  ", answers.is_urgent.noul);
console.log("usage:      ", usage);
