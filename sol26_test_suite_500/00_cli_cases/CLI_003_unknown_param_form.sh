#!/usr/bin/env bash
set -euo pipefail

# Unknown parameter should end with 10
# Expected exit code: 10
"${SOL26_INTERPRETER:-./solint}" --definitely-unknown foo.xml || rc=$?; echo "${rc:-0}"
