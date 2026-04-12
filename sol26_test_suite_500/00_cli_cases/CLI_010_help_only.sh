#!/usr/bin/env bash
set -euo pipefail

# Help-only invocation should print help and exit cleanly
# Expected exit code: 0
"${SOL26_INTERPRETER:-./solint}" --help || rc=$?; echo "${rc:-0}"
