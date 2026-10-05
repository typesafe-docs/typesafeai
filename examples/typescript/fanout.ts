// Speculative fan-out: every question in one request, code decides what's relevant.
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const ticket =
  "Hi, I placed an order (#98423) last Thursday and was charged twice. I also can't log in after the site update, and adding Apple Pay would be really helpful. This is getting frustrating.";

const { answers } = await client.systemOne({
  state: ticket,
  questions: {
    category: choice("Determine the broad category of this support ticket", {
      bug_report: "The user is reporting something that is broken or producing errors",
      billing: "Charges, invoices, refunds, subscriptions",
      feature_request: "The user is requesting new functionality",
      account: "Login, permissions, profile, security",
    }),
    bug_severity: score("How severe is the reported issue", [
      "Cosmetic; no impact to functionality",
      "Broken or degraded feature; workaround exists",
      "Blocking issue; no workaround exists",
    ]),
    has_reproducible_steps: noul("The user describes specific steps to reproduce the issue"),
    refund_requested: noul("The user is explicitly asking for a refund or credit"),
    frustration: score("How frustrated the user appears", ["Calm, matter-of-fact", "Frustrated but civil", "Very angry"]),
  },
});

const actions: string[] = [];
switch (answers.category.choice) {
  case "bug_report":
    actions.push(
      answers.bug_severity.score > 1.5 && answers.has_reproducible_steps.noul > 0.6
        ? "escalate_to_engineering"
        : "add_to_bug_backlog",
    );
    break;
  case "billing":
    actions.push(answers.refund_requested.noul > 0.7 ? "billing+refund_flag" : "billing");
    break;
  case "feature_request":
    actions.push("log_feature_request");
    break;
  default:
    actions.push("account_support");
}
if (answers.frustration.score > 1.5) actions.push("priority_response");
console.log(answers.category.choice, answers.category.probabilities, actions);
