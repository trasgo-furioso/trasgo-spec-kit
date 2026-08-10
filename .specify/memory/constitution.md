<!--
Sync Impact Report
  Version change: 1.3.0 → 1.4.0 (MINOR)
  Modified principles: none
  Added sections: Principle VII (Template-Driven Artifacts)
  Removed sections: none
  Follow-up TODOs: none
-->

# Trasgo Spec Kit Constitution

## Core Principles

### I. Composition Over Creation

Every new behavior MUST compose existing Spec Kit primitives (commands, presets,
templates, hooks). New behavior MUST use the extension pattern — command file plus
script file. Creating parallel systems that duplicate Spec Kit capabilities is
prohibited.

### II. Spec Kit Native

All features MUST use existing Spec Kit features (presets, templates, hooks,
bundle distribution). Never duplicate a capability that Spec Kit already provides.
If Spec Kit lacks a needed capability, contribute upstream or document the gap —
do not work around it.

### III. Documentation-Driven Development

Consult Spec Kit documentation before making tooling choices. The official docs
define the canonical way to achieve a goal. Deviating from documented patterns
requires explicit justification recorded in the spec or plan.

### IV. Idempotent & Traceable

All installations MUST be idempotent — running `specify bundle install` twice
produces the same result. Full provenance tracking is required: every artifact
MUST be traceable to its source bundle, version, and build.

### V. Version-Pinned Distribution

All manifests (`bundle.yml`, `extension.yml`) MUST use explicit version pins.
No floating versions, no unpinned dependencies. Version numbers follow semantic
versioning (MAJOR.MINOR.PATCH).

### VI. Test-Driven Development

Tests MUST be written first (red-green-refactor cycle). Every implementation task
begins with a failing test before writing production code. Tests use pytest only.
Manual shell test execution is prohibited — all validation goes through the test
suite.

### VII. Template-Driven Artifacts

Every command that produces an artifact MUST have an associated template that
users can override to tailor the output. Templates are distributed via the
bundle's preset `templates/` directory and resolved through the Spec Kit preset
resolution stack (`specify preset resolve <template-name>`). Users override
templates by placing files in `.specify/templates/overrides/`. Commands MUST
fall back to a hardcoded default if the template cannot be resolved.

## Extension Two-Part Pattern

Every extension command MUST follow the two-part pattern:

1. **Command file** (`commands/<dot.namespaced.id>.md`) — YAML frontmatter
   (`description`, `scripts`) plus markdown body with AI agent instructions.
   The command invokes the script, parses JSON, and renders output. It MUST NOT
   perform deterministic work itself.

2. **Script file** (`scripts/bash/<name>.sh`) — deterministic only, no AI calls.
   Emits single-line JSON on stdout, diagnostics on stderr. MUST target bash 3.2+
   (no `mapfile`, no `readarray`). MUST use `set -euo pipefail`. MUST locate repo
   root via `_find_specify_root` walk-up, not assume CWD.

## Naming Convention

Command IDs use dot namespacing: `speckit.trasgospec.<name>`. Dots map to hyphens
at invocation: `/speckit-trasgospec-<name>`. Aliases without the `speckit.` prefix
are registered (e.g., `trasgospec.<name>`).

## Governance

This constitution supersedes all other practices when conflicts arise. Amendments
require:

1. A documented rationale in the relevant spec or PR.
2. Version bump following semantic versioning (MAJOR for removals/redefinitions,
   MINOR for additions, PATCH for clarifications).
3. Update to CLAUDE.md to reflect the change.

All PRs and reviews MUST verify compliance with these principles.

**Version**: 1.4.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-08-10
