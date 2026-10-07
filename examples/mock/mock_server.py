"""A local, offline stand-in for the TypeSafe System One API.

It checks the basic request shape and returns well-formed *fake* answers: Choice picks the
first option, Score picks the middle level, and Noul returns 0.9. Use it to run the examples
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
    raise ValueError(t)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body):
        b = json.dumps(body).encode()
        self.send_response(code); self.send_header("content-type", "application/json")
        self.send_header("x-typesafe-request-id", "req_mock"); self.send_header("content-length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.rstrip("/").endswith("/v1/models"):
            return self.send(200, {"models": [{"name": "jev-latest", "description": "mock", "release_date": "2026-09-01"}]})
        self.send(404, {"error": "not found"})
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))

        try:
            assert self.path.rstrip("/").endswith("/v1/systemone"), self.path
            assert "state" in body and body.get("questions"), "missing state/questions"
            answers = {k: answer(q) for k, q in body["questions"].items()}
        except Exception as e:
            return self.send(422, {"detail": str(e)})
        self.send(200, {"model": "jev-1.13.0", "answers": answers, "usage": {"input_tokens": 100, "output_tokens": 10}})

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"mock System One API on http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
