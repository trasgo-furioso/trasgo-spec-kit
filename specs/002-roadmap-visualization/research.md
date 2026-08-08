# Research: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## R1: Spec Status Values

**Decision**: Spec statuses are free-form text fields; no official enum exists.

**Rationale**: Research confirms that Spec Kit's `spec-template.md` sets
`**Status**: Draft` as the default but does not define an enumeration of
valid values. The `**Status**:` field is a plain markdown bold-text pattern
that can contain any string. The script should read and output whatever
value is present without validation.

**Alternatives considered**:
- Hardcoded enum (Draft, In Progress, Complete) — rejected because Spec Kit
  does not enforce this and users may use custom statuses.

## R2: Architecture — Extension Pattern (Command + Script)

**Decision**: Implement as a Spec Kit extension with two components:
- `bundle/commands/speckit.trasgospec.roadmap.md` — command file with YAML
  frontmatter (description, `scripts:` section) and AI agent instructions
- `bundle/scripts/bash/scan-specs.sh` — deterministic shell script that
  scans specs and emits JSON

**Rationale**: The constitution was amended (v1.1.0) to allow runtime
behavior via the Spec Kit extension development pattern. This pattern
cleanly separates concerns:
- **Script**: deterministic filesystem scanning, metadata extraction,
  JSON output. No judgment, no AI calls. Testable in isolation.
- **Command**: AI agent instructions for running the script, parsing
  JSON output, and rendering the markdown table. Handles presentation
  and edge-case messaging.

The pattern follows the established convention demonstrated by the
roadmap extension's `load-config.sh` + command structure.

**Alternatives considered**:
- Pure skill (SKILL.md only, AI does all scanning) — rejected because it
  relies entirely on AI for deterministic filesystem work, making results
  non-reproducible and harder to test.
- Pure shell script (no AI instructions) — rejected because rendering
  decisions (empty state messaging, fallback labels) benefit from AI
  judgment in the command layer.

## R3: Script Design — scan-specs.sh

**Decision**: The script scans `specs/` subdirectories, reads each
`spec.md`, extracts metadata via grep/sed patterns, and emits a
single-line JSON array on stdout.

**Rationale**: Following the `load-config.sh` conventions:
- Bash 3.2+ compatible (macOS default)
- `set -euo pipefail` for safety
- Repo root resolution via `find_specify_root` (from core `common.sh`)
  with fallback
- `json_escape` sourced from core `common.sh` with inline fallback
- Single-line JSON output for reliable parsing
- Exit code 0 on success (even if no specs found — empty array is valid)

Field extraction patterns:
- Title: `grep -m1 '^# Feature Specification:'` → strip prefix
- Status: `grep -m1 '^\*\*Status\*\*:'` → strip prefix/formatting
- Created: `grep -m1 '^\*\*Created\*\*:'` → strip prefix/formatting
- ID: directory name (the full directory name, e.g., `001-bundle-install`)

**Alternatives considered**:
- Python script — rejected because adding Python as a runtime dependency
  violates the bundle constraint (Python is dev-only for testing).
- jq for JSON construction — rejected because jq is not guaranteed on
  macOS out of the box; pure bash JSON construction is sufficient.

## R4: Output Format

**Decision**: Markdown table with columns ID, Title, Status, Created.

**Rationale**: Confirmed during `/speckit-clarify` (Session 2026-08-08).
Markdown tables are scannable, render well in CLI and markdown-aware tools,
and are the most structured option for tabular data.

**Alternatives considered**:
- Bulleted list — less scannable for structured data
- Plain text aligned columns — no markdown rendering benefits

## R5: Bundle Version Strategy

**Decision**: Bump bundle version from 0.1.0 to 0.2.0 (minor version)
when adding the new command.

**Rationale**: Adding a new command with runtime behavior is a
backward-compatible feature addition, which warrants a minor version
bump per semantic versioning. The existing `trasgospec` skill and
catalog entry remain unchanged.

**Alternatives considered**:
- Patch bump (0.1.1) — rejected because adding a command is a feature.
- Major bump (1.0.0) — rejected because no breaking changes are introduced.

## R6: Command Naming Convention

**Decision**: Command ID is `speckit.trasgospec.roadmap` (dot-namespaced),
invoked as `/speckit-trasgospec-roadmap` (dots replaced with hyphens).

**Rationale**: Follows the Spec Kit extension naming convention where
dots in command IDs map to hyphens in invocation. The `speckit.trasgospec`
prefix scopes the command under the bundle namespace.

**Alternatives considered**:
- Flat name `trasgospec-roadmap` — rejected because it doesn't follow
  the extension naming convention with dot namespacing.

## R7: Script JSON Contract

**Decision**: Script outputs a single-line JSON object with a `specs`
array and `specs_dir` path:

```json
{"specs_dir":"specs","specs":[{"id":"001-bundle-install","title":"Bundle Install","status":"Draft","created":"2026-08-07"}]}
```

**Rationale**: Mirrors the `load-config.sh` pattern of emitting a stable
JSON contract. The `specs_dir` field provides context. Each spec entry
contains exactly the four fields needed for the markdown table (ID,
Title, Status, Created). Missing fields use fallback values in the
script itself (deterministic), not the AI layer.

**Alternatives considered**:
- AI agent does the parsing — rejected because it makes results
  non-deterministic and harder to test.
- Script outputs markdown directly — rejected because presentation
  belongs in the command layer (AI judgment for edge cases).
