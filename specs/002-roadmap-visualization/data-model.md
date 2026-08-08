# Data Model: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## Entities

### FeatureSpec

A single feature specification extracted from a `specs/` subdirectory
by the `scan-specs.sh` script.

| Field   | Type   | Source                                     | Fallback          |
|---------|--------|--------------------------------------------|-------------------|
| id      | string | Directory name (e.g., `001-bundle-install`) | Directory name    |
| title   | string | `# Feature Specification: [TITLE]` heading | Directory name (without numeric prefix) |
| status  | string | `**Status**: [VALUE]` field                | "Unknown"         |
| created | string | `**Created**: [DATE]` field                | "Unknown"         |

**Identity**: Each FeatureSpec is uniquely identified by its directory
name within `specs/`.

**Ordering**: Specs are ordered by their directory name (natural sort),
which respects both sequential (`001-`, `002-`) and timestamp-based
(`20260808-143022-`) naming conventions. Sorting is done by the script.

### ScanResult

The JSON contract emitted by `scan-specs.sh` on stdout.

| Field     | Type           | Description                            |
|-----------|----------------|----------------------------------------|
| specs_dir | string         | Relative path to specs directory       |
| specs     | FeatureSpec[]  | Ordered array of extracted spec entries |

**Empty state**: When no valid specs are found, `specs` is an empty
array `[]`. The command (AI layer) renders the empty-state message.

## Relationships

```text
ScanResult 1──* FeatureSpec
```

A ScanResult contains zero or more FeatureSpecs. The relationship is
read-only — neither the script nor the command modifies spec data.

## Validation Rules

- A directory is a valid FeatureSpec only if it contains a `spec.md` file
- Missing metadata fields use fallback values at the script level
- Empty `spec.md` files produce a FeatureSpec with all fallback values
- Non-spec directories (no `spec.md`) are silently skipped by the script
- The JSON output is always valid, even for zero specs (empty array)
