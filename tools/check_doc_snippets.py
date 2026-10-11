"""Type-check (and optionally run) every TypeScript snippet in the guide.

Each ```ts block in README.md and docs/ (excluding the generated cookbooks/ and reference/) is
compiled as its own module against the real @typesafe-ai/sdk. A block can be preceded by a hidden
HTML comment that supplies type-only context (declarations of app helpers, sample variables):

    <!-- ts-check run:
    declare const ticket: string;
    -->
    ```ts
    ...
    ```

`run` marks a self-contained block that is also executed against TYPESAFE_BASE_URL (use the offline
mock in examples/mock/). Declared helpers are stubbed at runtime and `declare const x: string`
becomes a sample string.

    python3 tools/check_doc_snippets.py          # type-check only
    python3 tools/check_doc_snippets.py --run    # also run `run` blocks (needs the mock server)
"""

import json
import os
import re
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = os.path.join(REPO, "examples", "typescript")
WORK = os.path.join(TS, ".doc-snippets")
BLOCK = re.compile(r"(?:<!-- ts-check( run)?(?::\n(.*?)\n| )-->\n)?^```(?:ts|typescript)\n(.*?)^```", re.M | re.S)


def doc_files() -> list[str]:
    out = []
    for root, _, files in os.walk(os.path.join(REPO, "docs")):
        if re.search(r"docs/(cookbooks|reference|assets)", root):
            continue
        out += [os.path.join(root, f) for f in files if f.endswith(".md")]
    return [os.path.join(REPO, "README.md"), *sorted(out)]


def main() -> int:
    run = "--run" in sys.argv
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK)
    snippets = []
    for path in doc_files():
        text = open(path).read()
        for m in BLOCK.finditer(text):
            line = text[: m.start(3)].count("\n")
            snippets.append({"where": f"{os.path.relpath(path, REPO)}:{line}", "run": bool(m.group(1)),
                             "src": (m.group(2) or "") + "\n" + m.group(3) + "\nexport {};\n"})
    for i, s in enumerate(snippets):
        open(os.path.join(WORK, f"s{i:03d}.ts"), "w").write(s["src"])
    json.dump({"compilerOptions": {"target": "ES2022", "module": "NodeNext", "moduleResolution": "NodeNext",
                                   "strict": True, "noEmit": True, "skipLibCheck": True}, "include": ["*.ts"]},
              open(os.path.join(WORK, "tsconfig.json"), "w"))

    r = subprocess.run(["npx", "tsc", "-p", WORK], cwd=TS, capture_output=True, text=True)
    errors = [l for l in r.stdout.splitlines() if l.strip()]
    for l in errors:
        m = re.match(r".*s(\d{3})\.ts\((\d+),", l)
        print(f"{snippets[int(m.group(1))]['where']}: {l.split(': ', 1)[-1]}" if m else l)
    print(f"{len(snippets)} TypeScript snippets type-checked, {len(errors)} errors")
    if errors:
        return 1

    if run:
        failed = 0
        runnable = [(i, s) for i, s in enumerate(snippets) if s["run"]]
        for i, s in runnable:
            src = re.sub(r"declare const (\w+): string;", r'const \1 = "Sample text for a smoke test.";', s["src"])
            src = re.sub(r"^declare function (\w+)\(.*$", r"const \1 = (..._a: any[]): any => undefined;", src, flags=re.M)
            f = os.path.join(WORK, f"r{i:03d}.ts")
            open(f, "w").write(src)
            r = subprocess.run(["npx", "tsx", f], cwd=TS, capture_output=True, text=True, timeout=120)
            if r.returncode:
                failed += 1
                print(f"RUN FAILED {s['where']}\n{r.stderr[-800:]}")
        print(f"{len(runnable)} self-contained snippets run, {failed} failed")
        return 1 if failed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
