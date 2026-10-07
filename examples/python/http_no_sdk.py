"""Call the System One API with plain `requests` (no SDK), including retry with backoff."""

import os
import random
import time

import requests

URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai").rstrip("/") + "/v1/systemone"
HEADERS = {"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}
RETRYABLE = {408, 429, 529}


def system_one(payload: dict, max_retries: int = 5) -> dict:
    delay = 0.5
    for attempt in range(max_retries + 1):
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        if r.ok:
            return r.json()
        if (r.status_code not in RETRYABLE and r.status_code < 500) or attempt == max_retries:
            raise RuntimeError(f"{r.status_code} {r.text} (request {r.headers.get('x-typesafe-request-id')})")
        retry_after = r.headers.get("retry-after")
        time.sleep(min(float(retry_after) if retry_after else delay * (1 - 0.25 * random.random()), 60))
        delay = min(delay * 2, 5)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    data = system_one({
        "state": "Help! My payouts have been failing for 3 days.",
        "model": "jev-latest",
        "questions": {
            "is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"},
            "department": {"type": "choice", "instructions": "Which team should handle this?",
                           "criteria": {"billing": "Payments, invoicing, refunds", "technical": "Bugs, outages, integrations"}},
        },
    })
    print(data["model"], data["answers"], data["usage"])
