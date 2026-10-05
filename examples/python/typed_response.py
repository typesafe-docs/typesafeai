"""Typed responses with pydantic via `response_model=` (typesafe-sdk >= 0.7.0)."""

from typesafe_sdk import (
    ChoiceAnswer,
    Choice,
    Noul,
    NoulAnswer,
    SystemOneResponse,
    TypeSafeAPIError,
    TypeSafeClient,
)


class TicketResponse(SystemOneResponse):
    billing: NoulAnswer
    tone: ChoiceAnswer


def main() -> None:
    with TypeSafeClient() as client:
        try:
            result = client.system_one(
                "I was charged twice and nobody is answering my emails!",
                {
                    "billing": Noul(instructions="Is this about billing?"),
                    "tone": Choice(
                        instructions="What is the customer's tone?",
                        criteria={"calm": None, "frustrated": None, "angry": None},
                    ),
                },
                response_model=TicketResponse,
            )
        except TypeSafeAPIError as error:
            print("API error", error.status, error.request_id)
            raise

    print(result.billing.noul, result.tone.choice, result.request_id)


if __name__ == "__main__":
    main()
