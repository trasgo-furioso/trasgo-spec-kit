# Quickstart: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## Prerequisites

- Spec Kit (`specify` CLI) installed, version >= 0.15.0
- Trasgo Spec Kit bundle installed (v0.2.0+)
- Python 3.11+ with pytest (dev-only)

## Running Tests

All validation is done through pytest. Never run bash commands
manually — encapsulate them in tests.

### Unit Tests (script contract)

```bash
cd /Users/trasgofurioso/Code/trasgo-spec-kit
pytest tests/unit/test_scan_specs.py -v
```

Validates: JSON contract output, metadata extraction, fallback
values, directory filtering, sorting, special character escaping.

### Integration Tests (acceptance scenarios)

```bash
# US1: View project roadmap
pytest tests/integration/test_us1_roadmap.py -v

# US2: Empty/single-spec projects
pytest tests/integration/test_us2_roadmap.py -v

# US3: Incomplete specs
pytest tests/integration/test_us3_roadmap.py -v
```

### Full Suite

```bash
pytest tests/ -v
```

## Validation Scenarios

### Scenario 1: Multiple Specs (US1)

Test creates a `tmp_path` project with 3 spec directories, each
containing a `spec.md` with different statuses. Runs `scan-specs.sh`
and asserts JSON output contains all 3 specs ordered by directory
name.

Expected JSON (see [contract](contracts/scan-specs-output.md)):
```json
{"specs_dir":"specs","specs":[{"id":"001-alpha","title":"Alpha","status":"Draft","created":"2026-08-01"},{"id":"002-beta","title":"Beta","status":"In Progress","created":"2026-08-02"},{"id":"003-gamma","title":"Gamma","status":"Complete","created":"2026-08-03"}]}
```

### Scenario 2: Empty Project (US2)

Test creates a `tmp_path` project with no `specs/` directory.
Runs script and asserts `{"specs_dir":"specs","specs":[]}`.

### Scenario 3: Missing Metadata (US3)

Test creates a `spec.md` missing the `**Status**:` field.
Runs script and asserts the entry has `"status":"Unknown"`.

### Scenario 4: End-to-End Command

After all tests pass, invoke `/speckit-trasgospec-roadmap` in this
project and verify markdown table output matches the script's JSON
data.
