#!/usr/bin/env bash
set -euo pipefail

# File-opening failure must not pollute stdout
# Expected exit code: 11
echo "Run a missing-file case and assert stdout is empty."
