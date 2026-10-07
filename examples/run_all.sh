#!/usr/bin/env bash
# Run every example. Defaults to the offline mock server; set USE_REAL_API=1 to hit api.typesafe.ai.
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${USE_REAL_API:-0}" != "1" ]]; then
  python3 mock/mock_server.py 8765 >/dev/null 2>&1 &
  MOCK_PID=$!
  trap 'kill $MOCK_PID' EXIT
  sleep 1
  export TYPESAFE_API_KEY=mock TYPESAFE_BASE_URL=http://127.0.0.1:8765
fi

for f in python/*.py; do
  echo "=== $f"
  python3 "$f"
done

if command -v npx >/dev/null && [[ -d typescript/node_modules ]]; then
  for f in typescript/*.ts; do
    echo "=== $f"
    (cd typescript && npx tsx "$(basename "$f")")
  done
fi
