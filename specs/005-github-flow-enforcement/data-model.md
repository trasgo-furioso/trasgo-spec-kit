# Data Model: GitHub Flow Enforcement

## Entities

### Flow Context (output of flow-context.sh)

Git-local state snapshot. Produced by `flow-context.sh`, consumed by both hook commands.

| Field | Type | Description |
|-------|------|-------------|
| `current_branch` | string or null | Current git branch name; null if detached HEAD |
| `is_main` | boolean | True if current branch is `main` |
| `spec_dir` | string or null | Active spec directory from `feature.json`; null if not set |
| `expected_branch` | string or null | Branch name read from `**Feature Branch**:` field in spec.md; null if not found |
| `spec_branch_match` | boolean or null | True if `current_branch` equals `expected_branch`; null if `expected_branch` is null |
| `branch_age_days` | integer | Days since first commit diverging from main; 0 if no divergent commits |
| `commits_behind_main` | integer | Number of commits main has that this branch doesn't |
| `uncommitted_changes` | boolean | True if working tree has uncommitted changes |

### PR Context (output of flow-nudge.sh)

Extends flow context with PR state. Produced by `flow-nudge.sh`, consumed by flow-nudge command.

| Field | Type | Description |
|-------|------|-------------|
| `flow_context` | object | Full flow context (see above) |
| `gh_available` | boolean | True if `gh` CLI is installed and in PATH |
| `gh_integration` | boolean | True if gh_integration setting is enabled |
| `has_open_pr` | boolean | True if an open PR exists for current branch |
| `pr_is_draft` | boolean | True if the open PR is a draft |
| `pr_number` | integer or null | PR number if one exists; null otherwise |
| `pr_url` | string or null | PR URL if one exists; null otherwise |
| `inferred_phase` | string | One of: `plan`, `implement`, `analyze` — inferred from artifacts |
| `suggested_action` | string | One of: `create_draft`, `mark_ready`, `final_review`, `none` |

### Hook Registration Entry (in extensions.yml)

| Field | Type | Description |
|-------|------|-------------|
| `extension` | string | Always `trasgospec` |
| `command` | string | Command ID (`speckit.trasgospec.flow-gate` or `speckit.trasgospec.flow-nudge`) |
| `description` | string | Human-readable description of what the hook does |
| `optional` | boolean | `false` for gate hooks, `true` for nudge hooks |
| `enabled` | boolean | Default `true`; can be set to `false` to disable |

## State Transitions

### Phase Inference (flow-nudge.sh)

```
Artifact State                          → Inferred Phase  → Suggested Action
─────────────────────────────────────────────────────────────────────────────
plan.md exists, no tasks.md             → plan            → create_draft
tasks.md exists                         → implement       → mark_ready
(after_analyze hook point)              → analyze         → final_review
PR already non-draft                    → any             → none (skip)
No PR and not plan phase                → any             → none (skip)
```

### gh Integration Mode Resolution

```
gh_integration setting    gh in PATH    → Effective Mode
──────────────────────────────────────────────────────────
true (or absent)          yes           → auto (execute gh commands)
true (or absent)          no            → output-only (warn once)
false                     any           → output-only (no warning)
```

### Flow-Gate Mode (after_specify vs before_*)

```
Hook Point        feature.json    spec.md exists    → Behavior
──────────────────────────────────────────────────────────────────
after_specify     just created    yes               → read expected_branch from spec.md,
                                                      create/switch to branch if not on it
before_*          exists          yes               → block on main, warn on mismatch
before_*          missing         n/a               → skip branch-match, still block on main
```

## Relationships

```
extensions.yml
  └── hooks.after_specify[] ──→ flow-gate command ──→ flow-context.sh ──→ spec.md (**Feature Branch**)
  └── hooks.before_*[]      ──→ flow-gate command ──→ flow-context.sh ──→ spec.md (**Feature Branch**)
  └── hooks.after_*[]       ──→ flow-nudge command ──→ flow-nudge.sh ──→ flow-context.sh
                                                                      ──→ gh CLI (optional)

.specify/feature.json ──→ flow-context.sh (reads spec_dir → locates spec.md)
spec.md **Feature Branch** field ──→ flow-context.sh (reads expected_branch)
```
