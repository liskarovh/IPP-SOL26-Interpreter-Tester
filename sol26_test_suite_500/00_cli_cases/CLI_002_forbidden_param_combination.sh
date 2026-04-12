#!/usr/bin/env bash
set -euo pipefail

# Forbidden parameter combination should end with 10
# Expected exit code: 10
"${SOL26_INTERPRETER:-./solint}" --source a.xml --source b.xml || rc=$?; echo "${rc:-0}"
