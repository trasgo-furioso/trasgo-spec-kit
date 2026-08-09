# Tasks: Discovery Command Hooks

**Input**: Design documents from `specs/010-discovery-hooks/`

**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests are REQUIRED per the project constitution (Principle VI: Test-Driven Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project initialization needed. This feature modifies existing files only.

- [ ] T001 Verify current test suite passes by running `.venv/bin/pytest tests/unit/ -v`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tests for the hook registration contract must be updated before any implementation can proceed.

- [ ] T002 [P] Add `"before_discovery"` to `EXPECTED_GATE_HOOKS` list and `"after_discovery"` to `EXPECTED_NUDGE_HOOKS` list in `tests/unit/test_hook_registration.py`
- [ ] T003 [P] Add `EXPECTED_STATUS_HOOKS` list with `"before_specify"`, `"before_tasks"`, `"after_plan"`, `"after_implement"`, and `"after_discovery"` entries in `tests/unit/test_hook_registration.py`, plus a `test_status_hooks_count` test method that asserts 5 status hooks total
- [ ] T004 Update `build_hooks_yaml()` in `tests/unit/test_hook_registration.py` to generate `before_discovery` (flow-gate, mandatory, priority 10) and `after_discovery` (status mandatory priority 5, flow-nudge optional priority 10) hook entries
- [ ] T005 Update `test_total_hook_count` from 11 to 14 (adding 3 new entries: 1 gate + 1 nudge + 1 status) in `tests/unit/test_hook_registration.py`
- [ ] T006 Update `test_gate_hooks_count` from 8 to 9 and `test_nudge_hooks_count` from 3 to 4 in `tests/unit/test_hook_registration.py`
- [ ] T007 Update `test_applying_hooks_twice_produces_same_result` assertion from 11 to 14 in `tests/unit/test_hook_registration.py`

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_hook_registration.py -v` — tests should FAIL (red) because `build_hooks_yaml()` doesn't yet generate discovery hooks and counts are wrong.

---

## Phase 3: User Story 1 — Hook Dispatch in Discovery Command (Priority: P1)

**Goal**: Add Pre-Execution Checks and Mandatory Post-Execution Hooks sections to the discovery command file so it dispatches `before_discovery` and `after_discovery` hooks.

**Independent Test**: Register a test hook under `before_discovery` in extensions.yml, run the discovery command, and verify the hook was dispatched.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Create `tests/unit/test_discovery_hooks.py` with `TestDiscoveryCommandPreHooks` class: test that `bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md` contains "Pre-Execution Checks" section header
- [ ] T009 [P] [US1] Add `TestDiscoveryCommandPostHooks` class in `tests/unit/test_discovery_hooks.py`: test that command file contains "Mandatory Post-Execution Hooks" section header
- [ ] T010 [P] [US1] Add `TestDiscoveryHookKeys` class in `tests/unit/test_discovery_hooks.py`: test that command file references `hooks.before_discovery` and `hooks.after_discovery` key strings
- [ ] T011 [P] [US1] Add `TestDiscoveryAbortGuard` class in `tests/unit/test_discovery_hooks.py`: test that post-hooks block contains the abort guard text ("session was aborted" or "skip this section")
- [ ] T012 [P] [US1] Add `TestDiscoveryHookProtocol` class in `tests/unit/test_discovery_hooks.py`: test that command file contains `EXECUTE_COMMAND` directive and `optional` flag handling instructions
- [ ] T013 [P] [US1] Add `TestDiscoveryDotToHyphen` class in `tests/unit/test_discovery_hooks.py`: test that command file contains the dot-to-hyphen mapping instruction (FR-006)

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py -v` — all tests should FAIL (red).

### Implementation for User Story 1

- [ ] T014 [US1] Insert Pre-Execution Checks section in `bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md` between "User Input" and "Goal" sections, using the exact block from `specs/010-discovery-hooks/contracts/command-blocks.md`
- [ ] T015 [US1] Insert Mandatory Post-Execution Hooks section in `bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md` between step 10 ("Session finalization") and "Done When" section, using the exact block from `specs/010-discovery-hooks/contracts/command-blocks.md` including the abort guard
- [ ] T016 [US1] Add `- [ ] Extension hooks dispatched or skipped according to the rules above` to the Done When checklist in `bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md`

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py -v` — all tests should PASS (green).

---

## Phase 4: User Story 2 — Discovery to Opportunity Transition via After Hook (Priority: P2)

**Goal**: Register the `speckit.trasgospec.status` command as a mandatory `after_discovery` hook in the bundle's `extension.yml` so the Discovery-to-Opportunity transition fires automatically.

**Independent Test**: Verify `extension.yml` contains `after_discovery` hook declaration with `speckit.trasgospec.status` command.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US2] Add `TestExtensionYmlAfterDiscovery` class in `tests/unit/test_discovery_hooks.py`: test that `bundle/extensions/trasgospec/extension.yml` contains `after_discovery` key under `hooks`
- [ ] T018 [P] [US2] Add test in `TestExtensionYmlAfterDiscovery`: verify `after_discovery` hooks include a mandatory entry with command `speckit.trasgospec.status` and description mentioning "Opportunity"

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py::TestExtensionYmlAfterDiscovery -v` — tests should FAIL (red).

### Implementation for User Story 2

- [ ] T019 [US2] Add `after_discovery` hook declarations to `bundle/extensions/trasgospec/extension.yml` under `hooks:` with status (mandatory, priority 5) and flow-nudge (optional, priority 10) entries per `specs/010-discovery-hooks/contracts/hook-registration.md`

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py::TestExtensionYmlAfterDiscovery -v` — tests should PASS (green).

---

## Phase 5: User Story 3 — Branch Gating Before Discovery (Priority: P2)

**Goal**: Register the `speckit.trasgospec.flow-gate` command as a mandatory `before_discovery` hook in the bundle's `extension.yml` so branch discipline is enforced before discovery.

**Independent Test**: Verify `extension.yml` contains `before_discovery` hook declaration with `speckit.trasgospec.flow-gate` command.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T020 [P] [US3] Add `TestExtensionYmlBeforeDiscovery` class in `tests/unit/test_discovery_hooks.py`: test that `bundle/extensions/trasgospec/extension.yml` contains `before_discovery` key under `hooks`
- [ ] T021 [P] [US3] Add test in `TestExtensionYmlBeforeDiscovery`: verify `before_discovery` hook has command `speckit.trasgospec.flow-gate` and `optional: false`

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py::TestExtensionYmlBeforeDiscovery -v` — tests should FAIL (red).

### Implementation for User Story 3

- [ ] T022 [US3] Add `before_discovery` hook declaration to `bundle/extensions/trasgospec/extension.yml` under `hooks:` with flow-gate (mandatory) entry per `specs/010-discovery-hooks/contracts/hook-registration.md`

**Checkpoint**: Run `.venv/bin/pytest tests/unit/test_discovery_hooks.py::TestExtensionYmlBeforeDiscovery -v` — tests should PASS (green).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all user stories.

- [ ] T023 Run full test suite: `.venv/bin/pytest tests/unit/test_discovery_hooks.py tests/unit/test_hook_registration.py -v` — all tests pass
- [ ] T024 Run bundle validation: `specify bundle validate --path bundle --offline`
- [ ] T025 Run quickstart.md validation scenarios from `specs/010-discovery-hooks/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — updates test infrastructure
- **User Story 1 (Phase 3)**: Depends on Foundational — command file changes
- **User Story 2 (Phase 4)**: Depends on Foundational — can run in parallel with US1 and US3
- **User Story 3 (Phase 5)**: Depends on Foundational — can run in parallel with US1 and US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Independent of US1 (different file: extension.yml vs command file)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) — Independent of US1 and US2 (same file as US2 but different section)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation makes tests pass
- Checkpoint validates before moving on

### Parallel Opportunities

- T002 + T003 can run in parallel (different sections of same file, but logically independent)
- T008–T013 can all run in parallel (all create test classes in the new test file)
- T017 + T018 can run in parallel (same test class)
- T020 + T021 can run in parallel (same test class)
- US1, US2, and US3 implementation phases can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create TestDiscoveryCommandPreHooks in tests/unit/test_discovery_hooks.py"
Task: "Create TestDiscoveryCommandPostHooks in tests/unit/test_discovery_hooks.py"
Task: "Create TestDiscoveryHookKeys in tests/unit/test_discovery_hooks.py"
Task: "Create TestDiscoveryAbortGuard in tests/unit/test_discovery_hooks.py"
Task: "Create TestDiscoveryHookProtocol in tests/unit/test_discovery_hooks.py"
Task: "Create TestDiscoveryDotToHyphen in tests/unit/test_discovery_hooks.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify existing tests)
2. Complete Phase 2: Foundational (update hook registration tests)
3. Complete Phase 3: User Story 1 (add hook blocks to command file)
4. **STOP and VALIDATE**: Test command file contains all hook dispatch infrastructure
5. Discovery command now supports hooks even without specific registrations

### Incremental Delivery

1. Complete Setup + Foundational → Test infrastructure ready
2. Add User Story 1 → Command file has hook dispatch → Validate
3. Add User Story 2 + 3 → extension.yml declares hooks → Validate
4. Polish → Full validation → Ready for review

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- `.specify/extensions.yml` and `.claude/skills/.../SKILL.md` are managed by speckit and NOT modified directly — only `bundle/` files and tests are modified
