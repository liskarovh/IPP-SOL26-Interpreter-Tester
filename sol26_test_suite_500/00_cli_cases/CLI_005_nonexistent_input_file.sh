#!/usr/bin/env bash
set -euo pipefail

# Nonexistent input file should end with 11
# Expected exit code: 11
"${SOL26_INTERPRETER:-./solint}" /definitely/missing/file.xml || rc=$?; echo "${rc:-0}"
