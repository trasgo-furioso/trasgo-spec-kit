# Tasks: Audit and Logs

**Input**: Design documents from `specs/011-audit-and-logs/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization — gitignore and test infrastructure

- [x] T001 Add `.specify/` to `.gitignore` and remove `.specify/` from git tracking
- [x] T002 [P] Create test helper `run_commit_sh()` in `tests/unit/test_commit.py` that runs `commit.sh` against a `tmp_path` git repo

**Checkpoint**: `.specify/` is gitignored, test infrastructure ready

---

## Phase 2: Foundational — commit.sh Script

**Purpose**: The deterministic script that gathers git state. MUST be complete before the command file can be built.

**⚠️ CRITICAL**: The command file (US1) depends on this script's JSON contract.

### Tests for commit.sh

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T003 [P] Test that `commit.sh` outputs valid JSON with all required fields (`changed_files`, `new_files`, `deleted_files`, `has_changes`, `branch`, `has_remote`, `error`) in `tests/unit/test_commit.py`
- [x] T004 [P] Test that `commit.sh` detects modified tracked files and includes them in `changed_files` with correct path and status in `tests/unit/test_commit.py`
- [x] T005 [P] Test that `commit.sh` detects untracked new files and includes them in `new_files` in `tests/unit/test_commit.py`
- [x] T006 [P] Test that `commit.sh` detects deleted files and includes them in `deleted_files` in `tests/unit/test_commit.py`
- [x] T007 [P] Test that `commit.sh` sets `has_changes` to `false` when no files have changed in `tests/unit/test_commit.py`
- [x] T008 [P] Test that `commit.sh` reports `branch: null` and `error` message on detached HEAD in `tests/unit/test_commit.py`
- [x] T009 [P] Test that `commit.sh` excludes `.specify/` files from all arrays (gitignored) in `tests/unit/test_commit.py`
- [x] T010 [P] Test that `commit.sh` reports `has_remote: true` when branch has upstream and `false` when not in `tests/unit/test_commit.py`

### Implementation

- [x] T011 Implement `commit.sh` in `bundle/extensions/trasgospec/scripts/bash/commit.sh` per the JSON contract in `contracts/commit-script-json.md` — use `git status --porcelain` repo-wide, parse output into `changed_files`/`new_files`/`deleted_files`, check branch state with `git rev-parse`, check remote with `git config --get branch.<name>.remote`
- [x] T012 Run all commit.sh tests (T003–T010) and verify they pass in `tests/unit/test_commit.py`

**Checkpoint**: `commit.sh` produces correct JSON for all scenarios

---

## Phase 3: User Story 1+4 — Automatic Commit and Push + Gitignore (Priority: P1) 🎯 MVP

**Goal**: The commit command performs the full git cycle: detect → decide → stage → commit → push. The `.specify/` directory is excluded from commits.

**Independent Test**: Run the commit command after modifying files, verify a commit is created with the structured message format and pushed to remote.

### Tests for US1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Test that the command file frontmatter declares `scripts.sh` pointing to `scripts/bash/commit.sh` in `tests/unit/test_commit.py`
- [x] T014 [P] [US1] Integration test: after creating files in a test repo, the commit command creates a commit with the `<path> - <description>` message format in `tests/integration/test_commit_integration.py`

### Implementation for US1

- [x] T015 [US1] Create command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.commit.md` with YAML frontmatter (`description`, `scripts.sh`) and AI instructions for: running the script, inspecting diffs to generate descriptions, deciding what to include (asking user when unsure about secrets/binaries/unrelated files), staging with `git add`, committing with structured message, pushing with `git push`, handling errors gracefully
- [x] T016 [US1] Register the commit command in `bundle/extensions/trasgospec/extension.yml` under `provides.commands` with name `speckit.trasgospec.commit`, aliases `["trasgospec.commit"]`

**Checkpoint**: The commit command can be invoked manually and performs the full git cycle

---

## Phase 4: User Story 2 — Readable Audit Trail (Priority: P2)

**Goal**: Automated commit messages are human-readable and distinctive — each line is `<repo-relative-path> - <description>`.

**Independent Test**: After several skill runs with the commit hook, `git log` shows structured, parseable commit messages.

### Implementation for US2

- [x] T017 [US2] Add commit message format examples and validation rules to the command file instructions in `bundle/extensions/trasgospec/commands/speckit.trasgospec.commit.md` — ensure the AI generates descriptions by inspecting diffs (for modified files) or file content (for new files), keeps descriptions under 80 chars, uses full repo-relative paths, and produces no tags/headers/footers

**Checkpoint**: Commit messages are consistently formatted and readable in `git log`

---

## Phase 5: User Story 3 — Hook Registration (Priority: P3)

**Goal**: The commit command is automatically triggered after every artifact-producing skill via `after_*` hooks with priority 20.

**Independent Test**: Inspect `extension.yml` and verify `after_*` entries for all 8 artifact-producing skills.

### Tests for US3

- [x] T018 [US3] Test that `extension.yml` contains `after_*` hook entries for all 8 phases (discovery, specify, clarify, checklist, plan, tasks, implement, converge) pointing to `speckit.trasgospec.commit` with `priority: 20` in `tests/unit/test_commit.py`

### Implementation for US3

- [x] T019 [US3] Add `after_*` hook declarations to `bundle/extensions/trasgospec/extension.yml` for all 8 artifact-producing skills: `after_discovery`, `after_specify`, `after_clarify`, `after_checklist`, `after_plan`, `after_tasks`, `after_implement`, `after_converge` — each with `command: speckit.trasgospec.commit`, `optional: false`, `priority: 20`, `description: "Audit — auto-commit and push"`

**Checkpoint**: Hook entries registered for all artifact-producing skills

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T020 Run `specify bundle validate --path bundle --offline` to verify the bundle manifest is valid with the new command and hooks
- [x] T021 Run quickstart.md validation scenarios to verify end-to-end behavior
- [x] T022 Run full test suite `.venv/bin/pytest tests/ -v` to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T002 from Setup (test helper)
- **US1+US4 (Phase 3)**: Depends on Phase 2 (commit.sh must be complete)
- **US2 (Phase 4)**: Depends on Phase 3 (command file must exist to add format rules)
- **US3 (Phase 5)**: Depends on Phase 3 (command must be registered before hooks can reference it)
- **Polish (Phase 6)**: Depends on all previous phases

### User Story Dependencies

- **US1+US4 (P1)**: Depends on Foundational — no dependencies on other stories
- **US2 (P2)**: Depends on US1 — refines the command file's message generation instructions
- **US3 (P3)**: Depends on US1 — hooks reference the registered command

### Within Each Phase

- Tests MUST be written and FAIL before implementation
- Script before command file
- Command file before hook registration

### Parallel Opportunities

- T002 can run in parallel with T001 (different files)
- T003–T010 can all run in parallel (independent test cases in the same file)
- T013–T014 can run in parallel (different test files)

---

## Parallel Example: Phase 2 Tests

```bash
# All commit.sh tests can be written in parallel:
Task: T003 "Test JSON output fields"
Task: T004 "Test modified file detection"
Task: T005 "Test new file detection"
Task: T006 "Test deleted file detection"
Task: T007 "Test no-changes case"
Task: T008 "Test detached HEAD"
Task: T009 "Test .specify/ exclusion"
Task: T010 "Test remote detection"
```

---

## Implementation Strategy

### MVP First (US1+US4 Only)

1. Complete Phase 1: Setup (.gitignore + test helper)
2. Complete Phase 2: Foundational (commit.sh with TDD)
3. Complete Phase 3: US1+US4 (command file + command registration)
4. **STOP and VALIDATE**: Test the commit command manually
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → commit.sh working
2. Add US1+US4 → Full commit cycle works → MVP!
3. Add US2 → Commit messages refined
4. Add US3 → Hooks registered, fully automatic
5. Polish → Bundle validated, all tests pass

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution requires TDD: tests written first, must fail before implementation
- `.specify/` must be gitignored before any commit work begins (prevents noise)
- The command file contains AI instructions — not code. It tells the AI how to run the script, interpret JSON, inspect diffs, and make commit decisions.
- All bash scripts must target bash 3.2+ (no `mapfile`/`readarray`)
