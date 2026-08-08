# Tasks: Conversational Discovery Command

**Input**: Design documents from `specs/007-conversational-discovery/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included per constitution Principle VI (TDD). Tests MUST be written first and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and extension registration

- [x] T001 Register discovery command in bundle/extensions/trasgospec/extension.yml with ID `speckit.trasgospec.discovery`, alias `trasgospec.discovery`, and script reference `scripts/bash/discovery.sh`
- [x] T002 Create empty command file at bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md with YAML frontmatter (description, scripts key pointing to discovery.sh)
- [x] T003 Create empty script file at bundle/extensions/trasgospec/scripts/bash/discovery.sh with bash 3.2 boilerplate (set -euo pipefail, _find_specify_root, common.sh sourcing, json_escape fallback)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Script implementation — all user stories depend on the script creating the directory and scaffold

**CRITICAL**: No user story work can begin until the script is functional

### Tests

- [x] T004 [P] Write unit test for sequential numbering logic (no existing specs → 001, existing 001/004/005 → 006, existing 007 → 008) in tests/unit/test_discovery.py
- [x] T005 [P] Write unit test for directory creation and prd.md scaffold output in tests/unit/test_discovery.py
- [x] T006 [P] Write unit test for feature.json update in tests/unit/test_discovery.py
- [x] T007 [P] Write unit test for JSON output contract (all fields present, correct types) in tests/unit/test_discovery.py
- [x] T008 Write unit test for slug-hint handling (provided vs. omitted) in tests/unit/test_discovery.py

### Implementation

- [x] T009 Implement sequential numbering logic in bundle/extensions/trasgospec/scripts/bash/discovery.sh — scan specs/[0-9]* directories, extract max numeric prefix, compute next number, zero-pad to 3 digits
- [x] T010 Implement directory creation and prd.md scaffold in bundle/extensions/trasgospec/scripts/bash/discovery.sh — mkdir specs/<NNN-slug>/, write prd.md with section headers per contract
- [x] T011 Implement feature.json update in bundle/extensions/trasgospec/scripts/bash/discovery.sh — write {"feature_directory": "specs/<NNN-slug>"} to .specify/feature.json
- [x] T012 Implement JSON output emission in bundle/extensions/trasgospec/scripts/bash/discovery.sh — emit single-line JSON with spec_dir, spec_number, slug, prd_path, feature_json_updated fields
- [x] T013 Implement slug-hint argument parsing in bundle/extensions/trasgospec/scripts/bash/discovery.sh — accept optional positional arg, derive kebab-case slug, fallback to timestamp if omitted

**Checkpoint**: Script is functional — creates directories, scaffolds prd.md, emits correct JSON. All foundational tests pass.

---

## Phase 3: User Story 1 - Interactive Problem Exploration (Priority: P1) MVP

**Goal**: Users can invoke the discovery command with a rough idea and be guided through an interactive conversation that produces a structured prd.md.

**Independent Test**: Invoke the discovery command with a brief feature idea. Verify (a) the command asks at least one question before producing output, (b) prd.md exists in the correct specs directory, (c) prd.md contains all required sections populated with conversation content.

### Tests

- [x] T014 [P] [US1] Write integration test verifying discovery command invokes the script and creates the spec directory in tests/integration/test_discovery_integration.py
- [x] T015 [P] [US1] Write integration test verifying prd.md scaffold is created with correct section headers in tests/integration/test_discovery_integration.py

### Implementation

- [x] T016 [US1] Implement script invocation and JSON parsing in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — run {SCRIPT} with slug hint derived from user input, parse JSON output for spec_dir and prd_path
- [x] T017 [US1] Implement adaptive topic exploration logic in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — analyze user input for existing coverage, identify least-covered topic, ask targeted question about it
- [x] T018 [US1] Implement topic coverage tracking in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — maintain internal checklist of required sections (pain_point, who, current_alternatives, desired_outcome, user_stories, assumptions) with empty/partial/complete status
- [x] T019 [US1] Implement criteria-based completion detection in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — when all required sections reach complete status, nudge user that PRD is complete but allow continued refinement
- [x] T020 [US1] Implement incremental persistence in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — after each topic reaches sufficient coverage, ask user if they want to save progress; write current state to prd.md on confirmation
- [x] T021 [US1] Implement session finalization in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — when user says "done", write final prd.md with all sections populated from conversation content
- [x] T022 [US1] Implement abort handling in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — if user aborts mid-session, exit gracefully without creating artifacts (or clean up partial artifacts)

**Checkpoint**: User Story 1 is fully functional. Users can run `/speckit-trasgospec-discovery`, have an interactive conversation, and get a complete prd.md.

---

## Phase 4: User Story 2 - Challenging Vague Statements (Priority: P2)

**Goal**: The command detects vague or hand-wavy answers and pushes back with targeted follow-up questions.

**Independent Test**: Provide deliberately vague answers during a discovery session. Verify the command responds with follow-ups requesting specifics rather than moving to the next topic.

### Tests

- [x] T023 [P] [US2] Write unit test verifying vague audience statements trigger follow-up (e.g., "everyone" → "who specifically?") in tests/unit/test_discovery.py
- [x] T024 [P] [US2] Write unit test verifying unmeasurable outcomes trigger follow-up (e.g., "better" → "what does better mean?") in tests/unit/test_discovery.py

### Implementation

- [x] T025 [US2] Implement vagueness detection logic in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — detect non-specific audiences, unmeasurable outcomes, undefined scope, missing specifics
- [x] T026 [US2] Implement targeted follow-up generation in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — for each vague statement type, generate a follow-up question requesting specifics before accepting the answer
- [x] T027 [US2] Implement contradiction detection in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — surface contradictory answers and ask user to resolve before proceeding

**Checkpoint**: Vagueness challenging works. Vague answers get follow-ups; specific answers are accepted.

---

## Phase 5: User Story 4 - PRD as Specify Input (Priority: P2)

**Goal**: The prd.md produced by discovery can be passed to `/speckit-specify` as enriched input for higher-quality spec generation.

**Independent Test**: Generate a PRD via discovery, pass its path to `/speckit-specify`, verify the resulting spec reflects PRD content with fewer NEEDS CLARIFICATION markers.

### Tests

- [x] T028 [P] [US4] Write integration test verifying prd.md structure is valid markdown parseable by downstream tools in tests/integration/test_discovery_integration.py
- [x] T029 [P] [US4] Write integration test verifying prd.md contains all required sections with non-empty content in tests/integration/test_discovery_integration.py

### Implementation

- [x] T030 [US4] Validate prd.md output format in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — ensure final prd.md follows the exact structure defined in the contract (PRD scaffold with populated content)
- [x] T031 [US4] Add completion report with specify handoff instructions in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — display prd.md path and suggest `/speckit-specify <prd-path>` as next step

**Checkpoint**: PRD-to-specify handoff works. Generated prd.md is valid input for `/speckit-specify`.

---

## Phase 6: User Story 3 - Web Research Enrichment (Priority: P3)

**Goal**: Users can opt into web research to enrich the discovery conversation with external findings.

**Independent Test**: Invoke discovery with web research enabled. Verify the final PRD references external findings in the Research Findings section.

### Tests

- [x] T032 [P] [US3] Write unit test verifying web research is not attempted when not enabled in tests/unit/test_discovery.py
- [x] T033 [P] [US3] Write integration test verifying Research Findings section is populated when web research is enabled in tests/integration/test_discovery_integration.py

### Implementation

- [x] T034 [US3] Implement web research opt-in detection in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — detect --research flag or user opt-in during conversation
- [x] T035 [US3] Implement /research skill invocation in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — invoke /research at natural conversation points (current alternatives, desired outcomes) and weave findings into conversation
- [x] T036 [US3] Implement Research Findings section population in bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md — persist research results in the Research Findings section of prd.md; omit section entirely when web research was not used

**Checkpoint**: Web research enrichment works. Research findings appear in PRD when enabled; absent when not.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T037 [P] Update bundle/extensions/trasgospec/extension.yml version to reflect new command addition
- [x] T038 Run quickstart.md validation scenarios end-to-end in specs/007-conversational-discovery/quickstart.md
- [x] T039 Verify bundle validates with `specify bundle validate --path bundle --offline`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1) can start after Foundational
  - US2 (P2) can start after US1 (builds on conversation loop)
  - US4 (P2) can start after US1 (needs prd.md output to validate)
  - US3 (P3) can start after US1 (enrichment layer on top of core loop)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 — vagueness challenging is an enhancement to the conversation loop
- **User Story 4 (P2)**: Depends on US1 — needs a working prd.md to validate handoff
- **User Story 3 (P3)**: Depends on US1 — web research enriches the existing conversation flow

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Script logic before command file logic
- Core behavior before edge case handling

### Parallel Opportunities

- T004, T005, T006, T007 can run in parallel (independent test cases)
- T014, T015 can run in parallel (independent integration tests)
- T023, T024 can run in parallel (independent vagueness test cases)
- T028, T029 can run in parallel (independent format validation tests)
- T032, T033 can run in parallel (independent research tests)
- US2, US4, and US3 can potentially start in parallel after US1, but US2 and US3 modify the same command file

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tests together:
Task: "Unit test for sequential numbering" (T004)
Task: "Unit test for directory creation" (T005)
Task: "Unit test for feature.json update" (T006)
Task: "Unit test for JSON output contract" (T007)
```

## Parallel Example: User Story 1

```bash
# Launch integration tests together:
Task: "Integration test for script invocation" (T014)
Task: "Integration test for prd.md scaffold" (T015)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T013) — script must work
3. Complete Phase 3: User Story 1 (T014-T022) — core conversation loop
4. **STOP and VALIDATE**: Run `/speckit-trasgospec-discovery` with a test idea
5. Verify prd.md is created with all sections populated

### Incremental Delivery

1. Setup + Foundational → Script works, directories created
2. Add US1 → Interactive conversation produces prd.md (MVP!)
3. Add US2 → Vague answers get challenged
4. Add US4 → PRD handoff to specify validated
5. Add US3 → Web research enrichment available
6. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution Principle VI requires TDD: tests first, fail, then implement
- Command file is the bulk of the work — all conversational AI logic lives there
- Script is small and focused — ~100 lines of bash for directory/numbering/scaffold
