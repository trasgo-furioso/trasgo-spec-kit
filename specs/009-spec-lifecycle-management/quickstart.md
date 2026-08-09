# Quickstart: Spec Lifecycle Management

## Prerequisites

- trasgo-spec-kit repo cloned and set up (`./scripts/setup.sh`)
- Python venv active (`.venv/bin/pytest` available)
- On branch `009-spec-lifecycle-management`

## Validation Scenarios

### 1. PRD-only features appear on the roadmap

```bash
# Create a test project with a PRD-only feature
mkdir -p /tmp/lifecycle-test/specs/001-test-prd/.specify
echo '# PRD: Test PRD Feature
**Status**: Discovery
**Created**: 2026-08-09' > /tmp/lifecycle-test/specs/001-test-prd/prd.md

# Run scan-specs.sh against it
bash .specify/extensions/trasgospec/scripts/bash/scan-specs.sh
# Expected: JSON includes {"id":"001-test-prd","title":"Test PRD Feature","status":"Discovery","created":"2026-08-09"}
```

### 2. spec.md takes precedence over prd.md

```bash
# In a feature dir with both files, spec.md status should win
# Create spec.md alongside the prd.md above:
echo '# Feature Specification: Test Feature
**Status**: Planning
**Created**: 2026-08-09' > /tmp/lifecycle-test/specs/001-test-prd/spec.md

# Re-run scan-specs.sh
# Expected: status is "Planning" (from spec.md), not "Discovery" (from prd.md)
```

### 3. Status change command

```bash
# Run the status-change script to set a feature's status
bash bundle/extensions/trasgospec/scripts/bash/status-change.sh set planning
# Expected: JSON with success=true, old_status and new_status fields

# Verify the file was updated
grep '**Status**' specs/009-spec-lifecycle-management/spec.md
# Expected: **Status**: Planning
```

### 4. Unblock from git history

```bash
# Set status to Blocked, commit, then unblock
bash bundle/extensions/trasgospec/scripts/bash/status-change.sh set blocked
git add specs/009-spec-lifecycle-management/spec.md && git commit -m "test: block feature"

bash bundle/extensions/trasgospec/scripts/bash/status-change.sh unblock
# Expected: status reverts to previous value recovered from git log
```

### 5. Quality gate for Opportunity

```bash
# Try to advance a PRD missing sections to Opportunity
bash bundle/extensions/trasgospec/scripts/bash/status-change.sh set opportunity
# Expected: success=false with gate_failures listing missing sections
```

### 6. Run unit tests

```bash
.venv/bin/pytest tests/unit/test_scan_specs.py -v
.venv/bin/pytest tests/unit/test_status_change.py -v
```

### 7. Roadmap displays all phases

```bash
# Run the roadmap skill and verify PRD-only and spec features both appear
# /speckit-trasgospec-roadmap
```
