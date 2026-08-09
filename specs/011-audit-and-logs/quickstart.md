# Quickstart: Audit and Logs

## Prerequisites

- trasgospec bundle installed (`specify bundle install trasgospec`)
- Git repository with a remote configured
- `.specify/` in `.gitignore`
- On a feature branch (not `main`)

## Validation Scenarios

### Scenario 1: Verify script detects repo-wide changes

```bash
# Modify a file anywhere in the repo
echo "test" >> specs/011-audit-and-logs/spec.md

# Run the script
.specify/extensions/trasgospec/scripts/bash/commit.sh
```

**Expected output** (JSON on stdout):
```json
{"changed_files":[{"path":"specs/011-audit-and-logs/spec.md","status":"M"}],"new_files":[],"deleted_files":[],"has_changes":true,"on_branch":true,"branch":"011-audit-and-logs","has_remote":true,"error":null}
```

### Scenario 2: Verify script reports no changes

```bash
# Ensure repo has no uncommitted changes
git checkout -- .

# Run the script
.specify/extensions/trasgospec/scripts/bash/commit.sh
```

**Expected output**:
```json
{"changed_files":[],"new_files":[],"deleted_files":[],"has_changes":false,"on_branch":true,"branch":"011-audit-and-logs","has_remote":true,"error":null}
```

### Scenario 3: Verify .specify/ is excluded

```bash
# Modify a file in .specify/
echo "test" >> .specify/feature.json

# Run the script
.specify/extensions/trasgospec/scripts/bash/commit.sh
```

**Expected**: `.specify/feature.json` does NOT appear in any array (it's gitignored).

### Scenario 4: Verify hook registration

```bash
grep -c "speckit.trasgospec.commit" bundle/extensions/trasgospec/extension.yml
```

**Expected output**: `8` (one per artifact-producing skill phase)

### Scenario 5: End-to-end commit + push

```bash
# After running a skill with the commit hook active:
git log -1 --format='%B'
```

**Expected**: Message body contains one `<repo-relative-path> - <description>` per line, no tags.

## Running Tests

```bash
.venv/bin/pytest tests/unit/test_commit.py -v
.venv/bin/pytest tests/integration/test_commit_integration.py -v
```
