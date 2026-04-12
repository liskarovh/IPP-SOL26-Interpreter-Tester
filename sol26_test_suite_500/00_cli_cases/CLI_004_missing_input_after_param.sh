#!/usr/bin/env bash
set -euo pipefail

# Missing argument after CLI parameter should end with 10
# Expected exit code: 10
"${SOL26_INTERPRETER:-./solint}" --source || rc=$?; echo "${rc:-0}"
