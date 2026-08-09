# Research: Spec Lifecycle Management

## R1: Extending scan-specs.sh for PRD scanning

**Decision**: Extend the existing loop in `scan-specs.sh` to also check for `prd.md` when `spec.md` is absent, and extract title from `# PRD:` heading pattern.

**Rationale**: The current script skips directories without `spec.md` (line 77: `[ -f "$spec_dir/spec.md" ] || continue`). Changing this to a precedence check (`spec.md` first, then `prd.md`) adds PRD-only features to the roadmap while maintaining backward compatibility. The `# PRD:` heading pattern mirrors `# Feature Specification:` — same extraction logic, different prefix.

**Alternatives considered**:
- Separate `scan-prds.sh` script: rejected because it duplicates scanning logic and requires merging results in the command file.
- Scanning both files and merging: rejected because the spec says spec.md takes precedence, so we only need one file per directory.

## R2: Status field in prd.md

**Decision**: The discovery command already writes `**Status**: Discovery` to prd.md (as of the lifecycle feature PRD structure). The scan script reads this field identically to how it reads it from spec.md — same regex, same fallback.

**Rationale**: Uniform parsing. The `**Status**:` pattern is already established. No new parsing logic needed.

**Alternatives considered**:
- Separate status storage (JSON sidecar): rejected per clarification — status lives in the markdown file's `**Status**` field.

## R3: Status change script — git log for unblock

**Decision**: The `status-change.sh` script uses `git log -1 --diff-filter=M -p -- <file> | grep '^\-\*\*Status\*\*:'` to find the previous status value when unblocking.

**Rationale**: Per clarification, git history is the source of truth. The script diffs the file's last modification to find the removed `**Status**:` line, which contains the prior phase. This avoids adding metadata fields.

**Alternatives considered**:
- `**Previous Status**:` field: rejected per clarification.
- Sidecar `.status.json`: rejected per clarification.

## R4: Hook registration pattern for status transitions

**Decision**: Register `trasgospec.roadmap.status.change` as hooks in `extension.yml` at the four transition points defined in the spec:
- `before_specify` → set "Planning"
- `after_plan` → set "Ready to Dev"
- `before_tasks` → set "In Progress"
- `after_implement` → set "In Review"

**Rationale**: Follows the existing hook pattern (flow-gate, flow-nudge). Each hook entry specifies the target status as part of the command args passed through the hook. The status-change command accepts the target status as an argument.

**Alternatives considered**:
- Single hook that infers phase from context: rejected because it couples the status command to skill-specific knowledge.
- Inline status update in each skill: rejected because it bypasses the extension hook mechanism and violates Composition Over Creation.

## R5: Command naming — dot notation

**Decision**: Command ID is `speckit.trasgospec.roadmap.status.change`, invoked as `/speckit-trasgospec-roadmap-status-change`. Alias: `trasgospec.roadmap.status.change` → `/trasgospec-roadmap-status-change`.

**Rationale**: Follows established naming convention. The `roadmap` namespace groups it with the roadmap visualization command. Dots map to hyphens at invocation.

**Alternatives considered**:
- `speckit.trasgospec.status`: shorter but doesn't communicate the roadmap association.
- `speckit.trasgospec.lifecycle`: too abstract.
