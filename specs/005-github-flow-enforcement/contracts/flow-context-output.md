# Contract: flow-context.sh JSON Output

## Overview

`flow-context.sh` emits a single-line JSON object on stdout containing deterministic git-local state for the current repository. It reads the expected branch name from the `**Feature Branch**:` field in the active spec's `spec.md`. It is sourced/invoked by hook command scripts.

## Input

| Parameter | Source | Required |
|-----------|--------|----------|
| Working directory | CWD or `_find_specify_root` walk-up | Yes |
| `feature.json` | `.specify/feature.json` in repo root | No (graceful when absent) |
| `spec.md` | `<feature_directory>/spec.md` (path from `feature.json`) | No (graceful when absent) |

## Output (stdout, single-line JSON)

```json
{
  "current_branch": "005-github-flow-enforcement",
  "is_main": false,
  "spec_dir": "specs/005-github-flow-enforcement",
  "expected_branch": "005-github-flow-enforcement",
  "spec_branch_match": true,
  "branch_age_days": 3,
  "commits_behind_main": 0,
  "uncommitted_changes": false
}
```

### Field Specifications

| Field | Type | Null When | Computation |
|-------|------|-----------|-------------|
| `current_branch` | string | Detached HEAD | `git branch --show-current` |
| `is_main` | boolean | Never | `current_branch == "main"` |
| `spec_dir` | string | No `feature.json` or missing `feature_directory` key | Parsed from `.specify/feature.json` |
| `expected_branch` | string | No spec.md or no `**Feature Branch**` field | Grep `**Feature Branch**:` from spec.md, strip prefix/backticks/whitespace |
| `spec_branch_match` | boolean | `expected_branch` is null | `current_branch == expected_branch` (exact match) |
| `branch_age_days` | integer | Never (0 if no divergent commits) | Days since `git log main..HEAD --format="%ai" --reverse \| head -1` |
| `commits_behind_main` | integer | Never (0 on main) | `git rev-list HEAD..main --count` |
| `uncommitted_changes` | boolean | Never | `git status --porcelain` is non-empty |

### Branch Name Extraction

The `expected_branch` field is extracted from spec.md using the same pattern-matching approach as `scan-specs.sh` uses for title and status:

```bash
branch_line=$(grep -m1 '^\*\*Feature Branch\*\*:' "$spec_file" 2>/dev/null || true)
# Strip "**Feature Branch**: " prefix
# Strip backtick wrapping (` `)
# Trim whitespace
```

The extracted value is used as-is — no prefix is added.

### Edge Cases

| Condition | Behavior |
|-----------|----------|
| Detached HEAD | `current_branch: null`, `is_main: false`, `spec_branch_match: false` |
| No `feature.json` | `spec_dir: null`, `expected_branch: null`, `spec_branch_match: null` |
| `feature.json` exists but spec.md missing | `spec_dir` set, `expected_branch: null`, `spec_branch_match: null` |
| spec.md has no `**Feature Branch**` field | `expected_branch: null`, `spec_branch_match: null` |
| On `main` with no divergent commits | `branch_age_days: 0`, `commits_behind_main: 0` |
| No `main` branch exists | `commits_behind_main: 0`, `branch_age_days: 0` |
| Not a git repository | Exit code 1, error on stderr |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Not a git repository or fatal error |

## Diagnostics (stderr)

All diagnostic output goes to stderr. Examples:
- `"flow-context: not a git repository"` (exit 1)
- `"flow-context: feature.json not found, skipping spec context"` (continues)
- `"flow-context: spec.md has no Feature Branch field"` (continues)
- `"flow-context: main branch not found, defaulting to zero divergence"` (continues)
