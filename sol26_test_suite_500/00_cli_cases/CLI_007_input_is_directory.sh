#!/usr/bin/env bash
set -euo pipefail

# Directory used as input should end with 11
# Expected exit code: 11
tmp=$(mktemp -d)
"${SOL26_INTERPRETER:-./solint}" "$tmp" || rc=$?
rm -rf "$tmp"
echo "${rc:-0}"
