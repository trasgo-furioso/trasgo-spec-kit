# Tasks: Spec Lifecycle Management

**Input**: Design documents from `specs/009-spec-lifecycle-management/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution Principle VI (TDD mandatory).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed — this feature extends existing scripts and adds one new extension command.

- [x] T001 Verify existing test infrastructure works: `.venv/bin/pytest tests/unit/test_scan_specs.py -v`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The `**Status**` field must be present in prd.md for PRD-only features to appear on the roadmap. The discovery script must write it.

**⚠️ CRITICAL**: US1 (roadmap visibility) and US3 (manual status command) both depend on this.

- [x] T002 Write failing test: discovery.sh writes `**Status**: Discovery` in prd.md scaffold in tests/unit/test_discovery.py
- [x] T003 Update discovery.sh to include `**Status**: Discovery` in the prd.md template at bundle/extensions/trasgospec/scripts/bash/discovery.sh
- [x] T004 Sync installed copy at .specify/extensions/trasgospec/scripts/bash/discovery.sh

**Checkpoint**: discovery.sh produces prd.md with a `**Status**` field. Tests pass.

---

## Phase 3: User Story 1 — Roadmap Shows Lifecycle Status for All Features (Priority: P1) 🎯 MVP

**Goal**: `scan-specs.sh` scans both prd.md and spec.md, extracts title from `# PRD:` headings, and includes PRD-only features on the roadmap.

**Independent Test**: Create features with different artifacts (prd-only, spec+plan, both) and verify the roadmap displays correct status for each.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Write failing test: scan-specs includes prd-only features in output in tests/unit/test_scan_specs.py
- [x] T006 [P] [US1] Write failing test: scan-specs extracts title from `# PRD:` heading in tests/unit/test_scan_specs.py
- [x] T007 [P] [US1] Write failing test: scan-specs reads `**Status**` from prd.md when no spec.md exists in tests/unit/test_scan_specs.py
- [x] T008 [P] [US1] Write failing test: spec.md takes precedence over prd.md when both exist in tests/unit/test_scan_specs.py
- [x] T009 [P] [US1] Write failing test: scan-specs reads `**Created**` from prd.md in tests/unit/test_scan_specs.py

### Implementation for User Story 1

- [x] T010 [US1] Modify scan-specs.sh to check for prd.md when spec.md is absent (file selection logic) at bundle/extensions/trasgospec/scripts/bash/scan-specs.sh
- [x] T011 [US1] Add `# PRD:` title extraction pattern alongside `# Feature Specification:` in scan-specs.sh
- [x] T012 [US1] Sync installed copy at .specify/extensions/trasgospec/scripts/bash/scan-specs.sh
- [x] T013 [US1] Run all scan-specs tests and verify they pass: `.venv/bin/pytest tests/unit/test_scan_specs.py -v`

**Checkpoint**: PRD-only features appear on the roadmap with correct title, status, and created date. `spec.md` takes precedence when both exist.

---

## Phase 4: User Story 3 — Manual Status Management Command (Priority: P2)

**Goal**: A new extension command `trasgospec.roadmap.status.change` allows users and agents to set lifecycle status on any feature's prd.md or spec.md.

**Independent Test**: Run the status command with different phase arguments and verify the `**Status**` field updates correctly.

> Note: US3 is implemented before US2 because US2 (automated hooks) depends on the status-change script existing.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US3] Write failing test: status-change.sh sets status to a valid phase in tests/unit/test_status_change.py
- [x] T015 [P] [US3] Write failing test: status-change.sh rejects invalid phase names in tests/unit/test_status_change.py
- [x] T016 [P] [US3] Write failing test: status-change.sh selects spec.md over prd.md when both exist in tests/unit/test_status_change.py
- [x] T017 [P] [US3] Write failing test: status-change.sh selects prd.md when no spec.md exists in tests/unit/test_status_change.py
- [x] T018 [P] [US3] Write failing test: status-change.sh sets Blocked status in tests/unit/test_status_change.py

### Implementation for User Story 3

- [x] T019 [US3] Create status-change.sh script with `set` action at bundle/extensions/trasgospec/scripts/bash/status-change.sh
- [x] T020 [US3] Add `blocked` action to status-change.sh
- [x] T021 [US3] Add `validate` action to status-change.sh
- [x] T022 [US3] Add input validation against valid lifecycle phases in status-change.sh
- [x] T023 [US3] Create command file speckit.trasgospec.roadmap.status.change.md at bundle/extensions/trasgospec/commands/speckit.trasgospec.roadmap.status.change.md
- [x] T024 [US3] ~~Create skill file~~ Skipped — skills are auto-generated by bundle install
- [x] T025 [US3] Register command and alias in bundle/extensions/trasgospec/extension.yml
- [x] T026 [US3] ~~Install script copy~~ Skipped — .specify/extensions is gitignored; installed by bundle install
- [x] T027 [US3] Run all status-change tests: `.venv/bin/pytest tests/unit/test_status_change.py -v`

**Checkpoint**: Users can manually set any valid lifecycle phase on any feature. Invalid phases are rejected.

---

## Phase 5: User Story 2 — Automated Status Transitions via Hooks (Priority: P2)

**Goal**: Register status-change command as hooks at the four defined transition points so status advances automatically when skills run.

**Independent Test**: Run a skill on a feature and verify the status field updates to the expected phase.

### Tests for User Story 2

- [x] T028 [P] [US2] ~~Write failing test~~ Covered by existing T014 tests — hooks pass phase via AI agent dispatch

### Implementation for User Story 2

- [x] T029 [US2] Register `before_specify` hook → `trasgospec.roadmap.status.change` in bundle/extensions/trasgospec/extension.yml
- [x] T030 [US2] Register `after_plan` hook → `trasgospec.roadmap.status.change` in bundle/extensions/trasgospec/extension.yml
- [x] T031 [US2] Register `before_tasks` hook → `trasgospec.roadmap.status.change` in bundle/extensions/trasgospec/extension.yml
- [x] T032 [US2] Register `after_implement` hook → `trasgospec.roadmap.status.change` in bundle/extensions/trasgospec/extension.yml
- [x] T033 [US2] ~~Sync hook registrations~~ Handled by bundle install
- [x] T034 [US2] Run status-change tests: `.venv/bin/pytest tests/unit/test_status_change.py -v`

**Checkpoint**: Running `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, or `/speckit-implement` automatically advances feature status.

---

## Phase 6: User Story 4 — Agents Flag Blocked Status (Priority: P3)

**Goal**: Agents can set blocked status with contextual information. This is already supported by the status-change command from US3 — this phase adds the unblock mechanism.

**Independent Test**: Set a feature to Blocked, then unblock it and verify it reverts to the prior phase from git history.

### Tests for User Story 4

- [ ] T035 [P] [US4] Write failing test: status-change.sh unblock recovers previous status from git log in tests/unit/test_status_change.py

### Implementation for User Story 4

- [ ] T036 [US4] Add `unblock` action to status-change.sh using `git log` to recover prior status at bundle/extensions/trasgospec/scripts/bash/status-change.sh
- [ ] T037 [US4] Sync installed copy at .specify/extensions/trasgospec/scripts/bash/status-change.sh
- [ ] T038 [US4] Run unblock tests: `.venv/bin/pytest tests/unit/test_status_change.py -v`

**Checkpoint**: Blocked features can be unblocked, reverting to their previous lifecycle phase recovered from git history.

---

## Phase 7: User Story 5 — PRD Quality Gate for Opportunity Status (Priority: P3)

**Goal**: When setting status to "Opportunity" on a prd.md, the script validates that all required sections are populated.

**Independent Test**: Create PRDs with varying completeness and verify only complete ones can advance to Opportunity.

### Tests for User Story 5

- [ ] T039 [P] [US5] Write failing test: quality gate passes for complete PRD in tests/unit/test_status_change.py
- [ ] T040 [P] [US5] Write failing test: quality gate fails for PRD missing Assumptions section in tests/unit/test_status_change.py
- [ ] T041 [P] [US5] Write failing test: quality gate fails for PRD missing Jobs to Be Done in tests/unit/test_status_change.py

### Implementation for User Story 5

- [ ] T042 [US5] Add quality gate evaluation to status-change.sh for Opportunity transitions on prd.md at bundle/extensions/trasgospec/scripts/bash/status-change.sh
- [ ] T043 [US5] Sync installed copy at .specify/extensions/trasgospec/scripts/bash/status-change.sh
- [ ] T044 [US5] Run quality gate tests: `.venv/bin/pytest tests/unit/test_status_change.py -v`

**Checkpoint**: PRDs must pass the quality gate to advance to Opportunity. Incomplete PRDs are rejected with specific feedback.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and bundle consistency.

- [ ] T045 [P] Run full unit test suite: `.venv/bin/pytest tests/unit/ -v`
- [ ] T046 [P] Run quickstart.md validation scenarios
- [ ] T047 Validate bundle manifest: `specify bundle validate --path bundle --offline`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Phase 1
- **US1 (Phase 3)**: Depends on Phase 2 (prd.md needs Status field)
- **US3 (Phase 4)**: Depends on Phase 2. Can run in parallel with US1.
- **US2 (Phase 5)**: Depends on US3 (hooks call the status-change script)
- **US4 (Phase 6)**: Depends on US3 (extends status-change script)
- **US5 (Phase 7)**: Depends on US3 (extends status-change script)
- **Polish (Phase 8)**: Depends on all desired user stories

### User Story Dependencies

- **US1 (P1)**: Independent after Foundational — scan-specs changes only
- **US3 (P2)**: Independent after Foundational — new script and command
- **US2 (P2)**: Depends on US3 — hooks reference the status-change command
- **US4 (P3)**: Depends on US3 — adds unblock action to status-change script
- **US5 (P3)**: Depends on US3 — adds quality gate to status-change script

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Script changes before command/skill files
- Bundle copy before installed copy sync
- Tests pass before checkpoint

### Parallel Opportunities

- T005–T009 (US1 tests) can all run in parallel
- T014–T018 (US3 tests) can all run in parallel
- T039–T041 (US5 tests) can all run in parallel
- US1 and US3 can proceed in parallel after Foundational
- US4 and US5 can proceed in parallel after US3

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
Task: "Write failing test: scan-specs includes prd-only features"
Task: "Write failing test: scan-specs extracts title from # PRD: heading"
Task: "Write failing test: scan-specs reads Status from prd.md"
Task: "Write failing test: spec.md takes precedence over prd.md"
Task: "Write failing test: scan-specs reads Created from prd.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Status field in prd.md)
3. Complete Phase 3: US1 (scan-specs sees PRD-only features)
4. **STOP and VALIDATE**: Run roadmap and verify PRD-only features appear
5. Deliver MVP — roadmap now shows full portfolio

### Incremental Delivery

1. Setup + Foundational → prd.md has Status field
2. US1 → PRD-only features visible on roadmap (MVP!)
3. US3 → Manual status management command available
4. US2 → Status transitions automate via hooks
5. US4 → Blocked/unblock workflow operational
6. US5 → Quality gate enforces PRD completeness
7. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US3 is implemented before US2 because US2's hooks depend on the status-change script
- Bundle copies and installed copies must stay in sync (T004, T012, T026, T033, T037, T043)
- All scripts must target bash 3.2+ (no mapfile, no readarray)
