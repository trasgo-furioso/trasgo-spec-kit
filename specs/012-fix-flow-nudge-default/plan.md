# Implementation Plan: Fix Flow-Nudge Default Execution

**Branch**: `012-fix-flow-nudge-default` | **Date**: 2026-08-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/012-fix-flow-nudge-default/spec.md`

## Summary

Rename `flow-nudge` to `deliver`, change all deliver hook registrations from `optional: true` to `optional: false`, remove confirmation prompts from the command, add template-driven PR creation via `pr-template.md`, add template-driven commit messages via `commit-template.md`, and create a bundle preset to distribute both templates.

## Technical Context

**Language/Version**: Bash 3.2+ (scripts), Markdown (commands/templates)

**Primary Dependencies**: Spec Kit >=0.15.0, `gh` CLI (optional, graceful fallback)

**Storage**: N/A — all state is in `extension.yml`, `spec.md`, and git

**Testing**: pytest (unit tests in `tests/unit/`)

**Target Platform**: macOS/Linux (bash 3.2+ compatible)

**Project Type**: CLI extension bundle

**Performance Goals**: N/A — configuration and template changes

**Constraints**: Bash 3.2+ compatibility (no `mapfile`, no `readarray`)

**Scale/Scope**: 4 hook registrations, 2 templates, 1 command rename, 1 command rewrite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | Using existing Spec Kit preset/template system |
| II. Spec Kit Native | PASS | Templates distributed via presets, resolved via `specify preset resolve` |
| III. Documentation-Driven Development | PASS | Research confirmed preset structure from Spec Kit docs |
| IV. Idempotent & Traceable | PASS | `specify bundle install` is idempotent; templates land at deterministic paths |
| V. Version-Pinned Distribution | PASS | Bundle version 0.9.0, preset version pinned in `preset.yml` |
| VI. Test-Driven Development | PASS | Tests for hook registration validation and script JSON contract |
| VII. Template-Driven Artifacts | PASS | This feature implements this principle for deliver and commit commands |

## Project Structure

### Documentation (this feature)

```text
specs/012-fix-flow-nudge-default/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
bundle/
├── bundle.yml                                          # ADD provides.presets entry
├── presets/
│   └── trasgospec/
│       ├── preset.yml                                  # NEW — preset manifest
│       └── templates/
│           ├── pr-template.md                          # NEW — PR title/body template
│           └── commit-template.md                      # NEW — commit message format template
└── extensions/
    └── trasgospec/
        ├── extension.yml                               # MODIFY — rename hooks, set optional: false
        ├── commands/
        │   ├── speckit.trasgospec.deliver.md            # NEW (replaces flow-nudge.md)
        │   └── speckit.trasgospec.commit.md             # MODIFY — add template resolution
        └── scripts/
            └── bash/
                └── deliver.sh                          # NEW (replaces flow-nudge.sh)

tests/
└── unit/
    ├── test_deliver.py                                 # NEW — deliver script JSON contract tests
    └── test_commit_template.py                         # NEW — commit template resolution tests
```

**Structure Decision**: Existing bundle structure extended with a `presets/trasgospec/` directory for template distribution. No new top-level directories. Old `flow-nudge` files are replaced, not kept alongside.

## Implementation Workstreams

### W1: Rename flow-nudge → deliver (FR-001)

1. Rename `commands/speckit.trasgospec.flow-nudge.md` → `commands/speckit.trasgospec.deliver.md`
2. Rename `scripts/bash/flow-nudge.sh` → `scripts/bash/deliver.sh`
3. Update `extension.yml`: command registration name, file path, aliases
4. Update all hook registrations from `speckit.trasgospec.flow-nudge` → `speckit.trasgospec.deliver`
5. Delete old files

### W2: Set hooks to optional: false (FR-002, FR-003)

1. Change all 4 deliver hook registrations to `optional: false` in `bundle/extensions/trasgospec/extension.yml`
2. Mirror changes to installed copy at `.specify/extensions/trasgospec/extension.yml`

### W3: Remove confirmation prompts (FR-004)

1. Rewrite `speckit.trasgospec.deliver.md` command file:
   - Remove "Offer: Open a draft PR? [Y/n]" prompt for `create_draft`
   - Remove "Mark PR as ready for review? [Y/n]" prompt for `mark_ready`
   - Execute `gh pr create` / `gh pr ready` directly
   - Display result or error

### W4: Create bundle preset with templates (FR-007, FR-008, FR-010, FR-011)

1. Create `bundle/presets/trasgospec/preset.yml`
2. Create `bundle/presets/trasgospec/templates/pr-template.md` with:
   - Frontmatter: `title: "feat({{spec_dir}}): {{spec_title}}"`
   - Body: PR description with `{{spec_title}}` and `{{spec_summary}}` placeholders
3. Create `bundle/presets/trasgospec/templates/commit-template.md` with:
   - Body: Format instructions for one-line-per-file commit messages
4. Update `bundle/bundle.yml` to declare preset under `provides.presets`

### W5: Update deliver command for template resolution (FR-008)

1. In the deliver command file, add logic to:
   - Resolve `pr-template` via `specify preset resolve pr-template` (or read from known path)
   - Parse YAML frontmatter for `title` pattern
   - Read markdown body for PR body pattern
   - Interpolate `{{spec_title}}` and `{{spec_summary}}`
   - Pass interpolated title and body to `gh pr create`
   - Fall back to hardcoded defaults if template not found

### W6: Update commit command for template resolution (FR-011)

1. In the commit command file, add logic to:
   - Resolve `commit-template` via `specify preset resolve commit-template` (or read from known path)
   - Use template instructions when composing commit messages
   - Fall back to hardcoded default format if template not found

### W7: Error handling (FR-005, FR-009)

1. Deliver command: when `gh` unavailable or `gh_integration: false`, display suggestion block
2. Deliver command: when `gh pr create`/`gh pr ready` fails, display error, exit 0
3. Already implemented in flow-nudge.sh script — verify behavior carries over to deliver.sh

### W8: Tests

1. Unit tests for deliver.sh JSON contract (same as flow-nudge.sh but renamed)
2. Unit tests verifying hook registrations in extension.yml use `optional: false`
3. Unit tests for template file existence in preset directory
