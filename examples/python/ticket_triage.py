"""Speculative fan-out + confidence-gated routing for support tickets.

All questions go out in ONE request; code decides which answers matter.
Questions and thresholds live at the top of the file so they are easy to review.
"""

from typesafe_sdk import Choice, Noul, Question, Score, TypeSafeClient

# --------------------------------------------------------------------------- questions
QUESTIONS: dict[str, Question] = {
    "category": Choice(
        instructions="Determine the broad category of this support ticket",
        criteria={
            "bug_report": "The user is reporting something that is broken or producing errors",
            "billing": "Charges, invoices, refunds, subscriptions",
            "feature_request": "The user is requesting new functionality",
            "account": "Login, permissions, profile, security",
        },
    ),
    # speculative: only matters for bug reports
    "bug_severity": Score(
        instructions="How severe is the reported issue",
        criteria=[
            "Cosmetic; no impact to functionality",
            "Broken or degraded feature; workaround exists",
            "Blocking issue; no workaround exists",
        ],
    ),
    "has_reproducible_steps": Noul(
        instructions="The user describes specific steps to reproduce the issue",
    ),
    # speculative: only matters for billing
    "refund_requested": Noul(
        instructions="The user is explicitly asking for a refund or credit",
    ),
    "frustration": Score(
        instructions="How frustrated the user appears",
        criteria=["Calm, matter-of-fact", "Frustrated but civil", "Very angry"],
    ),
}

# --------------------------------------------------------------------------- thresholds
CATEGORY_MIN_CONFIDENCE = 0.5
HIGH_SEVERITY = 1.5
REPRO_YES = 0.6
REFUND_YES = 0.7
PRIORITY_FRUSTRATION = 1.5


def triage(client: TypeSafeClient, ticket: str) -> list[str]:
    r = client.system_one(state=ticket, questions=QUESTIONS)
    # Typed accessors (r.choices / r.scores / r.nouls) keep mypy and your IDE happy
    actions: list[str] = []

    category = r.choices["category"]
    if category.confidence < CATEGORY_MIN_CONFIDENCE:
        actions.append(f"manual_triage (category confidence {category.confidence:.2f})")
    elif category.choice == "bug_report":
        if (
            r.scores["bug_severity"].score > HIGH_SEVERITY
            and r.nouls["has_reproducible_steps"].noul > REPRO_YES
        ):
            actions.append("escalate_to_engineering(severity=high)")
        else:
            actions.append("add_to_bug_backlog")
    elif category.choice == "billing":
        refund_likely = r.nouls["refund_requested"].noul > REFUND_YES
        actions.append(f"route_to_billing(refund_likely={refund_likely})")
    elif category.choice == "feature_request":
        actions.append("log_feature_request")
    else:
        actions.append("route_to_account_support")

    # Frustration is useful regardless of category
    if r.scores["frustration"].score > PRIORITY_FRUSTRATION:
        actions.append("flag_for_priority_response")

    return actions


TICKETS = [
    "The export button crashes the settings page in Safari. Steps: open settings, click Export. "
    "Nothing works and I'm furious, this is the third time.",
    "I was charged twice for my subscription this month. Please refund the duplicate.",
    "Would love a dark mode option!",
]

if __name__ == "__main__":
    with TypeSafeClient() as client:
        for t in TICKETS:
            print(f"{t[:60]!r:65} -> {triage(client, t)}")
