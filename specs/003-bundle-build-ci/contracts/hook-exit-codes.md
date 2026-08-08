# Contract: Pre-Push Hook Exit Codes

The pre-push hook communicates its result to git via exit codes and stderr messages.

## Exit Codes

| Code | Meaning | Git Behavior | Stderr Output |
|------|---------|-------------|---------------|
| 0 | Success or skip | Push proceeds | Build summary (if build ran) or silent (if skipped) |
| 1 | Validation failed | Push blocked | Validation error details from `specify bundle validate` |
| 2 | Build failed | Push blocked | Build error details from `specify bundle build` |
| 3 | Prerequisites missing | Push blocked | `"ERROR: specify CLI not found. Install Spec Kit before pushing bundle changes."` |
| 4 | Catalog update failed | Push blocked | `"ERROR: Failed to update catalog.json"` with details |
| 5 | Auto-commit failed | Push blocked | `"ERROR: Failed to create build commit"` with details |

## Stderr Output Format

All diagnostic output goes to stderr. Stdout is not used.

```
[bundle-build] <message>
```

### Success (exit 0, build ran):
```
[bundle-build] Validating bundle...
[bundle-build] Building bundle...
[bundle-build] Updating catalog.json (v0.2.0 → v0.3.0)
[bundle-build] Created commit: chore: build bundle v0.3.0
[bundle-build] Done.
```

### Success (exit 0, skipped):
No output (silent pass-through).

### Failure example (exit 1):
```
[bundle-build] Validating bundle...
[bundle-build] ERROR: Bundle validation failed:
<specify bundle validate stderr output>
[bundle-build] Push blocked. Fix validation errors and try again.
```
