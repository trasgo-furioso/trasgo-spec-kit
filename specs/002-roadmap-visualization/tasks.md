# Tasks: Roadmap Visualization

**Input**: Design documents from `specs/002-roadmap-visualization/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/scan-specs-output.md

**Organization**: Tasks are grouped by user story. TDD approach: tests are written FIRST and must FAIL before implementation. All testing via pytest — never run bash commands manually.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure, test infrastructure, and script scaffold

- [x] T001 Create bundle extension directories: `bundle/commands/`, `bundle/scripts/bash/`, `bundle/skills/trasgospec-roadmap/`
- [x] T002 [P] Create test directory `tests/unit/` with `__init__.py`
- [x] T003 [P] Create `scan-specs.sh` scaffold with shebang, `set -euo pipefail`, repo root resolution via `find_specify_root` walk-up, and `common.sh` sourcing with inline `json_escape` fallback in `bundle/scripts/bash/scan-specs.sh` — make executable (`chmod +x`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Write unit tests for the script's JSON contract, then implement the script to make them pass

**CRITICAL**: Tests written FIRST, must FAIL, then implement until green

### Unit Tests (write first, must FAIL)

- [x] T004 [P] Write `TestSpecsDirectoryDiscovery` in `tests/unit/test_scan_specs.py`: test that script outputs valid JSON with `specs_dir` field when run against a `tmp_path` project with a `specs/` directory; test empty JSON `specs` array when `specs/` is missing or empty
- [x] T005 [P] Write `TestSpecDirectoryIteration` in `tests/unit/test_scan_specs.py`: test that script discovers only subdirectories containing `spec.md`, skips directories without it, and sorts by directory name ascending
- [x] T006 [P] Write `TestMetadataExtraction` in `tests/unit/test_scan_specs.py`: test extraction of `id`, `title`, `status`, `created` from a well-formed `spec.md`; test fallback values when fields are missing; test empty `spec.md` produces all fallbacks
- [x] T007 [P] Write `TestJsonOutputContract` in `tests/unit/test_scan_specs.py`: test that output is valid single-line JSON matching the contract schema in `contracts/scan-specs-output.md`; test `json_escape` handles special characters in titles

**Checkpoint**: Run `pytest tests/unit/test_scan_specs.py -v` — all tests must FAIL (script scaffold has no logic yet)

### Implementation (make tests pass)

- [x] T008 Implement specs directory discovery in `bundle/scripts/bash/scan-specs.sh`: locate `specs/` relative to repo root, emit `specs_dir` field, exit 0 with empty `specs` array if directory is missing or empty — run `pytest tests/unit/test_scan_specs.py::TestSpecsDirectoryDiscovery -v` until green
- [x] T009 Implement spec directory iteration in `bundle/scripts/bash/scan-specs.sh`: list subdirectories of `specs/`, filter to those containing `spec.md`, sort by directory name — run `pytest tests/unit/test_scan_specs.py::TestSpecDirectoryIteration -v` until green
- [x] T010 Implement metadata extraction in `bundle/scripts/bash/scan-specs.sh`: for each valid spec directory, extract `id` (directory name), `title` (from `# Feature Specification:` heading), `status` (from `**Status**:` field), `created` (from `**Created**:` field) with fallbacks per data-model.md — run `pytest tests/unit/test_scan_specs.py::TestMetadataExtraction -v` until green
- [x] T011 Implement JSON output assembly in `bundle/scripts/bash/scan-specs.sh`: build single-line JSON object with `specs_dir` and `specs` array using `json_escape` for all string values — run `pytest tests/unit/test_scan_specs.py::TestJsonOutputContract -v` until green

**Checkpoint**: Run `pytest tests/unit/test_scan_specs.py -v` — ALL tests must PASS

---

## Phase 3: User Story 1 - View Project Roadmap (Priority: P1) MVP

**Goal**: Users can invoke `/speckit-trasgospec-roadmap` and see a markdown table of all specs with ID, Title, Status, and Created columns.

**Independent Test**: Create a project with 2+ specs, run the script, verify JSON contains all specs with correct metadata.

### Integration Tests (write first, must FAIL)

- [x] T012 [P] [US1] Write `TestViewProjectRoadmap` in `tests/integration/test_us1_roadmap.py`: AS-1: Given a `tmp_path` project with 3 spec directories each with `spec.md` (title, status, created), When `scan-specs.sh` is run, Then JSON output contains all 3 specs with correct fields
- [x] T013 [P] [US1] Write `TestRoadmapStatusReflection` in `tests/integration/test_us1_roadmap.py`: AS-2: Given specs with statuses "Draft", "In Progress", "Complete", When script runs, Then each status is accurately reflected in JSON output
- [x] T014 [P] [US1] Write `TestRoadmapOrdering` in `tests/integration/test_us1_roadmap.py`: AS-3: Given specs with sequential numbering (`001-`, `002-`, `003-`), When script runs, Then specs are listed in number order in JSON array

**Checkpoint**: Run `pytest tests/integration/test_us1_roadmap.py -v` — tests should PASS (script already implemented in Phase 2)

### Implementation for User Story 1

- [x] T015 [US1] Create command file `bundle/commands/speckit.trasgospec.roadmap.md` with YAML frontmatter: `description`, `scripts.sh` pointing to `bundle/scripts/bash/scan-specs.sh`
- [x] T016 [US1] Write AI agent instructions in `bundle/commands/speckit.trasgospec.roadmap.md`: run the script via `{SCRIPT}`, parse JSON output, render markdown table with columns ID, Title, Status, Created, ordered by spec number
- [x] T017 [US1] Create skill trigger `bundle/skills/trasgospec-roadmap/SKILL.md` that delegates to the command `/speckit-trasgospec-roadmap`
- [x] T018 [US1] Update `bundle/bundle.yml`: add `trasgospec-roadmap` skill (version `0.2.0`) to `provides.skills` list and bump bundle version from `0.1.0` to `0.2.0`

**Checkpoint**: User Story 1 is functional. `pytest tests/ -v` — all tests pass.

---

## Phase 4: User Story 2 - Empty or Single-Spec Projects (Priority: P2)

**Goal**: The script and command provide clear feedback for zero or one spec.

**Independent Test**: Run script in a project with no specs, empty specs, and exactly one spec.

### Tests (write first)

- [x] T019 [P] [US2] Write `TestEmptySpecsDirectory` in `tests/integration/test_us2_roadmap.py`: AS-1: Given a `tmp_path` project with no `specs/` directory, When `scan-specs.sh` runs, Then JSON output has empty `specs` array
- [x] T020 [P] [US2] Write `TestEmptySpecsDirExists` in `tests/integration/test_us2_roadmap.py`: AS-1 variant: Given a `tmp_path` project with empty `specs/` directory, When script runs, Then JSON output has empty `specs` array
- [x] T021 [P] [US2] Write `TestSingleSpec` in `tests/integration/test_us2_roadmap.py`: AS-2: Given a project with exactly one spec, When script runs, Then JSON contains exactly one entry

**Checkpoint**: Run `pytest tests/integration/test_us2_roadmap.py -v` — tests should PASS (script handles these cases from Phase 2)

### Implementation for User Story 2

- [x] T022 [US2] Add empty-state handling to command instructions in `bundle/commands/speckit.trasgospec.roadmap.md`: when `specs` array is empty, display a clear message indicating no features have been specified yet

**Checkpoint**: `pytest tests/ -v` — all tests pass.

---

## Phase 5: User Story 3 - Graceful Handling of Incomplete Specs (Priority: P3)

**Goal**: Specs with missing metadata appear with fallback values; invalid directories are skipped.

**Independent Test**: Create spec directories with missing metadata, verify fallbacks in JSON.

### Tests (write first)

- [x] T023 [P] [US3] Write `TestMissingStatusField` in `tests/integration/test_us3_roadmap.py`: AS-1: Given a spec missing the `**Status**:` field, When script runs, Then JSON entry has `status: "Unknown"`
- [x] T024 [P] [US3] Write `TestDirectoryWithoutSpecFile` in `tests/integration/test_us3_roadmap.py`: AS-2: Given a directory in `specs/` with no `spec.md`, When script runs, Then that directory is skipped in JSON output
- [x] T025 [P] [US3] Write `TestEmptySpecFile` in `tests/integration/test_us3_roadmap.py`: Edge case: Given a `spec.md` that is completely empty, When script runs, Then JSON entry uses directory name as title and "Unknown" for status and created
- [x] T026 [P] [US3] Write `TestNonSpecSubdirectories` in `tests/integration/test_us3_roadmap.py`: Edge case: Given non-spec directories (e.g., `.git`, `__pycache__`) in `specs/`, When script runs, Then they are ignored

**Checkpoint**: Run `pytest tests/integration/test_us3_roadmap.py -v` — tests should PASS (fallback logic implemented in Phase 2)

### Implementation for User Story 3

- [x] T027 [US3] Verify and adjust fallback-aware presentation in command instructions in `bundle/commands/speckit.trasgospec.roadmap.md`: ensure "Unknown" values render cleanly in the markdown table

**Checkpoint**: `pytest tests/ -v` — all tests pass.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize bundle and validate end-to-end

- [x] T028 [P] Write `TestTimestampNaming` in `tests/unit/test_scan_specs.py`: verify script works with timestamp-based directory naming (`20260808-143022-feature-name`)
- [x] T029 [P] Update `catalog.json` at repo root: bump version to `0.2.0`, update description to mention roadmap command
- [x] T030 Run `pytest tests/ -v` — all unit and integration tests must pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T003 (script scaffold) — tests first, then implementation
- **User Story 1 (Phase 3)**: Depends on Phase 2 (script must pass unit tests)
- **User Story 2 (Phase 4)**: Depends on Phase 2 (script handles empty cases)
- **User Story 3 (Phase 5)**: Depends on Phase 2 (script handles fallbacks)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2
- **User Story 2 (P2)**: Can start after Phase 2 (independent of US1 for script tests; command work depends on US1)
- **User Story 3 (P3)**: Can start after Phase 2 (independent of US1 for script tests)

### TDD Flow Within Each Phase

1. Write test(s) — must FAIL
2. Implement code — run tests until green
3. Refactor if needed — tests stay green
4. Commit

### Parallel Opportunities

- T002 and T003 can run in parallel (different directories)
- T004-T007 can all run in parallel (different test classes, same file)
- T012-T014 can run in parallel (different test classes)
- T019-T021 can run in parallel
- T023-T026 can run in parallel
- US2/US3 integration tests can run in parallel with US1 command work

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Unit tests FAIL → implement → tests PASS (T004-T011)
3. Complete Phase 3: Integration tests + command/skill/manifest (T012-T018)
4. **STOP and VALIDATE**: `pytest tests/ -v` — all green

### Incremental Delivery

1. Setup + Foundational (TDD) → script works, unit tests green
2. User Story 1 → integration tests + command + skill → MVP
3. User Story 2 → empty/single tests + command update
4. User Story 3 → fallback tests + command verification
5. Polish → timestamp test, catalog update, full test suite green

---

## Notes

- TDD: tests are written FIRST and must FAIL before implementation
- All testing via `pytest` — never run bash commands manually to try things
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Unit tests use `subprocess.run` with `tmp_path` to test `scan-specs.sh` directly
- Integration tests follow existing `conftest.py` patterns (`run_specify`, fixtures)
- Script must follow constitution v1.2.0 Extension Development Pattern
- Commit after each phase or logical group
