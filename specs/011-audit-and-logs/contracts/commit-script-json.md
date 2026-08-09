# Contract: commit.sh JSON Output

## Invocation

```bash
.specify/extensions/trasgospec/scripts/bash/commit.sh
```

No arguments. Scans the entire repository for changes.

## Success Response — Changes Found (exit 0)

```json
{
  "changed_files": [
    {"path": "specs/011-audit-and-logs/spec.md", "status": "M"},
    {"path": "tests/unit/test_commit.py", "status": "M"}
  ],
  "new_files": [
    {"path": "specs/011-audit-and-logs/research.md", "status": "??"}
  ],
  "deleted_files": [],
  "has_changes": true,
  "branch": "011-audit-and-logs",
  "has_remote": true,
  "error": null
}
```

## Success Response — No Changes (exit 0)

```json
{
  "changed_files": [],
  "new_files": [],
  "deleted_files": [],
  "has_changes": false,
  "branch": "011-audit-and-logs",
  "has_remote": true,
  "error": null
}
```

## Detached HEAD Response (exit 0)

```json
{
  "changed_files": [],
  "new_files": [],
  "deleted_files": [],
  "has_changes": false,
  "branch": null,
  "has_remote": false,
  "error": "Detached HEAD — cannot commit"
}
```

## Fatal Error (exit 1)

Stderr: `commit: not a git repository`
No stdout output.

## Field Guarantees

- `changed_files`, `new_files`, `deleted_files` are always arrays (possibly empty)
- Each array element has `path` (string, repo-relative) and `status` (string, git status code)
- `has_changes` is always a boolean
- `has_remote` is always a boolean
- `branch` is null when on a detached HEAD, non-null otherwise
- `error` is null on success, string on recoverable error
- Files in `.specify/` are excluded from all arrays (filtered by the script since `.specify/` is gitignored)
