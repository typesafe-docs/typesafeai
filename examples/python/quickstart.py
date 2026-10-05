"""Quick start: one request, three question types.

    pip install -r requirements.txt
    export TYPESAFE_API_KEY=...
    python quickstart.py
"""

from typesafe_sdk import Choice, Noul, Question, Score, TypeSafeClient

TICKET = (
    "Hi, I've been trying to connect my Stripe account for 3 days and the integration "
    "keeps failing. I'm losing sales. Please help ASAP."
)

QUESTIONS: dict[str, Question] = {
    "department": Choice(
        instructions="Which team should handle this",
        criteria={
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    ),
    "frustration": Score(
        instructions="How frustrated the customer appears",
        criteria=[
            "Calm, just stating facts",
            "Frustrated but civil",
            "Very angry, strong language",
        ],
    ),
    "is_urgent": Noul(
        instructions="The message conveys urgency or time-sensitivity",
    ),
}


def main() -> None:
    with TypeSafeClient() as client:
        response = client.system_one(state=TICKET, questions=QUESTIONS)

    department = response.choices["department"]
    frustration = response.scores["frustration"]
    urgent = response.nouls["is_urgent"]

    print(f"model:       {response.model}")
    print(f"department:  {department.choice} (confidence {department.confidence:.2f})")
    print(f"             {dict(department.probabilities)}")
    print(f"frustration: {frustration.score:.2f} (confidence {frustration.confidence:.2f})")
    print(f"is_urgent:   {urgent.noul:.2f}")
    print(f"usage:       {response.usage.input_tokens} in / {response.usage.output_tokens} out")


if __name__ == "__main__":
    main()
