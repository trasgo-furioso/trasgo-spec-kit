# Contract: Pre-Push Hook Exit Codes

The pre-push hook communicates its result to git via exit codes and stderr messages.

## Exit Codes

| Code | Meaning | Git Behavior | Stderr Output |
|------|---------|-------------|---------------|
| 0 | Skip or retry success | Push proceeds | Silent (skip) or none (retry — HEAD is already a build commit) |
| 1 | Validation failed | Push blocked | Validation error details from `specify bundle validate` |
| 2 | Build failed | Push blocked | Build error details from `specify bundle build` |
| 3 | Prerequisites missing | Push blocked | `"ERROR: specify CLI not found. Install Spec Kit before pushing bundle changes."` |
| 4 | Catalog update failed | Push blocked | `"ERROR: Failed to update catalog.json"` with details |
| 5 | Auto-commit failed | Push blocked | `"ERROR: Failed to create build commit"` with details |
| 6 | Build committed, push again | Push blocked | Build summary + `"Run 'git push' again to include them."` |

## Stderr Output Format

All diagnostic output goes to stderr. Stdout is not used.

```
[bundle-build] <message>
```

### Build committed, push again (exit 6):
```
[bundle-build] Validating bundle...
[bundle-build] Building bundle...
[bundle-build] Updating catalog.json (v0.3.0)
[bundle-build] Created commit: chore: build bundle v0.3.0
[bundle-build]
[bundle-build] Build artifacts committed. Run 'git push' again to include them.
```

### Retry success (exit 0, HEAD is build commit):
No output (silent pass-through).

### Skip (exit 0, no bundle changes):
No output (silent pass-through).

### Failure example (exit 1):
```
[bundle-build] Validating bundle...
[bundle-build] ERROR: Bundle validation failed:
<specify bundle validate stderr output>
[bundle-build] Push blocked. Fix validation errors and try again.
```
