# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Trasgo Spec Kit is a [GitHub Spec Kit](https://github.com/github/spec-kit) bundle (`trasgospec`) that provides CLI extensions for spec-driven development. The project dogfoods its own Spec Kit workflow — features are developed using the specify → plan → tasks → implement cycle.

## Commands

```bash
# Setup (after cloning — configures git hooks)
./scripts/setup.sh

# Run tests (always use .venv/bin/pytest, never bare pytest)
.venv/bin/pytest tests/unit/ -v          # unit tests
.venv/bin/pytest tests/integration/ -v   # integration tests (uses HTTP server on port 8888)
.venv/bin/pytest tests/unit/test_scan_specs.py -v                    # single file
.venv/bin/pytest tests/unit/test_scan_specs.py::TestMetadataExtraction -v  # single class
.venv/bin/pytest tests/unit/test_scan_specs.py::TestMetadataExtraction::test_fallback_title_when_heading_missing -v  # single test

# Validate bundle manifest
specify bundle validate --path bundle --offline

# Build bundle (creates ZIP artifacts and updates catalog.json)
specify bundle build --path bundle
```

## Architecture

### Bundle Structure

```
bundle/
  bundle.yml                              # manifest — single source of truth for version, components, metadata
  extensions/trasgospec/
    extension.yml                         # extension manifest — declares commands and aliases
    commands/speckit.trasgospec.*.md       # command files (AI agent instructions + YAML frontmatter)
    scripts/bash/*.sh                     # deterministic scripts (JSON output, no AI logic)
```

### Extension Two-Part Pattern

Every extension command has two parts per the project constitution:

1. **Command file** (`commands/<dot.namespaced.id>.md`) — YAML frontmatter (`description`, `scripts`) + markdown body with AI agent instructions. The command invokes the script, parses JSON, and renders output. It must NOT do deterministic work itself.

2. **Script file** (`scripts/bash/<name>.sh`) — deterministic only, no AI calls. Emits single-line JSON on stdout, diagnostics on stderr. Must target bash 3.2+ (no `mapfile`, no `readarray`). Must use `set -euo pipefail`. Must locate repo root via `_find_specify_root` walk-up, not assume CWD. Must source `common.sh` opportunistically with inline `json_escape` fallback.

### Naming Convention

Command IDs use dot namespacing: `speckit.trasgospec.<name>` (e.g., `speckit.trasgospec.roadmap`). Dots map to hyphens at invocation: `/speckit-trasgospec-roadmap`. Aliases without the `speckit.` prefix are also registered (e.g., `trasgospec.roadmap`).

### Distribution

The pre-push git hook (`.githooks/pre-push`) automates bundle builds. When pushing changes to `bundle/` on main, it validates, builds ZIPs, updates `catalog.json`, and creates a build commit. This requires two pushes: the first creates the build commit, the second pushes it through.

### Specs Directory

Feature specifications live in `specs/<NNN-slug>/` (sequential numbering) or `specs/<YYYYMMDD-HHMMSS-slug>/` (timestamp-based). Each contains `spec.md` and may include `plan.md`, `tasks.md`, and supporting artifacts. The `scan-specs.sh` script extracts metadata from `spec.md` files by pattern-matching `# Feature Specification:`, `**Status**:`, and `**Created**:` headings.

## Project Constitution

Read `.specify/memory/constitution.md` for the full set of non-negotiable principles and governance rules. The constitution is the authoritative source — always consult it directly.

## Spec Kit Workflow

The `.claude/skills/` directory contains the full Spec Kit pipeline. For feature development on this bundle, use these skills in order:

1. `/speckit-specify` — create feature spec from natural language description
2. `/speckit-clarify` — identify and resolve underspecified areas (max 5 questions)
3. `/speckit-checklist` — generate quality checklist ("unit tests for English")
4. `/speckit-plan` — generate implementation plan (research.md, data-model.md, contracts/)
5. `/speckit-tasks` — generate dependency-ordered tasks.md grouped by user story
6. `/speckit-implement` — execute tasks from tasks.md with TDD cycle
7. `/speckit-converge` — assess codebase against spec/plan/tasks, append remaining work
8. `/speckit-analyze` — cross-artifact consistency and quality analysis

Additional skills: `/speckit-constitution` (manage constitution), `/speckit-taskstoissues` (export to GitHub issues).

Bundle-specific commands: `/speckit-trasgospec-hello` (verify installation), `/speckit-trasgospec-roadmap` (view roadmap table).

## Testing Conventions

- Tests live in `tests/unit/` and `tests/integration/`, organized by user story
- Integration tests use a session-scoped HTTP server fixture (port 8888) serving catalog files
- Test helpers: `run_scan_specs()` runs the bash script against a `tmp_path` project, `create_spec()` builds spec fixtures, `make_specify_project()` creates a minimal `.specify` directory
- Every implementation task must begin with a failing test before writing production code
