"""Extract a date by its parts (Choices over closed sets); assemble and compare in code."""

from datetime import date

from typesafe_sdk import Choice, TypeSafeClient

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
TODAY = date(2026, 10, 7)
YEARS = [str(y) for y in range(TODAY.year - 2, TODAY.year + 3)]
ABSENT = "The document does not state this, or it is not this kind of date."
REVIEW_BELOW = 0.6


def questions(role: str) -> dict:
    return {
        "month": Choice(instructions=f"If {role} is an absolute calendar date, which month is it in?",
                        criteria={m: None for m in MONTHS} | {"none": ABSENT}),
        "day": Choice(instructions=f"If {role} is an absolute calendar date, which day of the month (1-31)?",
                      criteria={str(d): None for d in range(1, 32)} | {"none": ABSENT}),
        "year": Choice(instructions=f"If {role} is an absolute calendar date, which year? Pick 'none' if no year is stated.",
                       criteria={y: None for y in YEARS} | {"none": "No year is stated for this date."}),
    }


def extract(client: TypeSafeClient, document: str, role: str) -> dict:
    a = client.system_one(state=document, questions=questions(role)).choices
    if "none" in (a["month"].choice, a["day"].choice):
        return {"date": None, "needs_review": True}
    year = int(a["year"].choice) if a["year"].choice != "none" else TODAY.year  # code infers the year
    resolved = date(year, MONTHS.index(a["month"].choice) + 1, int(a["day"].choice))
    confidence = min(a[k].confidence for k in ("month", "day", "year"))
    return {"date": resolved, "confidence": round(confidence, 2), "needs_review": confidence < REVIEW_BELOW,
            "overdue": resolved < TODAY}  # comparison lives in code


if __name__ == "__main__":
    doc = "Invoice INV-2207. Payment is due on the 14th of August; late fees apply after that."
    with TypeSafeClient() as client:
        print(extract(client, doc, "the payment due date"))
