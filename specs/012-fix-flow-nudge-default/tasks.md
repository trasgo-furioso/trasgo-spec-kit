# Tasks: Fix Flow-Nudge Default Execution

**Input**: Design documents from `specs/012-fix-flow-nudge-default/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: Required per Constitution Principle VI (Test-Driven Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create preset directory structure and update bundle manifest

- [x] T001 Create preset directory structure at `bundle/presets/trasgospec/templates/`
- [x] T002 Create preset manifest at `bundle/presets/trasgospec/preset.yml` with id `trasgospec` and version matching bundle
- [x] T003 Update `bundle/bundle.yml` to declare preset under `provides.presets`

---

## Phase 2: Foundational (Rename flow-nudge → deliver)

**Purpose**: Rename all flow-nudge artifacts to deliver. MUST complete before user stories.

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Write unit test verifying deliver.sh produces valid JSON contract in `tests/unit/test_deliver.py`
- [x] T005 Copy `bundle/extensions/trasgospec/scripts/bash/flow-nudge.sh` to `bundle/extensions/trasgospec/scripts/bash/deliver.sh` and update internal references
- [x] T006 Create `bundle/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` based on flow-nudge command with updated script reference
- [x] T007 Update command registration in `bundle/extensions/trasgospec/extension.yml`: rename `speckit.trasgospec.flow-nudge` to `speckit.trasgospec.deliver`, update file path, update aliases to `trasgospec.deliver`
- [x] T008 Update all hook registrations in `bundle/extensions/trasgospec/extension.yml` from `speckit.trasgospec.flow-nudge` to `speckit.trasgospec.deliver`
- [x] T009 Delete old files: `bundle/extensions/trasgospec/commands/speckit.trasgospec.flow-nudge.md` and `bundle/extensions/trasgospec/scripts/bash/flow-nudge.sh`
- [x] T010 Run `test_deliver.py` — verify tests pass with renamed script

**Checkpoint**: All flow-nudge references replaced with deliver. Old files removed.

---

## Phase 3: User Story 1 - Deliver Runs Automatically (Priority: P1) MVP

**Goal**: Deliver hooks execute automatically at workflow milestones without prompting.

**Independent Test**: Run `/speckit-plan` on a feature branch and verify deliver auto-executes and creates a draft PR.

### Tests for User Story 1

- [x] T011 [P] [US1] Write unit test verifying all 4 deliver hooks in extension.yml have `optional: false` in `tests/unit/test_deliver.py`

### Implementation for User Story 1

- [x] T012 [US1] Set all 4 deliver hook registrations to `optional: false` in `bundle/extensions/trasgospec/extension.yml` (after_plan, after_implement, after_analyze, after_discovery)
- [x] T013 [US1] Rewrite `bundle/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` to remove confirmation prompts — execute `gh pr create`/`gh pr ready` directly when `suggested_action` is `create_draft` or `mark_ready`
- [x] T014 [US1] Run `test_deliver.py` — verify hook registration tests pass

**Checkpoint**: Deliver auto-executes at all milestones. No confirmation prompts.

---

## Phase 4: User Story 4 - PR Body Driven by Template (Priority: P2)

**Goal**: PR title and body composed from a `pr-template.md` template with `{{spec_title}}` and `{{spec_summary}}` placeholders.

**Independent Test**: Verify `specify preset resolve pr-template` resolves to the installed template and deliver uses it.

### Tests for User Story 4

- [x] T015 [P] [US4] Write unit test verifying `bundle/presets/trasgospec/templates/pr-template.md` exists and contains required frontmatter in `tests/unit/test_deliver.py`

### Implementation for User Story 4

- [x] T016 [US4] Create `bundle/presets/trasgospec/templates/pr-template.md` with frontmatter `title: "feat({{spec_dir}}): {{spec_title}}"` and body with `{{spec_title}}` and `{{spec_summary}}` placeholders
- [x] T017 [US4] Update `bundle/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` to resolve `pr-template` via preset resolution, parse frontmatter for title pattern, interpolate `{{spec_title}}` and `{{spec_summary}}`, and fall back to hardcoded defaults if template not found
- [x] T018 [US4] Run `test_deliver.py` — verify template existence test passes

**Checkpoint**: PRs created by deliver use the pr-template for title and body.

---

## Phase 5: User Story 5 - Commit Message Driven by Template (Priority: P2)

**Goal**: Commit messages composed using `commit-template.md` format instructions, defaulting to current one-line-per-file format.

**Independent Test**: Verify `specify preset resolve commit-template` resolves to the installed template.

### Tests for User Story 5

- [x] T019 [P] [US5] Write unit test verifying `bundle/presets/trasgospec/templates/commit-template.md` exists in `tests/unit/test_commit_template.py`

### Implementation for User Story 5

- [x] T020 [US5] Create `bundle/presets/trasgospec/templates/commit-template.md` with format instructions for one-line-per-file messages (`<repo-relative-path> - <description>`, no tags/prefixes/trailers)
- [x] T021 [US5] Update `bundle/extensions/trasgospec/commands/speckit.trasgospec.commit.md` to resolve `commit-template` via preset resolution and use template instructions when composing messages, falling back to hardcoded format if template not found
- [x] T022 [US5] Run `test_commit_template.py` — verify template existence test passes

**Checkpoint**: Commit command uses commit-template for message format.

---

## Phase 6: User Story 2 - Graceful Fallback (Priority: P2)

**Goal**: When `gh` is unavailable or `gh_integration` is `false`, deliver displays a suggestion block and exits successfully.

**Independent Test**: Remove `gh` from PATH, run deliver, verify suggestion block displayed and exit code 0.

### Tests for User Story 2

- [x] T023 [P] [US2] Write unit test verifying deliver.sh exits code 0 and includes `suggested_action` when gh is not available in `tests/unit/test_deliver.py`

### Implementation for User Story 2

- [x] T024 [US2] Verify `bundle/extensions/trasgospec/commands/speckit.trasgospec.deliver.md` displays suggestion block when `gh_available` is `false` or `gh_integration` is `false`, and report errors from `gh pr create`/`gh pr ready` without blocking workflow
- [x] T025 [US2] Run `test_deliver.py` — verify fallback tests pass

**Checkpoint**: Deliver degrades gracefully without gh.

---

## Phase 7: User Story 3 - User Override to Optional (Priority: P3)

**Goal**: Users can override deliver hooks to `optional: true` in local config to restore suggestion-only behavior.

**Independent Test**: Set `optional: true` on a deliver hook in local extension.yml and verify it displays as suggestion.

### Implementation for User Story 3

- [x] T026 [US3] Verify the deliver command file instructions handle both auto-execution (no prompt) and suggestion display modes correctly — no code changes expected, just validation that the hook processor's optional/mandatory distinction works with the new command

**Checkpoint**: Override mechanism works. Feature complete.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation

- [x] T027 Mirror all `bundle/extensions/trasgospec/extension.yml` changes to installed copy at `.specify/extensions/trasgospec/extension.yml`
- [x] T028 Mirror deliver command and script to installed copy at `.specify/extensions/trasgospec/`
- [x] T029 Run full test suite: `.venv/bin/pytest tests/unit/ -v`
- [x] T030 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — core bug fix
- **US4 (Phase 4)**: Depends on Foundational — can run parallel with US1
- **US5 (Phase 5)**: Depends on Setup only — independent of deliver
- **US2 (Phase 6)**: Depends on US1 — verifies fallback after prompts removed
- **US3 (Phase 7)**: Depends on US1 — verifies override after hooks changed
- **Polish (Phase 8)**: Depends on all stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependencies on other stories
- **US4 (P2)**: Can start after Foundational — no dependencies on other stories
- **US5 (P2)**: Can start after Setup — independent of deliver rename
- **US2 (P2)**: Should follow US1 to verify fallback with new command
- **US3 (P3)**: Should follow US1 to verify override with new hooks

### Parallel Opportunities

- T001, T002, T003 can run in parallel (Setup)
- T011, T015, T019, T023 can run in parallel (all test writing)
- US4 and US5 can proceed in parallel after Foundational
- US1 and US4 can proceed in parallel after Foundational

---

## Parallel Example: After Foundational

```bash
# US1 and US4 can run in parallel:
Task: "T012 [US1] Set all 4 deliver hooks to optional: false"
Task: "T016 [US4] Create pr-template.md"

# US5 can run in parallel with everything after Setup:
Task: "T020 [US5] Create commit-template.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (preset dirs)
2. Complete Phase 2: Foundational (rename flow-nudge → deliver)
3. Complete Phase 3: US1 (hooks optional:false + no prompts)
4. **STOP and VALIDATE**: Deliver auto-executes after /speckit-plan
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Rename complete
2. Add US1 → Deliver auto-executes → MVP!
3. Add US4 → PR uses template → Customizable PRs
4. Add US5 → Commit uses template → Customizable commits
5. Add US2 + US3 → Fallback + override verified → Feature complete
6. Polish → All tests pass, installed copies mirrored

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution Principle VI requires tests first (red-green-refactor)
- Constitution Principle VII requires templates for artifact-producing commands
- Old flow-nudge files are DELETED, not kept alongside deliver
- Commit after each task or logical group
