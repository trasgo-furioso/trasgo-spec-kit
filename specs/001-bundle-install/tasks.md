# Tasks: Bundle Install

**Input**: Design documents from `specs/001-bundle-install/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Integration tests are REQUIRED (TDD). Acceptance scenarios from user stories translate to pytest tests using Given (Arrange) / When (Act) / Then (Assert). Tests MUST be written and fail BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — Python dev environment, directory structure, gitignore

- [x] T001 Create Python virtual environment in .venv/, create .python-version with `3.11`, and configure direnv auto-activation in .envrc
- [x] T002 Create requirements-dev.txt with pytest dependency
- [x] T003 Install dev dependencies into .venv via pip install -r requirements-dev.txt
- [x] T004 [P] Update .gitignore with .venv/, __pycache__/, *.pyc, dist/, *.zip entries
- [x] T005 [P] Create directory structure: skills/trasgospec/, tests/integration/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Test infrastructure and minimal bundle stub that all tests depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create tests/integration/conftest.py with shared pytest fixtures: (1) session-scoped HTTP server fixture using Python `http.server` that serves catalog.json on localhost:8888, with automatic start/stop, (2) `catalog_url` fixture returning `http://localhost:8888/catalog.json`, (3) `clean_project` fixture using tmp_path factory that runs `specify init --integration claude` in a temp directory, (4) `project_with_catalog` fixture that creates a clean project and runs `specify bundle catalog add <catalog_url> --policy install-allowed`, (5) cleanup teardown
- [x] T007 Create minimal bundle.yml stub at project root with metadata (id: trasgospec, name: Trasgo Spec Kit, version: 0.1.0, role: developer, integration: claude, speckit_version requirement) and empty provides section — enough to be parseable but not yet valid
- [x] T008 Create skills/trasgospec/SKILL.md with /trasgospec hello command that outputs a greeting message

**Checkpoint**: Foundation ready — test fixtures exist, bundle files exist as stubs, user story test-and-implement cycles can begin

---

## Phase 3: User Story 1 - Install Trasgo Bundle from Self-Hosted Catalog (Priority: P1) MVP

**Goal**: A user can add the Trasgo catalog source, install the bundle by catalog identifier, and verify it appears in the bundle list

**Independent Test**: Add catalog source via local HTTP server, run `specify bundle install trasgospec`, then verify `specify bundle list` shows trasgospec with version 0.1.0

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Integration test: install via catalog in tests/integration/test_us1_install.py — Given a clean Spec Kit project with Trasgo catalog source added (HTTP server serving catalog.json on localhost:8888), When `specify bundle catalog add http://localhost:8888/catalog.json --policy install-allowed` and then `specify bundle install trasgospec`, Then exit code 0 and all declared components are applied
- [x] T010 [P] [US1] Integration test: bundle list after install in tests/integration/test_us1_install.py — Given a successful catalog-based install, When `specify bundle list`, Then output contains trasgospec with version 0.1.0, component count, and timestamp
- [x] T011 [P] [US1] Integration test: idempotent reinstall in tests/integration/test_us1_install.py — Given trasgospec already installed via catalog, When `specify bundle install trasgospec` again, Then exit code 0, no errors, no duplicate components
- [x] T012 [P] [US1] Integration test: install from local path in tests/integration/test_us1_install.py — Given a clean Spec Kit project, When `specify bundle install <bundle-dir>` (local path), Then exit code 0 and bundle list shows trasgospec v0.1.0
- [x] T013 [US1] Integration test: install initializes uninitialized project in tests/integration/test_us1_install.py — Given a directory that is NOT a Spec Kit project, When `specify bundle install <bundle-dir>`, Then project is initialized and bundle is installed

### Implementation for User Story 1

- [x] T014 [US1] Complete bundle.yml manifest at project root: add provides.skills entry for trasgospec with pinned version 0.1.0, per contracts/bundle-manifest.md
- [x] T015 [US1] Create catalog.json at project root with bundles array containing trasgospec entry (id, name, description, version, role, repository, release_url) per contracts/catalog-file.md — needed for catalog-based install tests
- [x] T016 [US1] Validate bundle manifest by running `specify bundle validate` from project root — must pass with zero errors
- [x] T017 [US1] Build bundle artifact by running `specify bundle build` — must produce trasgospec-0.1.0.zip
- [x] T018 [US1] Run US1 integration tests — all must pass

**Checkpoint**: User Story 1 fully functional — bundle installs via catalog and local path, appears in list, reinstall is idempotent

---

## Phase 4: Edge Cases & Final Validation

**Purpose**: Edge case coverage and final validation

### Edge Case Tests

- [x] T019 [P] Integration test: integration mismatch in tests/integration/test_edge_cases.py — Given a Spec Kit project initialized with a non-claude integration, When `specify bundle install trasgospec`, Then install applies 0 components (CLI does not abort for local path installs)
- [x] T020 [P] Integration test: missing catalog source in tests/integration/test_edge_cases.py — Given a clean Spec Kit project with NO Trasgo catalog source added, When `specify bundle install trasgospec` (by catalog ID), Then install fails with error indicating bundle not found in any active catalog
- [x] T021 [P] Integration test: unreachable catalog in tests/integration/test_edge_cases.py — Given a catalog source pointing to a stopped HTTP server, When `specify bundle install trasgospec`, Then install fails with a clear network error and no partial state is written

### Final Validation

- [x] T022 Run full integration test suite: pytest tests/integration/ -v — all 11 tests pass
- [x] T023 Run quickstart.md validation scenarios — verified via full test suite (catalog install, local path install, idempotency, edge cases)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all tests
- **US1 (Phase 3)**: Depends on Foundational — MVP, complete first
- **Edge Cases & Validation (Phase 4)**: Depends on US1 completion

### Within User Story 1

- Tests MUST be written and FAIL before implementation
- Implementation makes tests pass
- Validate at checkpoint before moving to edge cases

### Parallel Opportunities

- T004 and T005 can run in parallel (different files)
- T009, T010, T011, T012 can run in parallel (same file, different test functions — written together)
- T019, T020, T021 can run in parallel (same file, different test functions)

---

## Parallel Example: User Story 1

```bash
# Write all US1 tests together (different functions in same file):
Task: "Integration test: install via catalog in tests/integration/test_us1_install.py"
Task: "Integration test: bundle list after install in tests/integration/test_us1_install.py"
Task: "Integration test: idempotent reinstall in tests/integration/test_us1_install.py"
Task: "Integration test: install from local path in tests/integration/test_us1_install.py"

# Then implement (sequential — each step depends on previous):
Task: "Complete bundle.yml manifest"
Task: "Create catalog.json"
Task: "Validate bundle manifest"
Task: "Build bundle artifact"
Task: "Run US1 integration tests"
```

---

## Implementation Strategy

### MVP (User Story 1)

1. Complete Phase 1: Setup (venv, deps, dirs)
2. Complete Phase 2: Foundational (conftest with HTTP server fixture, bundle stub, SKILL.md)
3. Complete Phase 3: User Story 1 (tests → implement → validate)
4. **STOP and VALIDATE**: Run US1 tests, verify install via catalog and local path
5. Bundle is installable via self-hosted catalog — MVP achieved
6. Complete Phase 4: Edge cases + final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Python deps (pytest) are dev-only — bundle artifact contains no Python code
- The `specify` CLI handles install/remove/search behavior — our implementation is the correct bundle.yml, catalog.json, and SKILL.md files
- Tests shell out to `specify` CLI via subprocess and verify exit codes + stdout
- **Catalog testing strategy**: During dev time, the self-hosted catalog is a local file served by a tiny Python HTTP server at `http://localhost:8888/{filename}.json`. The conftest.py session-scoped fixture starts this server before tests and stops it after. All tests that need catalog access use this fixture rather than hitting GitHub.
- Commit after each task or logical group
