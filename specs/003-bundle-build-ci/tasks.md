# Tasks: Bundle Build CI

**Input**: Design documents from `/specs/003-bundle-build-ci/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required by Constitution Principle VI (Test-Driven Development). Tests MUST be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and configuration for git hooks

- [x] T001 Create `.githooks/` and `scripts/` directories at repository root
- [x] T002 Add `.gitignore` negation pattern `!trasgospec-*.zip` to allow bundle zip artifact while keeping general `*.zip` ignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pre-push hook skeleton that all user stories build upon

- [x] T003 Create pre-push hook skeleton in `.githooks/pre-push` with shebang (`#!/usr/bin/env bash`), `set -euo pipefail`, `[bundle-build]` log prefix function, repo root discovery via `.specify` marker walk-up, and json_escape helper following the pattern in `bundle/scripts/bash/scan-specs.sh`

**Checkpoint**: Hook skeleton exists and is executable — user story implementation can begin

---

## Phase 3: User Story 1 - Automated Bundle Build on Push (Priority: P1) MVP

**Goal**: When a developer pushes commits with `bundle/` changes to main, the hook validates, builds, updates catalog.json, and auto-commits artifacts before the push proceeds.

**Independent Test**: Push a change to any file in `bundle/`, verify zip produced, catalog.json updated with raw.githubusercontent.com URL, and a separate build commit created.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Write failing tests for bundle change detection (detects bundle/ changes, ignores non-bundle changes) and validate+build execution (runs `specify bundle validate` then `specify bundle build`, blocks on failure) in `tests/unit/test_pre_push_hook.py`
- [x] T005 [P] [US1] Write failing tests for catalog.json update (syncs version/description/download_url from bundle.yml, constructs raw.githubusercontent.com URL from git remote) and auto-commit creation (new commit with zip + catalog.json, original commits untouched) in `tests/unit/test_pre_push_hook.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement stdin ref parsing, main branch detection, and bundle change detection via `git diff --name-only <remote-sha>..<local-sha> -- bundle/` in `.githooks/pre-push`
- [x] T007 [US1] Implement `specify` CLI availability check, `specify bundle validate --path bundle`, and `specify bundle build --path bundle --output .` execution with exit code handling per `contracts/hook-exit-codes.md` in `.githooks/pre-push`
- [x] T008 [US1] Implement git remote URL parsing (SSH and HTTPS formats) and catalog.json update (sync id, name, version, description, role, download_url from bundle.yml) per `contracts/catalog-update.md` in `.githooks/pre-push`
- [x] T009 [US1] Implement working tree stash, `git add` of zip artifact and catalog.json, `git commit -m "chore: build bundle vX.Y.Z"`, and stash restore flow in `.githooks/pre-push`

**Checkpoint**: Pre-push hook validates, builds, updates catalog, and auto-commits on bundle changes. US1 is fully functional.

---

## Phase 4: User Story 2 - No Build for Non-Bundle Changes (Priority: P2)

**Goal**: Pushes that don't touch `bundle/` skip all build steps silently.

**Independent Test**: Push a commit modifying only files outside `bundle/`, verify no validation/build/commit occurs.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [US2] Write failing test verifying hook exits silently (exit 0, no stderr output, no auto-commit) when pushed commits contain no `bundle/` file changes in `tests/unit/test_pre_push_hook.py`

### Implementation for User Story 2

Implementation is covered by the change detection logic in T006. This phase validates the skip path independently.

**Checkpoint**: Non-bundle pushes pass through silently with no side effects.

---

## Phase 5: User Story 3 - Developer Hook Setup (Priority: P2)

**Goal**: A single script invocation activates the pre-push hook for a developer after cloning.

**Independent Test**: Run `scripts/setup.sh` in a fresh clone, verify `git config core.hooksPath` returns `.githooks`.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US3] Write failing tests for setup script: configures `core.hooksPath` to `.githooks`, is idempotent (second run succeeds without errors), and exits with error outside a git repository in `tests/unit/test_setup.py`

### Implementation for User Story 3

- [x] T012 [US3] Implement setup script in `scripts/setup.sh` that runs `git config core.hooksPath .githooks`, verifies `.githooks/` directory exists, and outputs confirmation message

**Checkpoint**: Developer can activate hooks with a single command. Setup is idempotent.

---

## Phase 6: User Story 4 - Catalog Version Consistency (Priority: P3)

**Goal**: After every build, catalog.json version and description match bundle.yml exactly.

**Independent Test**: Compare `version` and `description` fields between `bundle/bundle.yml` and `catalog.json` after a successful build.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [US4] Write failing tests verifying catalog.json `version` and `description` fields match the corresponding values from `bundle/bundle.yml` after a successful hook execution in `tests/unit/test_pre_push_hook.py`

### Implementation for User Story 4

Implementation is covered by the catalog update logic in T008. This phase validates version consistency independently.

**Checkpoint**: Catalog always reflects the manifest's version and description after a build.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, robustness, and end-to-end validation

- [x] T014 [P] Add edge case handling in `.githooks/pre-push`: create catalog.json from scratch if missing, handle bundle.yml parse errors with clear error messages (exit 4)
- [x] T015 Run end-to-end validation scenarios from `quickstart.md` to verify all user stories work together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — core hook logic
- **US2 (Phase 4)**: Depends on Phase 3 (T006 implements detection, T010 validates skip path)
- **US3 (Phase 5)**: Depends on Phase 2 only — independent of US1/US2
- **US4 (Phase 6)**: Depends on Phase 3 (T008 implements catalog update, T013 validates consistency)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **US2 (P2)**: Shares implementation with US1 (T006) but tests independently via T010
- **US3 (P2)**: Fully independent — can start after Foundational in parallel with US1
- **US4 (P3)**: Shares implementation with US1 (T008) but tests independently via T013

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Skeleton → detection → execution → output → commit flow
- Story complete before moving to next priority

### Parallel Opportunities

- T004 and T005 can run in parallel (different test classes in same file)
- T011 can run in parallel with T004/T005 (different test file)
- US3 (Phase 5) can be developed in parallel with US1 (Phase 3) after foundational phase

---

## Parallel Example: User Story 1

```bash
# Launch tests for US1 in parallel (different test classes):
Task: "T004 - Tests for change detection + validate/build in tests/unit/test_pre_push_hook.py"
Task: "T005 - Tests for catalog update + auto-commit in tests/unit/test_pre_push_hook.py"

# Then implement sequentially (same file, dependent logic):
Task: "T006 - Ref parsing + change detection"
Task: "T007 - CLI check + validate + build"
Task: "T008 - Remote parsing + catalog update"
Task: "T009 - Stash + auto-commit + restore"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003)
3. Complete Phase 3: User Story 1 (T004-T009)
4. **STOP and VALIDATE**: Test US1 independently — push a bundle change, verify build + catalog + commit
5. Deploy if ready — the core automation works

### Incremental Delivery

1. Setup + Foundational → Hook skeleton ready
2. Add US1 → Test independently → Core automation works (MVP!)
3. Add US2 → Test independently → Non-bundle pushes verified silent
4. Add US3 → Test independently → Setup script for new developers
5. Add US4 → Test independently → Version consistency verified
6. Polish → Edge cases + end-to-end validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 and US4 share implementation with US1 but have independent test phases
- Constitution Principle VI requires all tests written FIRST and failing before implementation
- All bash scripts target bash 3.2+ (macOS compatibility)
- Hook stderr uses `[bundle-build]` prefix per contracts/hook-exit-codes.md
