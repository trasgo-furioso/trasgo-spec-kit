# Quickstart: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## Prerequisites

- Spec Kit (`specify` CLI) installed, version >= 0.15.0
- Trasgo Spec Kit bundle installed (v0.2.0+)
- A Spec Kit project with at least one feature spec in `specs/`

## Validation Scenarios

### Scenario 1: View Roadmap with Multiple Specs

1. Open a Spec Kit project that has 2+ feature specs in `specs/`
2. Invoke `/trasgospec-roadmap`
3. **Expected**: A markdown table listing all specs with columns ID, Title, Status, Created, ordered by spec number

Example output:
```markdown
| ID  | Title                  | Status | Created    |
|-----|------------------------|--------|------------|
| 001 | Bundle Install         | Draft  | 2026-08-07 |
| 002 | Roadmap Visualization  | Draft  | 2026-08-08 |
```

### Scenario 2: Empty Project

1. Open a Spec Kit project with no `specs/` directory or an empty one
2. Invoke `/trasgospec-roadmap`
3. **Expected**: A clear message indicating no features have been specified yet

### Scenario 3: Spec with Missing Metadata

1. Create a spec directory with a `spec.md` that has no `**Status**:` field
2. Invoke `/trasgospec-roadmap`
3. **Expected**: The spec appears in the table with "Unknown" for the missing field

### Scenario 4: Directory Without spec.md

1. Create a subdirectory in `specs/` that contains no `spec.md` file
2. Invoke `/trasgospec-roadmap`
3. **Expected**: That directory is silently skipped; other valid specs display normally

## Running Tests

```bash
cd /Users/trasgofurioso/Code/trasgo-spec-kit
pytest tests/integration/test_us1_roadmap.py -v
```
