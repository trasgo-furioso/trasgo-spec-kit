# Research: Bundle Install

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## R1: Spec Kit bundle.yml Manifest Structure

**Decision**: Use the standard bundle.yml schema with metadata,
requirements, and provides sections.

**Rationale**: The Spec Kit bundle documentation defines a clear
manifest structure. The `provides` section declares components by type
(extensions, presets, workflows, steps) with version pins. Skills are
delivered as part of the integration-specific component set.

**Alternatives considered**:
- Custom manifest format → Rejected: violates Principle II (Spec Kit
  Native).

**Key findings**:
- `id`: unique bundle identifier (e.g., `trasgospec`)
- `name`: human-readable name (e.g., `Trasgo Spec Kit`)
- `version`: semver (e.g., `0.1.0`)
- `role`: target persona (e.g., `developer`)
- `integration`: target integration (`claude`)
- `speckit_version`: minimum SK version constraint
- `provides`: component declarations with pinned versions

## R2: Catalog File Format for Self-Hosting

**Decision**: Use a `catalog.json` file at the repository root,
hosted via raw.githubusercontent.com.

**Rationale**: Spec Kit catalogs are JSON files with a `bundles`
array. Each entry contains the bundle metadata and a `release_url`
pointing to the built `.zip` artifact. The catalog is added by
consumers via `specify bundle catalog add <url> --policy
install-allowed`.

**Alternatives considered**:
- GitHub Pages hosting → Rejected: adds a build/deploy step
  unnecessary for a single catalog file.
- GitHub Releases only (no catalog) → Rejected: consumers would need
  to use local path install, losing catalog discovery benefits.

**Key findings**:
- Catalog JSON structure: `{ "bundles": [{ id, name, description,
  version, role, repository, release_url }] }`
- Catalog source ID is derived from URL (e.g., `raw-githubusercontent-com-...`)
- Trust indicator: `community` (not on official catalog)

## R3: Skill Component Structure for Claude Integration

**Decision**: Place the `/trasgospec` skill under `skills/trasgospec/SKILL.md`
in the bundle source, separate from default SK skills in `.claude/skills/`.

**Rationale**: Default SK skills live at `.claude/skills/speckit-*/` and
are installed by `specify init`. Bundle-provided skills should be in a
separate location to avoid conflating default assets with custom
bundle components. The `provides` section in `bundle.yml` references
the skill by its component ID.

**Alternatives considered**:
- Place under `.claude/skills/trasgospec/` alongside defaults →
  Rejected: blurs the boundary between default and custom components,
  making it unclear what the bundle owns.

## R4: pytest Integration Test Strategy

**Decision**: Map acceptance scenarios from user stories to pytest
functions using Given (Arrange) / When (Act) / Then (Assert) pattern.
Tests shell out to `specify` CLI commands via `subprocess.run`.

**Rationale**: The user requires TDD with tests written before
implementation. pytest is the standard Python testing framework.
Integration tests verify end-to-end bundle operations against the
real `specify` CLI, ensuring the bundle works as documented.

**Alternatives considered**:
- Shell script tests (bats, shunit2) → Rejected: user specified
  pytest explicitly.
- Unit tests mocking CLI → Rejected: would not verify real bundle
  install behavior.

**Key findings**:
- Each test file corresponds to a user story (US1, US2, US3)
- `conftest.py` provides fixtures: temp directory, `specify init`,
  catalog source setup, cleanup
- Tests assert on CLI exit codes and stdout/stderr content
- Python deps are dev-only: `requirements-dev.txt` with pytest

## R5: Virtual Environment Auto-Activation

**Decision**: Use direnv with `.envrc` to auto-activate `.venv` on cd.

**Rationale**: direnv is the standard tool for per-directory
environment activation. It hooks into the shell (zsh/bash) and
automatically sources `.envrc` when entering the directory. This
provides seamless venv activation without manual steps.

**Alternatives considered**:
- pyenv virtualenv with `.python-version` → Works for version but
  doesn't auto-activate venvs by default without plugins.
- Manual activation → Rejected: user explicitly requested auto-activation.

**Key findings**:
- `.envrc` content: `layout python` or `source .venv/bin/activate`
- Requires `direnv` installed and hooked into shell (`eval "$(direnv hook zsh)"`)
- `.venv/` added to `.gitignore`
