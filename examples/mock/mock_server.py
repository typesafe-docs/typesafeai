"""A local, offline stand-in for the TypeSafe System One API.

It checks the basic request shape and returns well-formed *fake* answers: Choice picks the
first option, Score picks the middle level, Noul returns 0.9, and Box returns a fixed box. Use it to run the examples
and smoke-test your own integration without an API key. The answers carry no meaning.

    python examples/mock/mock_server.py 8765
    TYPESAFE_API_KEY=mock TYPESAFE_BASE_URL=http://127.0.0.1:8765 python examples/python/quickstart.py
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


def answer(q):
    t = q["type"]
    if t == "noul":
        return {"type": "noul", "noul": 0.9}
    if t == "choice":
        opts = list(q["criteria"])
        assert 1 <= len(opts) <= 255
        probs = {o: (0.8 if i == 0 else 0.2 / max(1, len(opts) - 1)) for i, o in enumerate(opts)}
        if len(opts) == 1: probs = {opts[0]: 1.0}
        n = len(opts); conf = (0.8 - 1 / n) / (1 - 1 / n) if n > 1 else 1.0
        return {"type": "choice", "choice": opts[0], "probabilities": probs, "confidence": round(conf, 3)}
    if t == "score":
        lv = q["criteria"]; assert 2 <= len(lv) <= 10, len(lv)
        n = len(lv); m = n // 2
        probs = {str(i): (1.0 if i == m else 0.0) for i in range(n)}
        return {"type": "score", "score": float(m), "confidence": 1.0, "probabilities": probs,
                "legend": {str(i): l for i, l in enumerate(lv)}}
    if t == "box":
        return {"type": "box", "box": {"top": 0.25, "bottom": 0.75, "left": 0.25, "right": 0.75}, "confidence": 0.8}
    raise ValueError(t)


def parse_body(raw, content_type):
    """JSON, or multipart with the JSON in a part named `request` and images in other parts."""
    if not content_type.startswith("multipart/"):
        return json.loads(raw), {}
    from email.parser import BytesParser
    from email.policy import HTTP
    msg = BytesParser(policy=HTTP).parsebytes(b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + raw)
    parts = {p.get_param("name", header="content-disposition"): p.get_payload(decode=True) for p in msg.iter_parts()}
    return json.loads(parts.pop("request")), parts

def decompress_zstd(data):
    """Both SDKs compress larger request bodies with zstd (Content-Encoding: zstd)."""
    try:
        from compression import zstd  # Python 3.14+
        return zstd.decompress(data)
    except ImportError:
        import zstandard  # pip install zstandard
        return zstandard.ZstdDecompressor().decompressobj().decompress(data)


def resolve(model):
    """Aliases resolve to the newest version; versioned IDs answer as themselves."""
    return model if model and model[-1].isdigit() else "jev-1.14.0"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body):
        b = json.dumps(body).encode()
        self.send_response(code); self.send_header("content-type", "application/json")
        self.send_header("x-typesafe-request-id", "req_mock"); self.send_header("content-length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.rstrip("/").endswith("/v1/models"):
            return self.send(200, {"models": [{"name": n, "description": "mock", "release_date": "2026-10-14"} for n in ("jev-latest", "jev-preview")]})
        self.send(404, {"error": "not found"})
    def do_POST(self):
        raw = self.rfile.read(int(self.headers["content-length"]))
        if self.headers.get("content-encoding", "").lower() == "zstd":
            raw = decompress_zstd(raw)
        body, parts = parse_body(raw, self.headers.get("content-type", ""))

        try:
            assert self.path.rstrip("/").endswith("/v1/systemone"), self.path
            assert "state" in body and body.get("questions"), "missing state/questions"
            uses_images = body.get("assets") or any(q.get("type") == "box" for q in body["questions"].values())
            if uses_images and self.headers.get("typesafe-danger-zone-images", "").lower() != "true":
                return self.send(400, {"detail": "images are not turned on: send TypeSafe-Danger-Zone-Images: true"})
            for ref, asset in (body.get("assets") or {}).items():
                assert asset.get("part") in parts or asset.get("data_base64"), f"asset {ref} has no data"
                assert ref in json.dumps({k: body[k] for k in ("state", "questions")}), f"asset {ref} is never referenced"
            answers = {k: answer(q) for k, q in body["questions"].items()}
        except Exception as e:
            return self.send(422, {"detail": str(e)})
        self.send(200, {"model": resolve(body.get("model")), "answers": answers, "usage": {"input_tokens": 100, "output_tokens": 10}})

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"mock System One API on http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
