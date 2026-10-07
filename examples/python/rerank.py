"""Re-rank a keyword shortlist with one Noul per (query, candidate) pair; sort on the probability."""

from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient

IS_ANSWER = Noul(
    instructions="Does the candidate passage directly answer the query?",
    criteria=NoulCriteria(
        true="The candidate states the specific fact or rule the query asks for.",
        false="The candidate is only on a similar topic.",
    ),
)

QUERY = "Can I change the email address on my account?"
CANDIDATES = [
    "Email notifications can be turned off under Settings > Notifications.",
    "To update the email address on your account, go to Profile > Account details and click Edit.",
    "Our support team answers email within 24 hours.",
]


def score(client: TypeSafeClient, candidate: str) -> float:
    r = client.system_one(state={"query": QUERY, "candidate_passage": candidate}, questions={"is_answer": IS_ANSWER})
    return r.nouls["is_answer"].noul


if __name__ == "__main__":
    with TypeSafeClient() as client, ThreadPoolExecutor(8) as pool:
        scores = list(pool.map(lambda c: score(client, c), CANDIDATES))
    for s, c in sorted(zip(scores, CANDIDATES), reverse=True):
        print(f"{s:4.2f}  {c}")
