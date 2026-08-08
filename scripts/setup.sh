#!/usr/bin/env bash
# setup.sh — One-time developer setup for Trasgo Spec Kit.
#
# Configures git to use the tracked .githooks/ directory for hooks.
# Idempotent — safe to run multiple times.
set -euo pipefail

# Verify we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Not a git repository. Run this from the project root." >&2
    exit 1
fi

# Configure git to use tracked hooks directory
git config core.hooksPath .githooks

echo "Git hooks configured: core.hooksPath = .githooks"
