# Data Model: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## Entities

### FeatureSpec

A single feature specification extracted from a `specs/` subdirectory.

| Field    | Source                                        | Fallback   |
|----------|-----------------------------------------------|------------|
| id       | Directory name prefix (e.g., `001`)           | Directory name |
| title    | `# Feature Specification: [TITLE]` heading    | Directory name (without prefix) |
| status   | `**Status**: [VALUE]` field                   | "Unknown"  |
| created  | `**Created**: [DATE]` field                   | "Unknown"  |

**Identity**: Each FeatureSpec is uniquely identified by its directory name
within `specs/`.

**Ordering**: Specs are ordered by their directory name (natural sort),
which respects both sequential (`001-`, `002-`) and timestamp-based
(`20260808-143022-`) naming conventions.

### RoadmapView

An aggregated, ordered collection of FeatureSpec summaries.

| Field       | Description                                      |
|-------------|--------------------------------------------------|
| specs       | Ordered list of FeatureSpec entries               |
| total_count | Number of valid specs found                       |

**Empty state**: When `specs` is empty, the roadmap displays a message
indicating no features have been specified yet.

## Relationships

```text
RoadmapView 1──* FeatureSpec
```

A RoadmapView contains zero or more FeatureSpecs. The relationship is
read-only — the roadmap never modifies FeatureSpec data.

## Validation Rules

- A directory is a valid FeatureSpec only if it contains a `spec.md` file
- Missing metadata fields use fallback values (never errors)
- Empty `spec.md` files produce a FeatureSpec with all fallback values
- Non-spec directories (no `spec.md`) are silently skipped
