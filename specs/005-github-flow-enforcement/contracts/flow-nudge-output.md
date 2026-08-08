# Contract: flow-nudge.sh JSON Output

## Overview

`flow-nudge.sh` emits a single-line JSON object on stdout containing PR state and phase inference. It sources `flow-context.sh` for git-local state and optionally queries `gh` for PR state.

## Input

| Parameter | Source | Required |
|-----------|--------|----------|
| Working directory | CWD or `_find_specify_root` walk-up | Yes |
| `feature.json` | `.specify/feature.json` in repo root | Yes (for spec dir / artifact detection) |
| `gh_integration` | `.specify/extensions.yml` `settings.gh_integration` | No (defaults to `true`) |

## Output (stdout, single-line JSON)

```json
{
  "flow_context": {
    "current_branch": "feat/005-github-flow-enforcement",
    "is_main": false,
    "spec_dir": "specs/005-github-flow-enforcement",
    "spec_branch_match": true,
    "suggested_branch": "feat/005-github-flow-enforcement",
    "branch_age_days": 3,
    "commits_behind_main": 0,
    "uncommitted_changes": false
  },
  "gh_available": true,
  "gh_integration": true,
  "has_open_pr": true,
  "pr_is_draft": true,
  "pr_number": 42,
  "pr_url": "https://github.com/owner/repo/pull/42",
  "inferred_phase": "implement",
  "suggested_action": "mark_ready"
}
```

### Field Specifications

| Field | Type | Null When | Computation |
|-------|------|-----------|-------------|
| `flow_context` | object | Never | Output of `flow-context.sh` |
| `gh_available` | boolean | Never | `command -v gh` succeeds |
| `gh_integration` | boolean | Never | Parsed from `extensions.yml` settings; `true` if absent |
| `has_open_pr` | boolean | Never (false when gh unavailable) | `gh pr view --json state,isDraft 2>/dev/null` |
| `pr_is_draft` | boolean | Never (false when no PR) | From `gh pr view` response |
| `pr_number` | integer | No open PR or gh unavailable | From `gh pr view --json number` |
| `pr_url` | string | No open PR or gh unavailable | From `gh pr view --json url` |
| `inferred_phase` | string | Never | Artifact-based: see inference rules below |
| `suggested_action` | string | Never | Derived from `inferred_phase` + PR state |

### Phase Inference Rules

The script checks artifacts in the feature directory (from `feature.json`):

| Condition | `inferred_phase` | `suggested_action` |
|-----------|-------------------|---------------------|
| `plan.md` exists AND `tasks.md` does NOT exist | `plan` | `create_draft` (if no PR) or `none` |
| `tasks.md` exists | `implement` | `mark_ready` (if PR is draft) or `none` |
| Fallback (after_analyze hook context) | `analyze` | `final_review` (if PR exists) or `none` |

### Suggested Action Resolution

| `inferred_phase` | PR State | `suggested_action` |
|-------------------|----------|---------------------|
| `plan` | No PR exists | `create_draft` |
| `plan` | PR already exists | `none` |
| `implement` | PR is draft | `mark_ready` |
| `implement` | PR is not draft | `none` |
| `implement` | No PR exists | `create_draft` |
| `analyze` | PR exists (any state) | `final_review` |
| `analyze` | No PR exists | `create_draft` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Not a git repository or fatal error |

## Diagnostics (stderr)

- `"flow-nudge: gh not found, PR fields will be empty"` (continues)
- `"flow-nudge: gh_integration disabled, skipping PR queries"` (continues)
- `"flow-nudge: feature.json not found, cannot infer phase"` (continues, `inferred_phase: "unknown"`, `suggested_action: "none"`)
