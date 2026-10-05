"""Classify many messages concurrently with the async client (+ optional HTTP/2)."""

import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulCriteria, RetryPolicy

QUESTIONS = {
    "wants_human": Noul(instructions="Is the customer asking for a human agent?"),
    "repeat_contact": Noul(
        instructions="Has the customer contacted support about this before?",
        criteria=NoulCriteria(
            true="Mentions a prior attempt, ticket, or that they have asked before",
            false="No sign of any previous contact",
        ),
    ),
}

YES, NO = 0.8, 0.2

MESSAGES = [
    "Thanks, that fixed it!",
    "How do I reset my password?",
    "Are you a bot?",
    "I have asked three times now. Can I please just talk to a real person?",
]


def route(wants_human: float, repeat: float) -> str:
    if NO < wants_human < YES or NO < repeat < YES:
        return "review"  # the model isn't sure either way
    priority = "high" if repeat > YES else "normal"
    return f"agent/{priority}" if wants_human > YES else f"bot/{priority}"


async def main() -> None:
    # For HTTP/2: pip install 'typesafe-sdk[http2]' and pass
    # http_client=httpx2.AsyncClient(http2=True)
    async with AsyncTypeSafeClient(retry=RetryPolicy(max_retries=4)) as client:
        sem = asyncio.Semaphore(8)

        async def one(msg: str) -> tuple[str, str]:
            async with sem:
                r = await client.system_one(msg, QUESTIONS)
                return msg, route(r.nouls["wants_human"].noul, r.nouls["repeat_contact"].noul)

        for msg, decision in await asyncio.gather(*(one(m) for m in MESSAGES)):
            print(f"{decision:12} {msg}")


if __name__ == "__main__":
    asyncio.run(main())
