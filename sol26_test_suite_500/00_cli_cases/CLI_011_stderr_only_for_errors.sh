#!/usr/bin/env bash
set -euo pipefail

# Failing CLI invocation should not pollute stdout
# Expected exit code: 10
echo "Run a failing CLI case and assert stdout is empty while stderr contains diagnostics."
