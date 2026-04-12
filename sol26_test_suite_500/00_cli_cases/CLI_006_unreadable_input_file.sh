#!/usr/bin/env bash
set -euo pipefail

# Unreadable input file should end with 11
# Expected exit code: 11
tmp=$(mktemp)
printf "<x/>" > "$tmp"
chmod 000 "$tmp"
"${SOL26_INTERPRETER:-./solint}" "$tmp" || rc=$?
chmod 600 "$tmp"
rm -f "$tmp"
echo "${rc:-0}"
