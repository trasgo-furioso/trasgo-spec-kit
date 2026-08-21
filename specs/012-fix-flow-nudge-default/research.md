# Research: Fix Flow-Nudge Default Execution

**Date**: 2026-08-10

## R1: Bundle Preset Structure for Template Distribution

**Decision**: Add a `presets/trasgospec/` directory to the bundle with a `preset.yml` manifest and `templates/` directory containing `pr-template.md` and `commit-template.md`.

**Rationale**: Spec Kit presets are the canonical mechanism for distributing templates. The bundle declares the preset in `bundle.yml` under `provides.presets`, and `specify bundle install` places it at `.specify/presets/trasgospec/templates/`. The `specify preset resolve <name>` command then finds templates via the resolution stack: project overrides → installed presets → core templates.

**Alternatives considered**:
- Placing templates directly in the extension directory — rejected because extensions don't participate in the template resolution stack.
- Creating a separate bundle for templates — rejected because it adds unnecessary distribution complexity for two files.

## R2: Rename Strategy (flow-nudge → deliver)

**Decision**: Rename all artifacts atomically — command file, script file, extension.yml registrations, aliases, and SKILL.md references. The existing `flow-nudge.sh` script is reused as `deliver.sh` (identical logic, just renamed). The command file (`speckit.trasgospec.deliver.md`) is rewritten to remove confirmation prompts and add template resolution.

**Rationale**: A partial rename creates inconsistency. Since this is a bundle (not a library with dependents), all consumers install the new version atomically.

**Alternatives considered**:
- Keeping a deprecated alias `flow-nudge` → rejected. No external dependents exist; clean break is simpler.
- Renaming only the user-facing name — rejected. Internal consistency matters for maintainability.

## R3: Template Placeholder Interpolation

**Decision**: The command file (AI agent) performs placeholder interpolation, not the bash script. The script gathers state as JSON; the command reads the template, replaces `{{spec_title}}` and `{{spec_summary}}` with values extracted from `spec.md`, then passes the result to `gh pr create`.

**Rationale**: Template interpolation requires reading markdown files, parsing frontmatter, and making contextual decisions — all of which the AI agent excels at. The bash script stays deterministic and simple (per Constitution Principle I).

**Alternatives considered**:
- Bash-side interpolation with `sed` — rejected. Fragile, hard to maintain, and violates the two-part pattern where scripts do deterministic JSON only.

## R4: Commit Template Format

**Decision**: The `commit-template.md` is a markdown file with YAML frontmatter containing format instructions. The body describes the message pattern. The AI agent reads this template and applies it when composing commit messages.

**Rationale**: Commit messages are composed by the AI agent (inspecting diffs, generating descriptions). The template defines the FORMAT, not the content. This matches how `pr-template.md` works — frontmatter for metadata, body for structure.

**Alternatives considered**:
- A plain-text template with literal placeholders — rejected. The commit message structure is more nuanced (variable number of files, AI-generated descriptions) and benefits from descriptive instructions rather than rigid substitution.
