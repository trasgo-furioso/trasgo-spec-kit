# Data Model: Audit and Logs

## Entities

### AuditCommitContext

The JSON contract emitted by `audit-commit.sh` on stdout. Consumed by the command file to decide whether to commit and what message to write.

| Field | Type | Description |
|-------|------|-------------|
| `spec_dir` | string \| null | Relative path to the feature's spec directory (e.g., `specs/011-audit-and-logs`) |
| `changed_files` | string[] | List of modified tracked files (relative to spec_dir) |
| `new_files` | string[] | List of untracked files in spec_dir |
| `has_changes` | boolean | `true` if `changed_files` or `new_files` is non-empty |
| `on_branch` | boolean | `true` if HEAD is on a named branch (not detached) |
| `branch` | string \| null | Current branch name, or null if detached |
| `error` | string \| null | Human-readable error message, or null if no error |

### CommitMessage

The structured git commit message assembled by the command file.

```
<file1> - <description1>
<file2> - <description2>
[speckit:audit]
```

**Rules**:
- One line per changed/new file
- Each line: `<filename> - <one-liner description>`
- Filename is relative to spec_dir (e.g., `spec.md`, not `specs/011-audit-and-logs/spec.md`)
- Last line is always `[speckit:audit]` (the grep tag)
- No blank lines between file entries and the tag

### HookRegistration

An entry in `.specify/extensions.yml` under an `after_*` key.

| Field | Type | Value |
|-------|------|-------|
| `extension` | string | `trasgospec` |
| `command` | string | `speckit.trasgospec.audit-commit` |
| `enabled` | boolean | `true` |
| `optional` | boolean | `false` |
| `priority` | integer | `20` |
| `description` | string | `Audit — auto-commit spec artifacts` |
| `condition` | null | No conditional execution |

## State Transitions

```
Skill completes
  → after_* hook fires (priority 20, after status/flow-nudge hooks)
    → audit-commit.sh runs
      → has_changes=true?
        YES → command inspects diffs, generates descriptions, stages + commits
              → displays "Committed: <files> [speckit:audit]"
        NO  → displays "No artifact changes to commit."
      → error set?
        → displays warning, does not block
      → on_branch=false?
        → displays "No commit created: detached HEAD"
```

## Relationships

- **feature.json** → provides `feature_directory` → script resolves to `spec_dir`
- **spec_dir** → scoped by `git status --porcelain -- <spec_dir>/` → produces `changed_files` + `new_files`
- **extension.yml** (bundle source) → declares hooks → installer merges into `.specify/extensions.yml` (runtime)
