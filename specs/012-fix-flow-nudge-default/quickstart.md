# Quickstart Validation: Fix Flow-Nudge Default Execution

**Date**: 2026-08-10

## Prerequisites

- Git repository with `.specify/` directory
- `gh` CLI installed and authenticated
- Trasgospec bundle installed (`specify bundle install`)

## Validation Scenario 1: Deliver Auto-Executes After Plan

**Purpose**: Verify the deliver hook runs automatically (not as suggestion).

```bash
# 1. Create a feature branch and spec
git checkout -b test-deliver-validation
# ... create a minimal spec.md with Feature Branch field

# 2. Run /speckit-plan
# Expected: After plan completes, the after_plan hooks fire:
#   - status hook advances to "Ready to Dev"
#   - deliver hook auto-executes (NOT displayed as suggestion)
#   - deliver creates a draft PR via gh

# 3. Verify PR was created
gh pr list --state open --head test-deliver-validation
# Expected: Draft PR exists
```

**Pass criteria**: The deliver hook output shows "Created draft PR" with a URL, not "To execute: /speckit-trasgospec-deliver".

## Validation Scenario 2: Graceful Fallback Without gh

```bash
# 1. Temporarily remove gh from PATH
PATH_BACKUP="$PATH"
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v gh | tr '\n' ':')

# 2. Run /speckit-plan on a feature branch
# Expected: deliver hook runs but displays suggestion block:
#   "PR Action Suggested: Open Draft PR"
#   "Run: gh pr create --draft --title ..."

# 3. Restore PATH
export PATH="$PATH_BACKUP"
```

**Pass criteria**: No error. Suggestion block displayed. Workflow continues.

## Validation Scenario 3: PR Template Resolution

```bash
# 1. Verify template resolves
specify preset resolve pr-template
# Expected: shows path under .specify/presets/trasgospec/templates/pr-template.md

# 2. Override with custom template
mkdir -p .specify/templates/overrides
cat > .specify/templates/overrides/pr-template.md << 'EOF'
---
title: "custom: {{spec_title}}"
---
Custom PR body for {{spec_title}}.
EOF

# 3. Run deliver (or /speckit-plan to trigger it)
# Expected: PR uses custom title format "custom: <title>" and custom body

# 4. Clean up override
rm .specify/templates/overrides/pr-template.md
```

**Pass criteria**: `specify preset resolve pr-template` shows the override path. PR uses custom format.

## Validation Scenario 4: Commit Template Resolution

```bash
# 1. Verify template resolves
specify preset resolve commit-template
# Expected: shows path under .specify/presets/trasgospec/templates/commit-template.md

# 2. Make a change and run /speckit-trasgospec-commit
# Expected: commit message follows the template format (one line per file)
git log -1 --format="%B"
```

**Pass criteria**: Commit message follows the template format.

## Validation Scenario 5: User Override to Optional

```bash
# 1. Edit .specify/extensions/trasgospec/extension.yml
# Change after_plan deliver hook to optional: true

# 2. Run /speckit-plan
# Expected: deliver is displayed as suggestion, not auto-executed
#   "Optional Hook: trasgospec"
#   "To execute: /speckit-trasgospec-deliver"
```

**Pass criteria**: Hook displayed as suggestion block, not auto-executed.
