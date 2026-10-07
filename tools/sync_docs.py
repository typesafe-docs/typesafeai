"""Regenerate docs/cookbooks/ and docs/reference/ from the official docs.typesafe.ai pages.

    python tools/sync_docs.py            # fetch fresh sources, then convert
    python tools/sync_docs.py --offline  # reuse tools/.cache

The hand-written guide (docs/01-*.md … docs/15-*.md) is not touched.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import mdx_to_gfm as convert

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(REPO, "tools", ".cache")


def fetch_sources() -> None:
    """Download every page listed in https://docs.typesafe.ai/llms.txt as Markdown into tools/.cache/md."""
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    os.makedirs(f"{SCR}/md", exist_ok=True)
    index = subprocess.run(["curl", "-sfL", "https://docs.typesafe.ai/llms.txt"], capture_output=True, text=True, check=True).stdout
    urls = sorted(set(re.findall(r"https://docs\.typesafe\.ai/[^)\s]+\.md", index)))

    def get(u: str) -> None:
        name = u.removeprefix("https://docs.typesafe.ai/").removesuffix(".md").replace("/", "_")
        subprocess.run(["curl", "-sfL", "-o", f"{SCR}/md/{name}.md", u], check=False)

    with ThreadPoolExecutor(12) as pool:
        list(pool.map(get, urls))
    print("fetched", len(urls), "pages")


if "--offline" not in sys.argv:
    fetch_sources()

# --------------------------------------------------------------------------- link map
CORE = {
    "/": "README.md",
    "/introduction": "docs/01-introduction.md",
    "/introduction/coding-agents": "docs/01-introduction.md#jev-and-coding-agents",
    "/introduction/machine-learning-primer": "docs/01-introduction.md#ai-primer-why-rlcd",
    "/concepts/system-one": "docs/01-introduction.md#system-one",
    "/concepts/use-case-map": "docs/01-introduction.md#example-use-case-categories",
    "/introduction/quickstart": "docs/02-quickstart.md",
    "/concepts/state": "docs/03-state.md",
    "/primitives": "docs/04-primitives/README.md",
    "/primitives/choice": "docs/04-primitives/choice.md",
    "/primitives/score": "docs/04-primitives/score.md",
    "/primitives/noul": "docs/04-primitives/noul.md",
    "/primitives/advanced": "docs/04-primitives/advanced-structure.md",
    "/confidence": "docs/05-confidence.md",
    "/concepts/how-to-build-with-system-one": "docs/06-building-with-typesafe.md",
    "/patterns": "docs/07-patterns.md",
    "/patterns/fan-out": "docs/07-patterns.md#speculative-fan-out",
    "/patterns/confidence-routing": "docs/07-patterns.md#confidence-gated-routing",
    "/patterns/composite-scoring": "docs/07-patterns.md#composite-scoring",
    "/patterns/intent-routing": "docs/07-patterns.md#intent-routing",
    "/cookbooks": "docs/08-cookbooks.md",
    "/demos": "docs/08-cookbooks.md#demo-smart-home-assistant",
    "/demos/smart-home": "docs/08-cookbooks.md#demo-smart-home-assistant",
    "/api": "docs/09-api-reference.md",
    "/sdk": "docs/10-sdk-python.md",
    "/sdk/python": "docs/10-sdk-python.md",
    "/sdk/javascript": "docs/11-sdk-javascript.md",
    "/models": "docs/12-models.md",
    "/model-jaggedness/jev-1.13": "docs/12-models.md#known-failure-modes-jev-113",
    "/agent-skill": "docs/13-agent-skill.md",
}
convert.LINKMAP.update(CORE)

COOKBOOKS = sorted(f[len("cookbooks_"):-3] for f in os.listdir(f"{SCR}/md") if f.startswith("cookbooks_"))
for c in COOKBOOKS:
    convert.LINKMAP[f"/cookbooks/{c}"] = f"docs/cookbooks/{c}.md"

PY = {
    "sdk_python_usage": ("usage.md", "/sdk/python/usage"),
    "sdk_python_api_clients_sync": ("sync-client.md", "/sdk/python/api/clients/sync"),
    "sdk_python_api_clients_async": ("async-client.md", "/sdk/python/api/clients/async"),
    "sdk_python_api_types_questions": ("questions.md", "/sdk/python/api/types/questions"),
    "sdk_python_api_types_responses": ("responses.md", "/sdk/python/api/types/responses"),
    "sdk_python_api_types_common": ("common-types.md", "/sdk/python/api/types/common"),
    "sdk_python_api_retries": ("retries.md", "/sdk/python/api/retries"),
    "sdk_python_api_exceptions": ("exceptions.md", "/sdk/python/api/exceptions"),
    "sdk_python_api_constants": ("constants.md", "/sdk/python/api/constants"),
    "sdk_python_changelog": ("changelog.md", "/sdk/python/changelog"),
}
for f, (out, path) in PY.items():
    convert.LINKMAP[path] = f"docs/reference/python/{out}"
convert.LINKMAP["/sdk/python/api"] = "docs/reference/python/README.md"
for p in ("/sdk/python/api/clients/sync/client", "/sdk/python/api/clients/sync/models"):
    convert.LINKMAP[p] = "docs/reference/python/sync-client.md"
for p in ("/sdk/python/api/clients/async/client", "/sdk/python/api/clients/async/models"):
    convert.LINKMAP[p] = "docs/reference/python/async-client.md"

JS_GROUPS = ["classes", "interfaces", "type-aliases", "functions", "variables"]
js_items = {g: [] for g in JS_GROUPS}
for f in sorted(os.listdir(f"{SCR}/md")):
    m = re.match(r"sdk_javascript_api_(classes|interfaces|type-aliases|functions|variables)_(.+)\.md$", f)
    if m:
        g, name = m.groups()
        js_items[g].append(name)
JS_TITLE = {"classes": "Class", "interfaces": "Interface", "type-aliases": "Type Alias", "functions": "Function", "variables": "Variable"}


def gh_anchor(h: str) -> str:
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


for g, names in js_items.items():
    for n in names:
        src = open(f"{SCR}/md/sdk_javascript_api_{g}_{n}.md").read()
        h1 = re.search(r"^# (.+)$", src, re.M).group(1)
        convert.LINKMAP[f"/sdk/javascript/api/{g}/{n}"] = f"docs/reference/javascript/{g}.md#{gh_anchor(h1)}"
convert.LINKMAP["/sdk/javascript/api"] = "docs/reference/javascript/README.md"
convert.LINKMAP["/sdk/javascript/changelog"] = "docs/reference/javascript/changelog.md"


def write(rel: str, text: str):
    path = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text.rstrip() + "\n")


def page(fname: str, rel: str, url: str, back: str, shift: int = 0) -> str:
    src = open(f"{SCR}/md/{fname}.md").read()
    body = convert.convert(src, rel, convert.SITE + url)
    if shift:
        body = re.sub(r"^(#{1,5}) ", lambda m: "#" * (len(m.group(1)) + shift) + " ", body, flags=re.M)
    return body


# --------------------------------------------------------------------------- cookbooks
cb_index = []
for c in COOKBOOKS:
    rel = f"docs/cookbooks/{c}.md"
    url = f"/cookbooks/{c}"
    body = page(f"cookbooks_{c}", rel, url, "")
    title = re.search(r"^# (.+)$", body, re.M).group(1)
    desc = re.search(r"^> (?!📝|💡|ℹ️|⚠️|🖼️|🧪)(.+)$", body, re.M)
    header = (
        f"[← Cookbooks](../08-cookbooks.md) · [README](../../README.md) · "
        f"Official: <{convert.SITE}{url}>\n\n"
    )
    body = body.replace(f"# {title}\n", f"# {title}\n\n{header}", 1)
    write(rel, body)
    n = len(re.findall(r"^```\w", body, re.M))
    cb_index.append((c, title, desc.group(1) if desc else "", n))

# --------------------------------------------------------------------------- python reference
py_index = []
for f, (out, url) in PY.items():
    rel = f"docs/reference/python/{out}"
    body = page(f, rel, url, "")
    title = re.search(r"^# (.+)$", body, re.M).group(1)
    header = f"[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <{convert.SITE}{url}>\n\n"
    body = body.replace(f"# {title}\n", f"# {title}\n\n{header}", 1)
    write(rel, body)
    py_index.append((out, title))

# --------------------------------------------------------------------------- js reference
for g, names in js_items.items():
    rel = f"docs/reference/javascript/{g}.md"
    parts = [
        f"# JavaScript SDK reference: {g.replace('-', ' ').title()}\n\n"
        f"[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <{convert.SITE}/sdk/javascript/api>\n\n"
        + "\n".join(f"- [{n}](#{gh_anchor(JS_TITLE[g] + ': ' + n)})" for n in names)
        + "\n"
    ]
    for n in names:
        body = page(f"sdk_javascript_api_{g}_{n}", rel, f"/sdk/javascript/api/{g}/{n}", "", shift=1)
        parts.append(body)
    text = "\n\n---\n\n".join(parts)

    # Generic names like ChoiceQuestion<T> would be eaten as HTML by GitHub: code-format them and
    # pin both anchor spellings ("interface-choicequestiont" and "interface-choicequestion").
    def _generic(m):
        hashes, kind, name = m.group(1), m.group(2), m.group(3)
        base = re.sub(r"<.*", "", name)
        a1 = gh_anchor(f"{kind}: {name}")
        a2 = gh_anchor(f"{kind}: {base}")
        return f'<a id="{a1}"></a><a id="{a2}"></a>\n\n{hashes} {kind}: `{name}`'
    text = re.sub(r"^(#{1,6}) (Class|Interface|Type Alias|Function|Variable): (\w+<[^>]+>)\s*$", _generic, text, flags=re.M)
    # anchors of the generic names were computed from H1 – fix any that differ
    write(rel, text)

write(
    "docs/reference/javascript/changelog.md",
    page("sdk_javascript_changelog", "docs/reference/javascript/changelog.md", "/sdk/javascript/changelog", "").replace(
        "# ", "# JavaScript SDK changelog\n\n[← JavaScript reference](README.md)\n\n<!-- -->\n# ", 1
    ).replace("\n<!-- -->\n# Changelog", "", 1),
)

import json

print("cookbooks", len(cb_index), "py", len(py_index), "js", {g: len(v) for g, v in js_items.items()})

import urllib.request
from concurrent.futures import ThreadPoolExecutor
def dl(item):
    dp, url = item
    dest = os.path.join(REPO, "docs/assets", dp)
    if os.path.exists(dest): return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    import subprocess
    subprocess.run(["curl","-sfL","-A","Mozilla/5.0","-o",dest,url],check=False)
with ThreadPoolExecutor(8) as p: list(p.map(dl, convert.IMAGES.items()))
print("images", len(convert.IMAGES))
