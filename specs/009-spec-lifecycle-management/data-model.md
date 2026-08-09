# Data Model: Spec Lifecycle Management

## Entities

### Lifecycle Phase

A finite set of named phases representing the progression of a feature from ideation to delivery.

**Values** (title case, ordered):

| Phase | Description | Transition Trigger |
|-------|-------------|-------------------|
| Discovery | PRD in progress | Manual (discovery command sets on prd.md creation) |
| Opportunity | PRD complete, validated | Manual (`/trasgospec-roadmap-status-change`) |
| Planning | Spec and plan being written | Auto (`before_specify` hook) |
| Ready to Dev | Spec and plan complete | Auto (`after_plan` hook) |
| In Progress | Tasks and implementation underway | Auto (`before_tasks` hook) |
| In Review | PR open, team reviewing | Auto (`after_implement` hook) |
| Delivered | Branch merged to main | Manual (`/trasgospec-roadmap-status-change`) |
| Blocked | Human decision needed (lateral) | Manual (user or agent) |

**Storage**: Persisted as the value of `**Status**: <Phase>` in prd.md or spec.md.

**Validation**: The status-change script validates input against this exact set (case-insensitive match, stored as title case).

**State transitions**: Not enforced as a strict state machine. Any phase can transition to any other phase. Backward transitions are valid.

### Feature

A directory under `specs/` containing at minimum one of:
- `prd.md` (PRD-only feature, phases: Discovery, Opportunity)
- `spec.md` (fully-specced feature, phases: Planning through Delivered)

**Precedence rule**: When both `prd.md` and `spec.md` exist, `spec.md` is the authoritative source for title, status, and created date.

**Identity**: The directory name (e.g., `009-spec-lifecycle-management`) serves as the feature ID.

**Metadata extraction patterns**:

| Field | Pattern (spec.md) | Pattern (prd.md) | Fallback |
|-------|-------------------|-------------------|----------|
| Title | `# Feature Specification: <title>` | `# PRD: <title>` | Directory name |
| Status | `**Status**: <value>` | `**Status**: <value>` | "Unknown" |
| Created | `**Created**: <date>` | `**Created**: <date>` | "Unknown" |

### Quality Gate

A set of completeness checks applied to a PRD to determine eligibility for Opportunity status.

**Required sections** (all must be non-empty):
- `**Pain Point**:`
- `**Who**:`
- `**Current Alternatives**:`
- `**Desired Outcome**:`
- `## Jobs to Be Done` (must have at least one `- When` bullet)
- `## Assumptions` (must have at least one `- ` bullet)

**Evaluation**: Performed by the status-change script when the target phase is "Opportunity" and the source file is prd.md.

## Relationships

```
Feature 1──1 Lifecycle Phase (current)
Feature 1──0..1 prd.md
Feature 1──0..1 spec.md
Quality Gate ──evaluates──> prd.md
```

## JSON Contracts

### scan-specs.sh output (extended)

```json
{
  "specs_dir": "specs",
  "specs": [
    {
      "id": "009-spec-lifecycle-management",
      "title": "Spec Lifecycle Management",
      "status": "Planning",
      "created": "2026-08-09"
    },
    {
      "id": "011-audit-and-logs",
      "title": "Audit and Logs",
      "status": "Discovery",
      "created": "2026-08-09"
    }
  ]
}
```

No schema change — same fields, same structure. The only change is that PRD-only features now appear in the array.

### status-change.sh output

```json
{
  "feature_dir": "specs/009-spec-lifecycle-management",
  "file": "spec.md",
  "old_status": "Planning",
  "new_status": "Ready to Dev",
  "success": true
}
```

For unblock:
```json
{
  "feature_dir": "specs/009-spec-lifecycle-management",
  "file": "spec.md",
  "old_status": "Blocked",
  "new_status": "Planning",
  "recovered_from": "git",
  "success": true
}
```

For quality gate failure:
```json
{
  "feature_dir": "specs/011-audit-and-logs",
  "file": "prd.md",
  "old_status": "Discovery",
  "new_status": "Opportunity",
  "success": false,
  "gate_failures": ["Missing: Jobs to Be Done", "Missing: Assumptions"]
}
```
