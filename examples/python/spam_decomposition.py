"""Decomposed spam/phishing detection: six atomic Nouls + weights in code.

Based on the official "Decompose the questions" example.
"""

from typing import Any

from typesafe_sdk import Noul, TypeSafeClient

MESSAGE: dict[str, Any] = {
    "sender": {"display_name": "Acme Payroll", "email": "rewards@claim-bonus.example"},
    "subject": "Urgent: claim your employee bonus",
    "body": "You have been selected for a $1,000 bonus. Confirm your payroll password today to receive it.",
    "links": [{"text": "Claim bonus", "url": "http://claim-bonus.example/acme"}],
}

QUESTIONS = {
    "requests_credentials": Noul(instructions="Does `message.body` ask the recipient to provide a password or other login credential?"),
    "offers_unexpected_reward": Noul(instructions="Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"),
    "creates_time_pressure": Noul(instructions="Does `message.subject` or `message.body` pressure the recipient to act quickly?"),
    "sender_identity_mismatch": Noul(instructions="Does the organization named in `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
    "link_domain_mismatch": Noul(instructions="Does the domain in `message.links[0].url` conflict with the organization named in `message.sender.display_name`?"),
    "disguises_link_destination": Noul(instructions="Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"),
}

WEIGHTS = {
    "requests_credentials": 0.30,
    "sender_identity_mismatch": 0.20,
    "link_domain_mismatch": 0.20,
    "offers_unexpected_reward": 0.10,
    "creates_time_pressure": 0.10,
    "disguises_link_destination": 0.10,
}
QUARANTINE, REVIEW = 0.6, 0.4

if __name__ == "__main__":
    with TypeSafeClient() as client:
        answers = client.system_one(state={"message": MESSAGE}, questions=QUESTIONS).nouls

    signals = {k: answers[k].noul for k in QUESTIONS}
    risk = sum(WEIGHTS[k] * v for k, v in signals.items())
    for k, v in sorted(signals.items(), key=lambda kv: -kv[1]):
        print(f"{v:5.2f}  {k}")
    verdict = "quarantine" if risk >= QUARANTINE else "review" if risk >= REVIEW else "deliver"
    print(f"\nspam risk {risk:.2f} -> {verdict}")
