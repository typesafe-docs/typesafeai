"""Double-check a citation: code checks the quote exists, one Choice judges support."""

from typesafe_sdk import Choice, TypeSafeClient

QUESTIONS = {
    "relation": Choice(
        instructions="How does the section relate to the claim?",
        criteria={
            "supports": "The section states the claim or directly implies that it is true",
            "contradicts": "The section states the opposite of the claim or implies it is false",
            "says_nothing": "The section does not address what the claim asserts, either way",
        },
    ),
}
VERDICT = {"supports": "verified", "contradicts": "contradicted", "says_nothing": "unsupported"}
AUTO_CONFIDENCE = 0.8

SOURCE = """Section 4.2. Refunds are available within 30 days of purchase for annual plans.
Monthly plans are not refundable but can be cancelled at any time."""


def check(claim: str, quote: str, client: TypeSafeClient) -> dict:
    if quote not in SOURCE:  # step 1, in code: does the cited text exist at all?
        return {"verdict": "fabricated", "confidence": None, "auto": True}
    a = client.system_one(state={"claim": claim, "section": SOURCE}, questions=QUESTIONS).choices["relation"]
    return {"verdict": VERDICT[a.choice], "confidence": round(a.confidence, 2), "auto": a.confidence >= AUTO_CONFIDENCE}


if __name__ == "__main__":
    with TypeSafeClient() as client:
        print(check("Annual plans can be refunded within a month.", "Refunds are available within 30 days", client))
        print(check("Monthly plans are refundable.", "Monthly plans are not refundable", client))
        print(check("Refunds take 5 days to process.", "Refunds are processed in 5 days", client))
