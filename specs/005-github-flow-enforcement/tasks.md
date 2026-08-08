# Tasks: GitHub Flow Enforcement

**Input**: Design documents from `/specs/005-github-flow-enforcement/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per Constitution Principle VI (Test-Driven Development). All tests use pytest and must fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and manifest updates for the new commands

- [x] T001 Update extension manifest to declare flow-gate and flow-nudge commands in bundle/extensions/trasgospec/extension.yml
- [x] T002 Update bundle manifest version from 0.2.0 to 0.3.0 in bundle/bundle.yml
- [x] T003 Update extension version from 0.2.0 to 0.3.0 in bundle/extensions/trasgospec/extension.yml

---

## Phase 2: Foundational — Flow Context Script (User Story 4, Priority: P1)

**Purpose**: The shared `flow-context.sh` script that all hook commands depend on. MUST be complete before any hook command can be implemented.

**Goal**: Emit a single-line JSON object with deterministic git state: `current_branch`, `is_main`, `spec_dir`, `expected_branch`, `spec_branch_match`, `branch_age_days`, `commits_behind_main`, `uncommitted_changes`.

**Independent Test**: Run the script directly against a controlled git repo and verify JSON output matches expected values.

### Tests for Flow Context

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US4] Test flow-context.sh outputs valid JSON with all required fields in tests/unit/test_flow_context.py
- [x] T005 [P] [US4] Test flow-context.sh reports `is_main: true` when on main branch in tests/unit/test_flow_context.py
- [x] T006 [P] [US4] Test flow-context.sh reports `current_branch: null` on detached HEAD in tests/unit/test_flow_context.py
- [x] T007 [P] [US4] Test flow-context.sh reads `expected_branch` from spec.md `**Feature Branch**:` field in tests/unit/test_flow_context.py
- [x] T008 [P] [US4] Test flow-context.sh sets `spec_branch_match: true` when current branch matches expected_branch in tests/unit/test_flow_context.py
- [x] T009 [P] [US4] Test flow-context.sh sets `spec_branch_match: null` when feature.json is missing in tests/unit/test_flow_context.py
- [x] T010 [P] [US4] Test flow-context.sh sets `expected_branch: null` when spec.md has no Feature Branch field in tests/unit/test_flow_context.py
- [x] T011 [P] [US4] Test flow-context.sh computes `branch_age_days` and `commits_behind_main` correctly in tests/unit/test_flow_context.py

### Implementation for Flow Context

- [x] T012 [US4] Implement flow-context.sh with repo root discovery, feature.json parsing, spec.md branch extraction, and git state queries in bundle/extensions/trasgospec/scripts/bash/flow-context.sh
- [x] T013 [US4] Verify all flow-context tests pass after implementation

**Checkpoint**: flow-context.sh produces correct JSON for all git states. All downstream commands can source it.

---

## Phase 3: User Story 1 — Branch Gate via Hook (Priority: P1) MVP

**Goal**: Block flow-aware skills on `main` and create/switch to feature branch after specify. The flow-gate command uses flow-context.sh to check git state, then gates or proceeds.

**Independent Test**: Run any skill on `main` → blocked. Run after specify → branch created/switched. Run on feature branch → proceeds.

### Tests for Branch Gate

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US1] Test flow-gate script exits with gate-block JSON when on main in tests/unit/test_flow_gate.py
- [x] T015 [P] [US1] Test flow-gate script exits with gate-pass JSON when on feature branch in tests/unit/test_flow_gate.py
- [x] T016 [P] [US1] Test flow-gate script includes mismatch warning when branch does not match expected_branch in tests/unit/test_flow_gate.py
- [x] T017 [P] [US1] Test flow-gate script blocks on detached HEAD in tests/unit/test_flow_gate.py

### Implementation for Branch Gate

- [x] T018 [US1] Implement flow-context.sh wrapper logic in flow-gate script (sources flow-context.sh, adds gate decision) — determine if this needs a separate script or if flow-context.sh output is sufficient for the command file
- [x] T019 [US1] Create flow-gate command file with AI agent instructions for after_specify mode (create/switch branch) and before_* mode (block on main, warn on mismatch) in bundle/extensions/trasgospec/commands/speckit.trasgospec.flow-gate.md
- [x] T020 [US1] Verify all flow-gate tests pass after implementation

**Checkpoint**: Flow-gate works as both after_specify (branch creation) and before_* (branch gating). User Story 1 is fully functional.

---

## Phase 4: User Story 2 & 3 — PR Nudges with Configurable gh Integration (Priority: P2)

**Goal**: Suggest PR actions at workflow milestones (after plan, implement, analyze). Adapt behavior based on gh_integration setting and gh availability. US2 and US3 are combined because the nudge command and gh integration are inseparable — the nudge delivers its value through gh.

**Independent Test**: Run plan/implement/analyze skills on a feature branch and verify appropriate PR nudge appears. Toggle gh_integration and verify output-only vs auto mode.

### Tests for PR Nudges

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T021 [P] [US2] Test flow-nudge.sh infers `plan` phase when plan.md exists but tasks.md does not in tests/unit/test_flow_nudge.py
- [x] T022 [P] [US2] Test flow-nudge.sh infers `implement` phase when tasks.md exists in tests/unit/test_flow_nudge.py
- [x] T023 [P] [US2] Test flow-nudge.sh suggests `create_draft` when no PR exists at plan phase in tests/unit/test_flow_nudge.py
- [x] T024 [P] [US2] Test flow-nudge.sh suggests `mark_ready` when draft PR exists at implement phase in tests/unit/test_flow_nudge.py
- [x] T025 [P] [US2] Test flow-nudge.sh suggests `none` when PR is already non-draft in tests/unit/test_flow_nudge.py
- [x] T026 [P] [US3] Test flow-nudge.sh sets `gh_available: false` when gh is not in PATH in tests/unit/test_flow_nudge.py
- [x] T027 [P] [US3] Test flow-nudge.sh reads gh_integration setting from extensions.yml in tests/unit/test_flow_nudge.py
- [x] T028 [P] [US3] Test flow-nudge.sh skips gh calls when gh_integration is false in tests/unit/test_flow_nudge.py

### Implementation for PR Nudges

- [x] T029 [US2] Implement flow-nudge.sh: source flow-context.sh, read gh_integration from extensions.yml, query PR state via gh (when available), infer phase from artifacts, compute suggested_action in bundle/extensions/trasgospec/scripts/bash/flow-nudge.sh
- [x] T030 [US2] Create flow-nudge command file with AI agent instructions for rendering PR suggestions, auto-executing gh commands, and output-only fallback in bundle/extensions/trasgospec/commands/speckit.trasgospec.flow-nudge.md
- [x] T031 [US2] Verify all flow-nudge and gh-integration tests pass after implementation

**Checkpoint**: PR nudges fire at correct phases with correct suggestions. gh integration works in all three modes (auto, fallback, disabled).

---

## Phase 5: User Story 6 — Hook Registration on Bundle Install (Priority: P1)

**Goal**: When trasgospec is installed, register all 11 hook entries in `.specify/extensions.yml` automatically and idempotently.

**Independent Test**: Install the bundle into a clean project and verify extensions.yml contains all expected hook entries. Install again and verify no duplicates.

### Tests for Hook Registration

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T032 [P] [US6] Test hook registration adds all 11 hook entries to a clean extensions.yml in tests/unit/test_hook_registration.py
- [x] T033 [P] [US6] Test hook registration is idempotent (running twice produces same result) in tests/unit/test_hook_registration.py
- [x] T034 [P] [US6] Test hook registration preserves existing hooks from other extensions in tests/unit/test_hook_registration.py

### Implementation for Hook Registration

- [x] T035 [US6] Implement hook registration logic (script or install-time mechanism) that adds gate and nudge hooks to extensions.yml idempotently
- [x] T036 [US6] Verify all hook registration tests pass after implementation

**Checkpoint**: Bundle install produces correct extensions.yml with all hooks. Idempotent and non-destructive.

---

## Phase 6: User Story 5 — Read-Only Commands Excluded (Priority: P3)

**Goal**: Verify that roadmap and hello commands have no flow hooks registered and execute normally on any branch.

**Independent Test**: Run both commands on main and verify no flow-related output.

### Verification

- [x] T037 [US5] Verify no hook entries exist for roadmap or hello commands in the hook registration contract and implementation
- [x] T038 [US5] Update test_extension_manifests.py to expect 4 commands (hello, roadmap, flow-gate, flow-nudge) instead of 2 in tests/unit/test_extension_manifests.py

**Checkpoint**: Read-only commands confirmed unaffected by flow enforcement.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T039 Run full test suite to verify no regressions: `.venv/bin/pytest tests/unit/ -v`
- [x] T040 Validate bundle manifest: `specify bundle validate --path bundle --offline`
- [x] T041 Run quickstart.md validation scenarios end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Flow Context)**: Depends on Phase 1 — BLOCKS all hook commands
- **Phase 3 (Branch Gate)**: Depends on Phase 2 — uses flow-context.sh
- **Phase 4 (PR Nudges)**: Depends on Phase 2 — uses flow-context.sh; independent of Phase 3
- **Phase 5 (Hook Registration)**: Depends on Phases 3 and 4 — registers commands that must exist
- **Phase 6 (Read-Only Exclusion)**: Depends on Phase 5 — verifies absence of hooks
- **Phase 7 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US4 (Flow Context)**: Foundational — no dependencies on other stories
- **US1 (Branch Gate)**: Depends on US4 (flow-context.sh)
- **US2/US3 (PR Nudges + gh)**: Depends on US4 (flow-context.sh); independent of US1
- **US6 (Hook Registration)**: Depends on US1 and US2/US3 (commands must exist to register)
- **US5 (Read-Only Exclusion)**: Depends on US6 (verifies hook registration correctness)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Script before command file (deterministic before AI instructions)
- Verify tests pass after implementation

### Parallel Opportunities

- All test tasks within a phase marked [P] can run in parallel
- Phase 3 (US1) and Phase 4 (US2/US3) can run in parallel after Phase 2 completes
- T001, T002, T003 (setup) can all run in parallel

---

## Parallel Example: Phase 2 (Flow Context Tests)

```bash
# Launch all flow-context tests in parallel (all different test cases, same file):
Task: T004 "Test valid JSON output"
Task: T005 "Test is_main on main branch"
Task: T006 "Test detached HEAD"
Task: T007 "Test expected_branch extraction"
Task: T008 "Test spec_branch_match true"
Task: T009 "Test spec_branch_match null"
Task: T010 "Test expected_branch null"
Task: T011 "Test branch_age_days and commits_behind_main"
```

## Parallel Example: After Phase 2

```bash
# Phase 3 and Phase 4 can run in parallel:
Stream A: T014-T020 (Branch Gate — US1)
Stream B: T021-T031 (PR Nudges — US2/US3)
```

---

## Implementation Strategy

### MVP First (User Stories 4 + 1)

1. Complete Phase 1: Setup (manifests)
2. Complete Phase 2: Flow Context (US4) — the data layer
3. Complete Phase 3: Branch Gate (US1) — the core enforcement
4. **STOP and VALIDATE**: Test gate blocks on main, creates branch after specify, passes on feature branch
5. This is a usable MVP — developers get branch discipline without PR nudges

### Incremental Delivery

1. Setup + Flow Context + Branch Gate → MVP (branch discipline)
2. Add PR Nudges + gh Integration → Full GitHub Flow (PR lifecycle)
3. Add Hook Registration → Automatic activation on install
4. Add Read-Only Verification → Complete feature
5. Each increment adds value without breaking previous increments

### Suggested MVP Scope

**Phases 1-3 (T001-T020)**: 20 tasks delivering flow-context.sh + flow-gate. This gives developers the core GitHub Flow discipline (branch gating) which is the highest-value part of the feature.

---

## Notes

- [P] tasks = different files or test cases, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 and US3 are combined in Phase 4 because PR nudges and gh integration are inseparable
- US5 (read-only exclusion) has no implementation tasks — it's a verification of absence
- Constitution requires TDD: all tests written and failing before implementation code
- All bash scripts must target bash 3.2+ (no mapfile, no readarray)
- All tests use `.venv/bin/pytest`
