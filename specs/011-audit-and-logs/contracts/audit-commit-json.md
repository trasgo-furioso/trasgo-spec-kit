# Contract: audit-commit.sh JSON Output

## Invocation

```bash
.specify/extensions/trasgospec/scripts/bash/audit-commit.sh
```

No arguments. Reads `feature.json` to locate the spec directory.

## Success Response (exit 0)

```json
{
  "spec_dir": "specs/011-audit-and-logs",
  "changed_files": ["spec.md", "plan.md"],
  "new_files": ["research.md"],
  "has_changes": true,
  "on_branch": true,
  "branch": "011-audit-and-logs",
  "error": null
}
```

## No Changes Response (exit 0)

```json
{
  "spec_dir": "specs/011-audit-and-logs",
  "changed_files": [],
  "new_files": [],
  "has_changes": false,
  "on_branch": true,
  "branch": "011-audit-and-logs",
  "error": null
}
```

## Detached HEAD Response (exit 0)

```json
{
  "spec_dir": "specs/011-audit-and-logs",
  "changed_files": [],
  "new_files": [],
  "has_changes": false,
  "on_branch": false,
  "branch": null,
  "error": "Detached HEAD — cannot commit"
}
```

## No Feature Context Response (exit 0)

```json
{
  "spec_dir": null,
  "changed_files": [],
  "new_files": [],
  "has_changes": false,
  "on_branch": true,
  "branch": "main",
  "error": "No feature.json found — skipping audit"
}
```

## Fatal Error Response (exit 1)

Stderr: `audit-commit: not a git repository`
No stdout output.

## Field Guarantees

- `changed_files` and `new_files` are always arrays (possibly empty)
- `has_changes` is always a boolean
- `on_branch` is always a boolean
- `error` is null on success, string on recoverable error
- File paths in arrays are relative to `spec_dir`
