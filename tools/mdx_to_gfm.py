"""Convert Mintlify MDX pages (docs.typesafe.ai/*.md) into GitHub-flavoured Markdown."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jsobject import parse  # JS object-literal parser

SITE = "https://docs.typesafe.ai"
LINKMAP: dict[str, str] = {}
IMAGES: dict[str, str] = {}  # "/cookbooks/x" -> repo-relative path ("docs/cookbooks/x.md")
CALLOUT = {"Note": "📝 **Note**", "Tip": "💡 **Tip**", "Info": "ℹ️ **Info**", "Warning": "⚠️ **Warning**", "Check": "✅"}


def js_strings(block: str) -> str:
    """Concatenate every {"..."} JSX string literal (SdkSignature)."""
    out = []
    for m in re.finditer(r'\{("(?:[^"\\]|\\.)*")\}', block):
        out.append(json.loads(m.group(1)))
    return "".join(out)


def attr(tag: str, name: str):
    m = re.search(name + r'=(?:"([^"]*)"|\{"([^"]*)"\}|\{([^}]*)\})', tag)
    if not m:
        return None
    return next(g for g in m.groups() if g is not None)


def to_request(example: dict) -> dict:
    req = {}
    if "state" in example:
        req["state"] = example["state"]
    models = example.get("selectedModels")
    if models or "state" in example:
        req["model"] = (models or ["jev-latest"])[0]
    req["questions"] = example.get("questions", {})
    return req


def relink(text: str, here: str) -> str:
    def fix(m):
        label, url = m.group(1), m.group(2)
        if url.startswith("/") and not url.startswith("//"):
            path, _, frag = url.partition("#")
            path = path.rstrip("/") or "/"
            path = re.sub(r"\.md$", "", path)
            target = LINKMAP.get(path)
            if target:
                tfile, _, tfrag = target.partition("#")
                rel = os.path.relpath(tfile, os.path.dirname(here))
                if tfile == here:
                    rel = ""
                frag = tfrag or frag
                return f"[{label}]({rel}{'#' + frag if frag else ''})"
            return f"[{label}]({SITE}{url})"
        return m.group(0)

    text = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix, text)
    text = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{SITE}{m.group(1)}"', text)
    return text


def convert(src: str, here: str, source_url: str) -> str:
    # drop the llms.txt banner
    src = re.sub(r"\A(> .*\n)+\n?", "", src)
    lines = src.split("\n")
    out: list[str] = []
    i = 0
    depth = 0
    in_code = False
    fence = ""

    def emit(s=""):
        out.append(s)

    def dedent(l: str) -> str:
        n = 0
        while n < len(l) and n < depth * 2 and l[n] == " ":
            n += 1
        return l[n:]

    while i < len(lines):
        raw = lines[i]
        line = dedent(raw)
        s = line.strip()

        # ---- code fences -------------------------------------------------
        if in_code:
            if s.startswith(fence) and s.strip("`~") == "":
                in_code = False
                emit(fence)
            else:
                emit(line)
            i += 1
            continue
        m = re.match(r"^(`{3,}|~{3,})(.*)$", s)
        if m:
            fence = m.group(1)
            info = m.group(2)
            info = re.sub(r"\s*theme=\{null\}", "", info)
            info = re.sub(r"\s*(expandable|wrap|lines|focus=\{[^}]*\}|highlight=\{[^}]*\}|icon=\"[^\"]*\")", "", info)
            title = re.search(r'title="([^"]*)"', info)
            info = re.sub(r'\s*title="[^"]*"', "", info).strip()
            parts = info.split(None, 1)
            lang = parts[0] if parts else ""
            fname = title.group(1) if title else (parts[1] if len(parts) > 1 else None)
            if fname and fname.lower() not in (lang.lower(),):
                emit(f"**`{fname}`**")
                emit()
            emit(fence + lang)
            in_code = True
            i += 1
            continue

        # ---- export function ... (component definitions) -----------------
        if s.startswith("export "):
            j = i
            while j < len(lines) and not re.match(r"^\};?\s*$", lines[j]):
                j += 1
            i = j + 1
            continue
        if s.startswith("import ") and " from " in s:
            i += 1
            continue

        # ---- multi-line JSX components needing their body ----------------
        if re.match(r"^<(TypesafeExample)\b", s):
            j = i
            buf = [lines[i]]
            while not re.search(r"/>\s*$", lines[j]) or j == i and not s.endswith("/>"):
                j += 1
                buf.append(lines[j])
                if re.search(r"/>\s*$", lines[j]):
                    break
            block = "\n".join(buf)
            title = attr(block.split("example=")[0], "title")
            k = block.find("example={")
            example = None
            if k >= 0:
                try:
                    example, _ = parse(block, k + len("example={"))
                except Exception as e:  # noqa
                    example = None
            if example is not None:
                req = to_request(example)
                if title:
                    emit(f"**{title}**")
                    emit()
                emit("```json")
                emit(json.dumps(req, indent=2, ensure_ascii=False))
                emit("```")
            i = j + 1
            continue

        if s.startswith("<SdkSignature"):
            j = i
            buf = []
            while "</SdkSignature>" not in lines[j]:
                buf.append(lines[j])
                j += 1
            buf.append(lines[j])
            code = js_strings("\n".join(buf)).rstrip()
            emit("```python" if "/python/" in source_url else "```ts")
            emit(code)
            emit("```")
            i = j + 1
            continue

        if re.match(r"^<(ConfidenceExplorer|ScoreExplorer|ScoreConfidenceExplorer)\b", s):
            emit(f"> 🧪 *Interactive explorer available on the [official page]({source_url}).*")
            i += 1
            continue

        # ---- media -------------------------------------------------------
        if re.match(r"^</?Frame\b", s) or re.match(r"^(\* )?<(img|iframe|video)\b", s):
            for im in re.finditer(r"<img\b[^>]*>", s):
                tag = im.group(0)
                if "dark:block" in tag:
                    continue
                src_url = attr(tag, "src")
                alt = attr(tag, "alt") or ""
                dp = attr(tag, "data-path")
                if src_url and dp:
                    IMAGES[dp] = src_url
                    rel = os.path.relpath(os.path.join("docs/assets", dp), os.path.dirname(here))
                    emit(f"![{alt}]({rel})")
                    emit()
            if re.match(r"^<iframe\b", s):
                emit(f"> 🎬 *Video available on the [official page]({source_url}).*")
            i += 1
            continue

        # ---- callouts ----------------------------------------------------
        m = re.match(r"^<(Note|Tip|Info|Warning|Check)>(.*)$", s)
        if m:
            tag = m.group(1)
            rest = m.group(2)
            body = []
            if rest.endswith(f"</{tag}>"):
                body = [rest[: -len(f"</{tag}>")]]
                i += 1
            else:
                if rest:
                    body.append(rest)
                i += 1
                while f"</{tag}>" not in lines[i]:
                    body.append(dedent(lines[i]).lstrip() if not lines[i].strip().startswith("```") else lines[i].strip())
                    i += 1
                last = lines[i].split(f"</{tag}>")[0].strip()
                if last:
                    body.append(last)
                i += 1
            # strip common indentation
            emit(f"> {CALLOUT[tag]}")
            emit(">")
            for b in body:
                emit(("> " + b).rstrip())
            emit()
            continue

        # ---- structural tags --------------------------------------------
        m = re.match(r"^<(Tab|Accordion|Step|Card|Expandable|ParamField|ResponseField|Update)\b([^>]*?)(/?)>(.*)$", s)
        if m:
            tag, attrs, selfclose, rest = m.groups()
            title = attr(attrs, "title")
            if tag == "Tab":
                emit(f"**{title}**")
                emit()
            elif tag == "Accordion":
                emit("<details>")
                emit(f"<summary><b>{title}</b></summary>")
                emit()
            elif tag == "Step":
                emit(f"#### {title}")
                emit()
            elif tag == "Card":
                href = attr(attrs, "href")
                inner = re.sub(r"</Card>\s*$", "", rest).strip()
                if href:
                    emit(f"- **[{title}]({href})**" + (f" — {inner}" if inner else ""))
                else:
                    emit(f"- **{title}**" + (f" — {inner}" if inner else ""))
                if "</Card>" not in s:
                    # body on following lines
                    i += 1
                    body = []
                    while "</Card>" not in lines[i]:
                        if lines[i].strip():
                            body.append(lines[i].strip())
                        i += 1
                    if body:
                        out[-1] += " — " + " ".join(body)
                i += 1
                continue
            elif tag == "Expandable":
                pass
            elif tag in ("ParamField", "ResponseField"):
                name = attr(attrs, "name") or attr(attrs, "body") or attr(attrs, "path") or attr(attrs, "query") or attr(attrs, "header")
                typ = attr(attrs, "type")
                req = " *(required)*" if re.search(r"\brequired\b", attrs) else ""
                typ = typ.replace("&#x22;", '"') if typ else typ
                head = f"- **`{name}`**" if name else "-"
                if typ:
                    head += f" `{typ}`"
                emit(head + req)
                inner = re.sub(rf"</{tag}>\s*$", "", rest).strip()
                if inner:
                    out[-1] += " — " + inner
                if selfclose or f"</{tag}>" in s:
                    i += 1
                    continue
                # gather simple text body
                i += 1
                body = []
                while i < len(lines) and f"</{tag}>" not in lines[i] and not re.match(r"^\s*<(Expandable|ParamField|ResponseField)", lines[i]):
                    if lines[i].strip():
                        body.append(lines[i].strip())
                    i += 1
                if body:
                    out[-1] += " — " + " ".join(body)
                if i < len(lines) and f"</{tag}>" in lines[i]:
                    i += 1
                else:
                    depth += 1  # nested fields follow; closing tag handled below
                continue
            if not selfclose and f"</{tag}>" not in s:
                depth += 1
            i += 1
            continue

        m = re.match(r"^</(Tab|Accordion|Step|Expandable|ParamField|ResponseField|Update)>\s*$", s)
        if m:
            tag = m.group(1)
            depth = max(0, depth - 1)
            if tag == "Accordion":
                emit()
                emit("</details>")
                emit()
            i += 1
            continue

        if re.match(r"^</?(Tabs|AccordionGroup|Steps|Columns|CardGroup|CodeGroup|Panel|RequestExample|ResponseExample)\b[^>]*>\s*$", s):
            if re.match(r"^<(Tabs|AccordionGroup|Steps|Columns|CardGroup|CodeGroup|RequestExample|ResponseExample)\b", s):
                depth += 1
            elif s.startswith("</"):
                depth = max(0, depth - 1)
            i += 1
            continue

        emit(line)
        i += 1

    text = "\n".join(out)
    text = cleanup_html(text)
    text = text.replace("&#x22;", '"')
    text = re.sub(r"\n{3,}", "\n\n", text)
    return relink(text, here)


def _strip_tags(x: str) -> str:
    x = re.sub(r"<[^>]+>", "", x)
    return x.replace("\\_", "_").replace("\\[", "[").replace("\\]", "]").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def cleanup_html(text: str) -> str:
    parts = re.split(r"(^```.*?^```)", text, flags=re.M | re.S)
    for k in range(0, len(parts), 2):
        t = parts[k]
        t = re.sub(r"This documentation is built and hosted on \[Mintlify\]\([^)]*\), a developer documentation platform\.\s*", "", t)
        t = re.sub(r'<a id="([^"]+)"\s*/>', r'<a id="\1"></a>', t)
        t = re.sub(
            r'<h([1-6]) id="([^"]+)">\s*(.*?)\s*</h\1>',
            lambda m: f'<a id="{m.group(2)}"></a>\n\n{"#" * int(m.group(1))} ' + _fmt_head(_strip_tags(m.group(3)).strip()),
            t,
            flags=re.S,
        )
        t = re.sub(r"<code>(.*?)</code>", lambda m: "`" + _strip_tags(m.group(1)) + "`", t, flags=re.S)
        parts[k] = t
    return "".join(parts)


def _fmt_head(h: str) -> str:
    return f"`{h}`" if " " not in h else h
