# Contract: status-change.sh

## Script Interface

**Location**: `bundle/extensions/trasgospec/scripts/bash/status-change.sh`

**Invocation**:
```bash
status-change.sh <action> [args...]
```

### Actions

| Action | Args | Description |
|--------|------|-------------|
| `set` | `<phase>` | Set status to the given phase |
| `blocked` | (none) | Set status to "Blocked" |
| `unblock` | (none) | Restore status from git history |
| `validate` | (none) | Check current status and output it |

### Arguments

- `<phase>`: One of `discovery`, `opportunity`, `planning`, `ready-to-dev`, `in-progress`, `in-review`, `delivered` (case-insensitive, stored as title case)
- Feature directory is resolved from `.specify/feature.json`

### Stdout (single-line JSON)

**Success**:
```json
{"feature_dir":"specs/009-...","file":"spec.md","old_status":"Planning","new_status":"Ready to Dev","success":true}
```

**Unblock success**:
```json
{"feature_dir":"specs/009-...","file":"spec.md","old_status":"Blocked","new_status":"Planning","recovered_from":"git","success":true}
```

**Quality gate failure** (when setting Opportunity on a prd.md):
```json
{"feature_dir":"specs/011-...","file":"prd.md","old_status":"Discovery","new_status":"Opportunity","success":false,"gate_failures":["Missing: Assumptions"]}
```

**Validation error** (invalid phase name):
```json
{"success":false,"error":"Invalid phase: foo","valid_phases":["Discovery","Opportunity","Planning","Ready to Dev","In Progress","In Review","Delivered","Blocked"]}
```

### Stderr

Diagnostic messages (e.g., "Reading previous status from git log...")

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (status changed or validated) |
| 1 | Error (invalid args, file not found, git history unavailable for unblock) |
| 0 | Quality gate failure (success=false in JSON, but script exits 0 for parseable output) |

## File Selection Logic

1. Read `feature_directory` from `.specify/feature.json`
2. If `spec.md` exists in that directory → use it
3. Else if `prd.md` exists → use it
4. Else → error

## Status Update Mechanism

1. Read the file
2. Find the line matching `**Status**: <value>`
3. Replace with `**Status**: <new_value>`
4. Write the file back

## Unblock Mechanism

1. Identify the target file (spec.md or prd.md)
2. Run: `git log -1 --diff-filter=M -p -- <file>`
3. Extract the removed line: `grep '^\-\*\*Status\*\*:' | head -1`
4. Parse the old status value from that line
5. Set status to the recovered value

## Quality Gate (Opportunity only)

When target phase is "Opportunity" and file is prd.md:

1. Check each required section for non-empty content:
   - `**Pain Point**:` has content after the colon
   - `**Who**:` has content after the colon
   - `**Current Alternatives**:` has content after the colon
   - `**Desired Outcome**:` has content after the colon
   - `## Jobs to Be Done` section has at least one `- When` bullet
   - `## Assumptions` section has at least one `- ` bullet
2. If any check fails → return `success: false` with `gate_failures` array
3. If all pass → proceed with status change

# Contract: scan-specs.sh (changes)

## Extended File Selection

**Current** (line 77):
```bash
[ -f "$spec_dir/spec.md" ] || continue
```

**New**:
```bash
# Determine which file to scan (spec.md takes precedence)
if [ -f "$spec_dir/spec.md" ]; then
    spec_file="$spec_dir/spec.md"
elif [ -f "$spec_dir/prd.md" ]; then
    spec_file="$spec_dir/prd.md"
else
    continue
fi
```

## Extended Title Extraction

**Current**: Only matches `# Feature Specification:`

**New**: Also matches `# PRD:` as fallback
```bash
title_line="$(grep -m1 '^# Feature Specification:\|^# PRD:' "$spec_file" 2>/dev/null || true)"
if [ -n "$title_line" ]; then
    # Try Feature Specification first
    case "$title_line" in
        "# Feature Specification:"*)
            title="${title_line#\# Feature Specification: }" ;;
        "# PRD:"*)
            title="${title_line#\# PRD: }" ;;
    esac
fi
```

## JSON Output

No schema change. Same `{"specs_dir":"specs","specs":[...]}` format.
