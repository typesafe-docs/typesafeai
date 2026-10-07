// Decomposed phishing detection with inferred types and weights in code.
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const message = {
  sender: { display_name: "Acme Payroll", email: "rewards@claim-bonus.example" },
  subject: "Urgent: claim your employee bonus",
  body: "You have been selected for a $1,000 bonus. Confirm your payroll password today to receive it.",
  links: [{ text: "Claim bonus", url: "http://claim-bonus.example/acme" }],
};

const questions = {
  requests_credentials: noul("Does `message.body` ask the recipient to provide a password or other login credential?"),
  offers_unexpected_reward: noul("Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"),
  creates_time_pressure: noul("Does `message.subject` or `message.body` pressure the recipient to act quickly?"),
  sender_identity_mismatch: noul("Does the organization named in `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
  link_domain_mismatch: noul("Does the domain in `message.links[0].url` conflict with the organization named in `message.sender.display_name`?"),
  disguises_link_destination: noul("Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"),
};

const weights: Record<keyof typeof questions, number> = {
  requests_credentials: 0.3,
  sender_identity_mismatch: 0.2,
  link_domain_mismatch: 0.2,
  offers_unexpected_reward: 0.1,
  creates_time_pressure: 0.1,
  disguises_link_destination: 0.1,
};

const { answers } = await client.systemOne({ state: { message }, questions });
const risk = (Object.keys(weights) as (keyof typeof questions)[]).reduce(
  (sum, k) => sum + weights[k] * answers[k].noul,
  0,
);
console.log({ risk: risk.toFixed(2), verdict: risk >= 0.6 ? "quarantine" : risk >= 0.4 ? "review" : "deliver" });
