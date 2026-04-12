#!/usr/bin/env bash
set -euo pipefail

# Missing required CLI parameter should end with 10
# Expected exit code: 10
"${SOL26_INTERPRETER:-./solint}" || rc=$?; echo "${rc:-0}"
