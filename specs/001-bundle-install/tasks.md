# Tasks: Bundle Install

**Input**: Design documents from `specs/001-bundle-install/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Integration tests are REQUIRED (TDD). Acceptance scenarios from user stories translate to pytest tests using Given (Arrange) / When (Act) / Then (Assert). Tests MUST be written and fail BEFORE implementation.

**Organization**: Tasks are grouped by feature area to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Part A: Bundle Install & Distribution

### Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — Python dev environment, directory structure, gitignore

- [x] T001 Create Python virtual environment in .venv/, create .python-version with `3.11`, and configure direnv auto-activation in .envrc
- [x] T002 Create requirements-dev.txt with pytest dependency
- [x] T003 Install dev dependencies into .venv via pip install -r requirements-dev.txt
- [x] T004 [P] Update .gitignore with .venv/, __pycache__/, *.pyc, dist/, *.zip entries
- [x] T005 [P] Create directory structure: skills/trasgospec/, tests/integration/

---

### Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Test infrastructure and minimal bundle stub that all tests depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create tests/integration/conftest.py with shared pytest fixtures: (1) session-scoped HTTP server fixture using Python `http.server` that serves catalog.json on localhost:8888, with automatic start/stop, (2) `catalog_url` fixture returning `http://localhost:8888/catalog.json`, (3) `clean_project` fixture using tmp_path factory that runs `specify init --integration claude` in a temp directory, (4) `project_with_catalog` fixture that creates a clean project and runs `specify bundle catalog add <catalog_url> --policy install-allowed`, (5) cleanup teardown
- [x] T007 Create minimal bundle.yml stub at project root with metadata (id: trasgospec, name: Trasgo Spec Kit, version: 0.1.0, role: developer, integration: claude, speckit_version requirement) and empty provides section — enough to be parseable but not yet valid
- [x] T008 Create skills/trasgospec/SKILL.md with /trasgospec hello command that outputs a greeting message

**Checkpoint**: Foundation ready — test fixtures exist, bundle files exist as stubs, user story test-and-implement cycles can begin

---

### Phase 3: User Story 1 - Install Trasgo Bundle from Self-Hosted Catalog (Priority: P1) MVP

**Goal**: A user can add the Trasgo catalog source, install the bundle by catalog identifier, and verify it appears in the bundle list

**Independent Test**: Add catalog source via local HTTP server, run `specify bundle install trasgospec`, then verify `specify bundle list` shows trasgospec with version 0.1.0

#### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Integration test: install via catalog in tests/integration/test_us1_install.py — Given a clean Spec Kit project with Trasgo catalog source added (HTTP server serving catalog.json on localhost:8888), When `specify bundle catalog add http://localhost:8888/catalog.json --policy install-allowed` and then `specify bundle install trasgospec`, Then exit code 0 and all declared components are applied
- [x] T010 [P] [US1] Integration test: bundle list after install in tests/integration/test_us1_install.py — Given a successful catalog-based install, When `specify bundle list`, Then output contains trasgospec with version 0.1.0, component count, and timestamp
- [x] T011 [P] [US1] Integration test: idempotent reinstall in tests/integration/test_us1_install.py — Given trasgospec already installed via catalog, When `specify bundle install trasgospec` again, Then exit code 0, no errors, no duplicate components
- [x] T012 [P] [US1] Integration test: install from local path in tests/integration/test_us1_install.py — Given a clean Spec Kit project, When `specify bundle install <bundle-dir>` (local path), Then exit code 0 and bundle list shows trasgospec v0.1.0
- [x] T013 [US1] Integration test: install initializes uninitialized project in tests/integration/test_us1_install.py — Given a directory that is NOT a Spec Kit project, When `specify bundle install <bundle-dir>`, Then project is initialized and bundle is installed

#### Implementation for User Story 1

- [x] T014 [US1] Complete bundle.yml manifest at project root: add provides.skills entry for trasgospec with pinned version 0.1.0, per contracts/bundle-manifest.md
- [x] T015 [US1] Create catalog.json at project root with bundles array containing trasgospec entry (id, name, description, version, role, repository, release_url) per contracts/catalog-file.md — needed for catalog-based install tests
- [x] T016 [US1] Validate bundle manifest by running `specify bundle validate` from project root — must pass with zero errors
- [x] T017 [US1] Build bundle artifact by running `specify bundle build` — must produce trasgospec-0.1.0.zip
- [x] T018 [US1] Run US1 integration tests — all must pass

**Checkpoint**: User Story 1 fully functional — bundle installs via catalog and local path, appears in list, reinstall is idempotent

---

### Phase 4: Edge Cases & Final Validation

**Purpose**: Edge case coverage and final validation

#### Edge Case Tests

- [x] T019 [P] Integration test: integration mismatch in tests/integration/test_edge_cases.py — Given a Spec Kit project initialized with a non-claude integration, When `specify bundle install trasgospec`, Then install applies 0 components (CLI does not abort for local path installs)
- [x] T020 [P] Integration test: missing catalog source in tests/integration/test_edge_cases.py — Given a clean Spec Kit project with NO Trasgo catalog source added, When `specify bundle install trasgospec` (by catalog ID), Then install fails with error indicating bundle not found in any active catalog
- [x] T021 [P] Integration test: unreachable catalog in tests/integration/test_edge_cases.py — Given a catalog source pointing to a stopped HTTP server, When `specify bundle install trasgospec`, Then install fails with a clear network error and no partial state is written

#### Final Validation

- [x] T022 Run full integration test suite: pytest tests/integration/ -v — all 11 tests pass
- [x] T023 Run quickstart.md validation scenarios — verified via full test suite (catalog install, local path install, idempotency, edge cases)

---

## Part B: Build Automation (Pre-Push Hook)

### Phase 5: Build CI Setup

**Purpose**: Create directory structure and configuration for git hooks

- [x] T024 Create `.githooks/` and `scripts/` directories at repository root
- [x] T025 Add `.gitignore` negation pattern `!trasgospec-*.zip` to allow bundle zip artifact while keeping general `*.zip` ignore

---

### Phase 6: Hook Foundational (Blocking Prerequisites)

**Purpose**: Pre-push hook skeleton that all build automation tests depend on

- [x] T026 Create pre-push hook skeleton in `.githooks/pre-push` with shebang (`#!/usr/bin/env bash`), `set -euo pipefail`, `[bundle-build]` log prefix function, repo root discovery via `.specify` marker walk-up, and json_escape helper

**Checkpoint**: Hook skeleton exists and is executable — user story implementation can begin

---

### Phase 7: User Story 2 - Automated Bundle Build on Push (Priority: P1) MVP

**Goal**: When a developer pushes commits with `bundle/` changes to main, the hook validates, builds, updates catalog.json, and auto-commits artifacts before the push proceeds.

#### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T027 [P] [US2] Write failing tests for bundle change detection (detects bundle/ changes, ignores non-bundle changes) and validate+build execution (runs `specify bundle validate` then `specify bundle build`, blocks on failure) in `tests/unit/test_pre_push_hook.py`
- [x] T028 [P] [US2] Write failing tests for catalog.json update (syncs version/description/download_url from bundle.yml, constructs raw.githubusercontent.com URL from git remote) and auto-commit creation (new commit with zip + catalog.json, original commits untouched) in `tests/unit/test_pre_push_hook.py`

#### Implementation for User Story 2

- [x] T029 [US2] Implement stdin ref parsing, main branch detection, and bundle change detection via `git diff --name-only <remote-sha>..<local-sha> -- bundle/` in `.githooks/pre-push`
- [x] T030 [US2] Implement `specify` CLI availability check, `specify bundle validate --path bundle`, and `specify bundle build --path bundle --output .` execution with exit code handling per `contracts/hook-exit-codes.md` in `.githooks/pre-push`
- [x] T031 [US2] Implement git remote URL parsing (SSH and HTTPS formats) and catalog.json update (sync id, name, version, description, role, download_url from bundle.yml) per `contracts/catalog-update.md` in `.githooks/pre-push`
- [x] T032 [US2] Implement working tree stash, `git add` of zip artifact and catalog.json, `git commit -m "chore: build bundle vX.Y.Z"`, and stash restore flow in `.githooks/pre-push`

**Checkpoint**: Pre-push hook validates, builds, updates catalog, and auto-commits on bundle changes. US2 is fully functional.

---

### Phase 8: User Story 3 - No Build for Non-Bundle Changes (Priority: P2)

**Goal**: Pushes that don't touch `bundle/` skip all build steps silently.

#### Tests for User Story 3

- [x] T033 [US3] Write failing test verifying hook exits silently (exit 0, no stderr output, no auto-commit) when pushed commits contain no `bundle/` file changes in `tests/unit/test_pre_push_hook.py`

**Checkpoint**: Non-bundle pushes pass through silently with no side effects.

---

### Phase 9: User Story 4 - Developer Hook Setup (Priority: P2)

**Goal**: A single script invocation activates the pre-push hook for a developer after cloning.

#### Tests for User Story 4

- [x] T034 [P] [US4] Write failing tests for setup script: configures `core.hooksPath` to `.githooks`, is idempotent (second run succeeds without errors), and exits with error outside a git repository in `tests/unit/test_setup.py`

#### Implementation for User Story 4

- [x] T035 [US4] Implement setup script in `scripts/setup.sh` that runs `git config core.hooksPath .githooks`, verifies `.githooks/` directory exists, and outputs confirmation message

**Checkpoint**: Developer can activate hooks with a single command. Setup is idempotent.

---

### Phase 10: User Story 5 - Catalog Version Consistency (Priority: P3)

**Goal**: After every build, catalog.json version and description match bundle.yml exactly.

#### Tests for User Story 5

- [x] T036 [US5] Write failing tests verifying catalog.json `version` and `description` fields match the corresponding values from `bundle/bundle.yml` after a successful hook execution in `tests/unit/test_pre_push_hook.py`

**Checkpoint**: Catalog always reflects the manifest's version and description after a build.

---

### Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, robustness, and end-to-end validation

- [x] T037 [P] Add edge case handling in `.githooks/pre-push`: create catalog.json from scratch if missing, handle bundle.yml parse errors with clear error messages (exit 4)
- [x] T038 Run end-to-end validation scenarios from `quickstart.md` to verify all user stories work together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Part A — Setup (Phase 1)**: No dependencies — can start immediately
- **Part A — Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all tests
- **Part A — US1 (Phase 3)**: Depends on Foundational — MVP, complete first
- **Part A — Edge Cases (Phase 4)**: Depends on US1 completion
- **Part B — Build CI Setup (Phase 5)**: Can start after Part A Phase 1
- **Part B — Hook Foundational (Phase 6)**: Depends on Phase 5
- **Part B — US2 (Phase 7)**: Depends on Phase 6 — core hook logic
- **Part B — US3 (Phase 8)**: Depends on Phase 7 (detection logic in T029)
- **Part B — US4 (Phase 9)**: Depends on Phase 6 only — independent of US2/US3
- **Part B — US5 (Phase 10)**: Depends on Phase 7 (catalog update in T031)
- **Part B — Polish (Phase 11)**: Depends on all user stories being complete

### Parallel Opportunities

- T004 and T005 can run in parallel (different files)
- T009, T010, T011, T012 can run in parallel (same file, different test functions)
- T019, T020, T021 can run in parallel (same file, different test functions)
- T027 and T028 can run in parallel (different test classes)
- T034 can run in parallel with T027/T028 (different test file)
- US4 (Phase 9) can run in parallel with US2 (Phase 7) after foundational phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Python deps (pytest) are dev-only — bundle artifact contains no Python code
- The `specify` CLI handles install/remove/search behavior — our implementation is the correct bundle.yml, catalog.json, and SKILL.md files
- Tests shell out to `specify` CLI via subprocess and verify exit codes + stdout
- All bash scripts target bash 3.2+ (macOS compatibility)
- Hook stderr uses `[bundle-build]` prefix per contracts/hook-exit-codes.md
- Commit after each task or logical group
