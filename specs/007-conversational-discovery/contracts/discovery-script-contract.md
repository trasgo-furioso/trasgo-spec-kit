# Contract: discovery.sh Script Output

## Invocation

```bash
discovery.sh [--json] [slug-hint]
```

- `--json`: Required. Emit JSON on stdout.
- `slug-hint`: Optional. A brief feature name hint to use for the directory slug. If omitted, the script uses a timestamp-based fallback.

## JSON Output (stdout, single line)

```json
{
  "spec_dir": "specs/008-feature-name",
  "spec_number": "008",
  "slug": "feature-name",
  "prd_path": "specs/008-feature-name/prd.md",
  "feature_json_updated": true
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `spec_dir` | string | Relative path to the created spec directory |
| `spec_number` | string | Zero-padded 3-digit sequential number |
| `slug` | string | Kebab-case slug derived from the hint or fallback |
| `prd_path` | string | Relative path to the scaffolded `prd.md` |
| `feature_json_updated` | boolean | Whether `.specify/feature.json` was updated |

## Side Effects

1. Creates directory `specs/<NNN-slug>/`
2. Creates empty scaffold `specs/<NNN-slug>/prd.md` with section headers only
3. Updates `.specify/feature.json` with `{"feature_directory": "specs/<NNN-slug>"}`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success — directory created, JSON emitted |
| 1 | Fatal error — not a Spec Kit project or filesystem error |

## Sequencing Logic

1. Scan all directories matching `specs/[0-9]*` pattern
2. Extract numeric prefixes, find the maximum
3. Next number = max + 1 (or 001 if no existing specs)
4. Zero-pad to 3 digits

## PRD Scaffold

The script creates `prd.md` with this content (headers only, no body text):

```markdown
# PRD: [slug as title case]

**Created**: [YYYY-MM-DD]
**Discovery Session**: [YYYY-MM-DD]

## Problem Statement

**Pain Point**:

**Who**:

**Current Alternatives**:

**Desired Outcome**:

## User Stories Overview

## Assumptions

## Research Findings
```

## Bash 3.2 Compatibility

- No `mapfile` or `readarray`
- No associative arrays
- Uses `set -euo pipefail`
- Sources `common.sh` opportunistically with inline `json_escape` fallback
- Locates repo root via `_find_specify_root` walk-up
