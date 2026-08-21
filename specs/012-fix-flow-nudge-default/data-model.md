# Data Model: Fix Flow-Nudge Default Execution

**Date**: 2026-08-10

## Entities

### Template File

A markdown file with YAML frontmatter distributed in the bundle's preset. Resolved via `specify preset resolve <name>`.

| Field | Location | Description |
|-------|----------|-------------|
| `title` | YAML frontmatter | Title pattern with `{{placeholder}}` interpolation (pr-template only) |
| body | Markdown body | Content pattern or format instructions |

**Resolution order**: `.specify/templates/overrides/` → `.specify/presets/<id>/templates/` → core templates

### pr-template.md

Default template for PR creation by the deliver command.

**Frontmatter fields**:
- `title`: `"feat({{spec_dir}}): {{spec_title}}"` — PR title pattern

**Body**: PR description structure with `{{spec_title}}` and `{{spec_summary}}` placeholders.

**Placeholders**:
- `{{spec_title}}` — extracted from `# Feature Specification: <title>` heading in spec.md
- `{{spec_summary}}` — extracted from the Problem Statement section of spec.md

### commit-template.md

Default template for commit message format by the commit command.

**Frontmatter fields**: none required for default format

**Body**: Format instructions describing the message pattern (one line per file, `<path> - <description>`, no tags/prefixes/trailers).

### Hook Registration

An entry in `extension.yml` under a `hooks.<phase>` key.

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Dot-namespaced command ID (e.g., `speckit.trasgospec.deliver`) |
| `optional` | boolean | `false` = mandatory (auto-execute), `true` = suggestion only |
| `priority` | integer | Execution order (lower = earlier) |
| `description` | string | Human-readable description |

### Bundle Preset

A preset component declared in `bundle.yml` under `provides.presets`.

| Field | Location | Description |
|-------|----------|-------------|
| `id` | `preset.yml` | Preset identifier (e.g., `trasgospec`) |
| `version` | `preset.yml` | Semantic version matching bundle |
| `templates/` | directory | Template files distributed with the preset |

## File Mapping

| Artifact | Bundle Source | Installed Location |
|----------|-------------|-------------------|
| `pr-template.md` | `bundle/presets/trasgospec/templates/pr-template.md` | `.specify/presets/trasgospec/templates/pr-template.md` |
| `commit-template.md` | `bundle/presets/trasgospec/templates/commit-template.md` | `.specify/presets/trasgospec/templates/commit-template.md` |
| `preset.yml` | `bundle/presets/trasgospec/preset.yml` | `.specify/presets/trasgospec/preset.yml` |
| deliver command | `bundle/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` | `.specify/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` |
| deliver script | `bundle/extensions/trasgospec/scripts/bash/deliver.sh` | `.specify/extensions/trasgospec/scripts/bash/deliver.sh` |
