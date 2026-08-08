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

## R6: Git Pre-Push Hook Mechanics

**Decision**: Use git's pre-push hook with stdin parsing for ref detection.

**Rationale**: The pre-push hook receives the remote name and URL as arguments, and ref information via stdin in the format `<local ref> <local sha> <remote ref> <remote sha>`. This allows detecting which branch is being pushed and which commits are new, enabling targeted bundle change detection via `git diff --name-only <remote-sha>..<local-sha> -- bundle/`.

**Alternatives considered**:
- Pre-commit hook: Too frequent, runs on every commit during iterative development
- CI pipeline: Requires environment setup, not leveraging local tooling
- Post-commit hook: Cannot block the push on validation failure

## R7: Hook Distribution via core.hooksPath

**Decision**: Store hooks in `.githooks/` directory tracked by git, activate via `git config core.hooksPath .githooks`.

**Rationale**: `core.hooksPath` is supported in git 2.9+ (2016), widely available. It allows the hook to be version-controlled and shared. A setup script sets this config once per clone.

**Alternatives considered**:
- Symlink from `.git/hooks/`: Requires per-hook symlinking, fragile
- Copy scripts into `.git/hooks/`: Copies drift from source, not auto-updated
- Tool-managed (husky, pre-commit): Adds external dependency, overkill for a single hook

## R8: Bundle Change Detection

**Decision**: Use `git diff --name-only` between the remote SHA and local SHA to check for files under `bundle/`.

**Rationale**: The pre-push hook receives the remote and local SHAs via stdin. Comparing them with `git diff --name-only` is efficient and only detects changes in the commits being pushed, not the entire history. Filtering with `-- bundle/` limits the check to the relevant directory.

**Alternatives considered**:
- Checking staged files: Not applicable in pre-push context (commits are already made)
- Using `git log --name-only`: More complex parsing, same result

## R9: YAML Parsing in Bash

**Decision**: Use simple grep/sed patterns to extract fields from `bundle/bundle.yml`.

**Rationale**: The bundle manifest has a flat, predictable structure. Fields like `version`, `id`, `name`, `description`, and `role` are top-level with simple key-value syntax. Complex YAML parsing is unnecessary.

**Alternatives considered**:
- Requiring yq: Adds external dependency
- Python helper: Available but overkill for flat YAML
- Sourcing a separate parser: Over-engineering for known structure

## R10: catalog.json Update Strategy

**Decision**: Use sed for in-place JSON field updates in `catalog.json`.

**Rationale**: The catalog JSON structure is well-known, flat, and stable (`schema_version: 1.0`). The fields to update are `version`, `description`, and `download_url` — all simple string replacements within a known structure.

**Alternatives considered**:
- jq: Most robust, but adds external dependency not present in project
- Python one-liner: Available via venv but adds complexity to a bash script
- Full JSON rewrite: Brittle if structure changes

## R11: .gitignore Conflict with *.zip

**Decision**: Add a negation pattern to `.gitignore` for the bundle zip artifact.

**Rationale**: The `.gitignore` currently contains `*.zip` which would prevent the bundle artifact from being committed. Adding `!trasgospec-*.zip` allows the bundle artifact through while keeping other zip files ignored.

**Alternatives considered**:
- Using `git add -f`: Works but requires remembering the force flag; fragile in automated scripts
- Removing `*.zip` entirely: Would allow all zip files, losing protection
- Moving the artifact to a non-ignored directory: Conflicts with `specify bundle build --output .`

## R12: GitHub Raw URL Inference from SSH Remote

**Decision**: Parse the git remote URL (SSH or HTTPS) to extract owner/repo for constructing the raw.githubusercontent.com download URL.

**Rationale**: The remote URL can be parsed with sed to extract owner and repo, then construct `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<filename>`.

**Parsing patterns**:
- SSH: `git@github.com:<owner>/<repo>.git` → extract via sed
- HTTPS: `https://github.com/<owner>/<repo>.git` → same sed pattern works

## R13: Auto-Commit Strategy in Pre-Push Hook

**Decision**: After building artifacts, create a new commit with `git add` + `git commit` before allowing the push to proceed.

**Rationale**: The pre-push hook runs after commits are made but before they are sent. Creating a new commit at this point adds it to the push. The hook must handle the case where the working tree has unstaged changes by stashing them, creating the build commit, then restoring.

**Key steps**:
1. Stash any uncommitted changes (if present)
2. Run validate + build
3. Update catalog.json
4. `git add <zip-file> catalog.json`
5. `git commit -m "chore: build bundle vX.Y.Z"`
6. Restore stash (if applied)
7. Exit 0 to allow push (which now includes the new commit)

**Alternatives considered**:
- Amending the last commit: Changes commit hash, confusing if already referenced
- Blocking push and asking developer to commit manually: Adds friction, defeats automation purpose

## R14: Testing Strategy for Pre-Push Hook

**Decision**: Test the hook logic as a standalone bash script via pytest + subprocess, following the existing test pattern.

**Rationale**: The project already tests bash scripts via `subprocess.run()` in pytest, creating isolated temporary project directories. The pre-push hook can be tested the same way — create a temp git repo, make bundle changes, invoke the hook script, and verify the output.

**Key test considerations**:
- Need a temp git repo with a remote (can use `git init --bare` for a local remote)
- Need `specify` CLI available in test environment
- Test both the hook script directly and the setup script
