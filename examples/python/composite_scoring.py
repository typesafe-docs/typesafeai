"""Composite scoring: rank resumes for two roles from four atomic Scores.

Weights live in code — change a coefficient, not a prompt.
"""

from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import Score, TypeSafeClient

QUESTIONS = {
    "python_depth": Score(
        instructions="How much depth of python experience does this candidate have, based on the supplied resume?",
        criteria=[
            "No Python experience mentioned",
            "Mentioned but no detail",
            "Used in projects, some specifics",
            "Primary language, multiple projects",
            "Deep expertise: architecture, performance, libraries",
        ],
    ),
    "team_leadership": Score(
        instructions="How much experience does this candidate have managing or leading engineering teams?",
        criteria=[
            "No management experience mentioned",
            "Informal mentorship or tech lead role",
            "Led a small team or project",
            "Managed a team with direct reports",
            "Managed multiple teams or an engineering org",
        ],
    ),
    "system_design": Score(
        instructions="How much experience does this candidate have designing large-scale or distributed systems?",
        criteria=[
            "No architecture work mentioned",
            "Contributed to design discussions",
            "Designed components of a larger system",
            "Owned architecture of a significant system",
            "Designed systems at scale across multiple domains",
        ],
    ),
    "generalist": Score(
        instructions="How much evidence is there that this candidate picks up unfamiliar tools, roles, or domains outside their core specialty?",
        criteria=[
            "Only one domain or role mentioned",
            "Some variety but within a narrow field",
            "Worked across a few different areas or tech stacks",
            "Regularly moved between domains, wore many hats",
            "Track record of ramping up in unfamiliar areas and delivering",
        ],
    ),
}

WEIGHTS = {
    "senior_ic": {"python_depth": 0.40, "team_leadership": 0.10, "system_design": 0.40, "generalist": 0.10},
    "eng_manager": {"python_depth": 0.15, "team_leadership": 0.40, "system_design": 0.20, "generalist": 0.25},
}

RESUMES = {
    "alice": "10 years Python, core contributor to a async web framework, designed the payments platform at a fintech handling 5k rps.",
    "bob": "Engineering manager for 3 teams (22 reports). Previously Java backend dev, some Python scripting. Moved from QA to infra to product.",
    "carol": "Data analyst, SQL and Excel. Took a Python course last year.",
}


def evaluate(client: TypeSafeClient, resume: str) -> dict[str, float]:
    answers = client.system_one(state=resume, questions=QUESTIONS).scores
    # Normalize each score to 0..1 by its top level number
    return {k: answers[k].score / (len(q.criteria) - 1) for k, q in QUESTIONS.items()}


if __name__ == "__main__":
    with TypeSafeClient() as client, ThreadPoolExecutor(max_workers=4) as pool:
        dims = dict(zip(RESUMES, pool.map(lambda r: evaluate(client, r), RESUMES.values())))

    for role, weights in WEIGHTS.items():
        ranked = sorted(dims, key=lambda name: -sum(w * dims[name][k] for k, w in weights.items()))
        print(role, "->", ranked)
