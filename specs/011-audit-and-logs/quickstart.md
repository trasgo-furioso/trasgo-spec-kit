# Quickstart: Audit and Logs

## Prerequisites

- trasgospec bundle installed (`specify bundle install trasgospec`)
- Git repository with a `.specify/` directory
- On a feature branch (not `main`)

## Validation Scenarios

### Scenario 1: Verify script detects changes

```bash
# Create a test feature context
echo '{"feature_directory":"specs/011-audit-and-logs"}' > .specify/feature.json

# Modify a file in the spec directory
echo "test" >> specs/011-audit-and-logs/spec.md

# Run the script
.specify/extensions/trasgospec/scripts/bash/audit-commit.sh
```

**Expected output** (JSON on stdout):
```json
{"spec_dir":"specs/011-audit-and-logs","changed_files":["spec.md"],"new_files":[],"has_changes":true,"on_branch":true,"branch":"011-audit-and-logs","error":null}
```

### Scenario 2: Verify script reports no changes

```bash
# Ensure spec directory has no uncommitted changes
git checkout -- specs/011-audit-and-logs/

# Run the script
.specify/extensions/trasgospec/scripts/bash/audit-commit.sh
```

**Expected output**:
```json
{"spec_dir":"specs/011-audit-and-logs","changed_files":[],"new_files":[],"has_changes":false,"on_branch":true,"branch":"011-audit-and-logs","error":null}
```

### Scenario 3: Verify hook registration

```bash
# Check that extension.yml declares audit-commit hooks
grep -c "audit-commit" bundle/extensions/trasgospec/extension.yml
```

**Expected output**: `8` (one per artifact-producing skill phase)

### Scenario 4: End-to-end audit trail

```bash
# After running several skills with audit hooks active:
git log --grep='[speckit:audit]' --oneline
```

**Expected**: Each skill invocation that modified artifacts has a corresponding commit with `[speckit:audit]` tag.

### Scenario 5: Verify commit message format

```bash
git log --grep='[speckit:audit]' -1 --format='%B'
```

**Expected**: Message body contains one `<filename> - <description>` per line, ending with `[speckit:audit]`.

## Running Tests

```bash
# Unit tests for audit-commit.sh
.venv/bin/pytest tests/unit/test_audit_commit.py -v

# Integration tests for hook chain
.venv/bin/pytest tests/integration/test_audit_commit_integration.py -v
```
