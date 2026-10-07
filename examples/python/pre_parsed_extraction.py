"""Regex finds candidates; TypeSafe picks which one plays the role; code owns the string."""

import re

from typesafe_sdk import Choice, TypeSafeClient

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
NONE = "none"

THREAD = """From: dana@oldcompany.example
Hi! I've moved jobs, so please send the receipt for order #881 to dana.lee@newco.example
instead of my old address. You can cc accounts@newco.example if needed."""


def pick(client: TypeSafeClient, document: str, candidates: list[str], question: str) -> tuple[str | None, float]:
    criteria = {c: None for c in candidates} | {NONE: "None of these is the requested value."}
    a = client.system_one(
        state=document, questions={"pick": Choice(instructions=question, criteria=criteria)}
    ).choices["pick"]
    return (None if a.choice == NONE else a.choice.lower()), a.confidence


if __name__ == "__main__":
    candidates = list(dict.fromkeys(EMAIL_RE.findall(THREAD)))  # dedupe, keep order
    with TypeSafeClient() as client:
        value, conf = pick(client, THREAD, candidates, "Which email address does the sender want their receipt sent to?")
    print(candidates, "->", value, f"(confidence {conf:.2f})")
