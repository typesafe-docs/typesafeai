#!/usr/bin/env bash
# List the model names (aliases) your account can send in the `model` field.
set -euo pipefail

curl -sS https://api.typesafe.ai/v1/models \
  -H "Authorization: Bearer ${TYPESAFE_API_KEY:?set TYPESAFE_API_KEY}"
echo
