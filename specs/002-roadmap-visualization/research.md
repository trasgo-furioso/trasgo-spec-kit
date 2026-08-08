# Research: Roadmap Visualization

**Feature**: 002-roadmap-visualization
**Date**: 2026-08-08

## R1: Spec Status Values

**Decision**: Spec statuses are free-form text fields; no official enum exists.

**Rationale**: Research confirms that Spec Kit's `spec-template.md` sets
`**Status**: Draft` as the default but does not define an enumeration of
valid values. The `**Status**:` field is a plain markdown bold-text pattern
that can contain any string. The roadmap skill should read and display
whatever value is present without validation.

**Alternatives considered**:
- Hardcoded enum (Draft, In Progress, Complete) — rejected because Spec Kit
  does not enforce this and users may use custom statuses.

## R2: Skill Format and Invocation

**Decision**: Use a Markdown-only SKILL.md file in
`bundle/skills/trasgospec-roadmap/` with natural-language instructions for
the AI agent.

**Rationale**: The existing `trasgospec` skill demonstrates this pattern.
Spec Kit skills for the `claude` integration are Markdown instruction files
interpreted by the AI agent at invocation time. The skill name
`trasgospec-roadmap` follows the bundle-id prefix convention and matches
the user's requested trigger `/trasgospec-roadmap`.

**Alternatives considered**:
- Shell script skill — rejected because the bundle targets the `claude`
  integration, which uses Markdown-based skills.
- Embedding logic in an extension — rejected per Constitution Principle I
  (Composition Over Creation): bundles must not add runtime behavior.

## R3: Metadata Extraction Approach

**Decision**: The SKILL.md instructions direct the AI agent to scan `specs/`
subdirectories, read each `spec.md`, and extract metadata using the standard
spec template field patterns.

**Rationale**: All spec files follow the template format with predictable
field markers:
- Title: `# Feature Specification: [TITLE]`
- Status: `**Status**: [VALUE]`
- Created: `**Created**: [DATE]`
- ID: derived from the directory name (e.g., `001` from `001-bundle-install`)

The AI agent has filesystem access and can parse these patterns reliably.

**Alternatives considered**:
- Index file or metadata cache — rejected as over-engineering for the
  current scope and would require write operations.

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
when adding the new skill.

**Rationale**: Adding a new skill is a backward-compatible feature addition,
which warrants a minor version bump per semantic versioning. The existing
`trasgospec` skill and catalog entry remain unchanged.

**Alternatives considered**:
- Patch bump (0.1.1) — rejected because adding a new skill is a feature,
  not a fix.
- Major bump (1.0.0) — rejected because no breaking changes are introduced.
