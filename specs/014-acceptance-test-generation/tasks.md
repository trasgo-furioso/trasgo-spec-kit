# Tasks: Acceptance Test Generation

**Input**: Design documents from `specs/014-acceptance-test-generation/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not applicable — this is an AI-only bundle command (no executable code to unit test). Validation via manual invocation and quickstart scenarios.

**Organization**: Tasks are grouped by user story. Each story extends the command file with new capabilities. The command file is the sole implementation artifact.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Register the command and create preset templates

- [x] T001 Register `speckit.trasgospec.acceptance-tests` command in `bundle/extensions/trasgospec/extension.yml` with name, file path, description, and alias `trasgospec.acceptance-tests` per the contract in `specs/014-acceptance-test-generation/contracts/command-file.md`
- [x] T002 [P] Create `acceptance-test-template.md` in `bundle/presets/trasgospec/templates/` defining the generated test file skeleton with `@generated` sentinel, `test.describe`/`test()` structure, `test.step()` GWT blocks, and all placeholder fields per the contract in `specs/014-acceptance-test-generation/contracts/acceptance-test-template.md`
- [x] T003 [P] Create `testing-surface-contract.md` in `bundle/presets/trasgospec/templates/` defining the Parts/States/Actions tables, Provider/Consumer Obligations sections, and parsing rules per the contract in `specs/014-acceptance-test-generation/contracts/testing-surface-contract-template.md`

**Checkpoint**: Templates exist and command is registered. Bundle validates with `specify bundle validate --path bundle --offline`.

---

## Phase 2: User Story 1 - Core Test Generation (Priority: P1) MVP

**Goal**: Parse spec.md acceptance scenarios, detect the frontend framework, and generate Playwright test files with Page Object Model composition and accessibility-first selectors.

**Independent Test**: Create a spec.md with 2 user stories (3 scenarios each) and a minimal React project. Run the command. Verify 2 test files generated (one per story), each with 3 tests, page objects using `getByRole`/`getByLabel`, fixtures via `test.extend`, and `test.step()` for GWT.

### Implementation for User Story 1

- [x] T004 [US1] Write the command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` with YAML frontmatter (`description` only, no `scripts` key) and the following markdown body sections:
  - **User Input**: `$ARGUMENTS` block
  - **Goal**: one-paragraph summary
  - **Outline Step 1**: Read `.specify/feature.json` to locate the active spec.md (FR-001)
  - **Outline Step 2**: Parse spec.md for acceptance scenarios — extract `**Given**`/`**When**`/`**Then**` format, associate with parent user story number/title/priority, warn and skip malformed scenarios (FR-002, FR-003, FR-004)
  - **Outline Step 3**: Detect project context — analyze `package.json` dependencies, config files (`next.config.js`, `vite.config.ts`, `nuxt.config.ts`), and file extensions (`.vue`, `.svelte`, `.tsx`) to identify framework; analyze component structure and routing; fall back to generic selectors if no framework detected (FR-005, FR-006, FR-007)
  - **Outline Step 4**: Resolve `acceptance-test-template` via template resolution stack — check `.specify/templates/overrides/` first, then preset, then hardcoded default (FR-026)
  - **Outline Step 5**: Generate test files — one `.spec.ts` per user story with one `test()` per scenario; generate Page Object classes using composition via `test.extend<>()` fixtures; use accessibility-first selectors (`getByRole` > `getByLabel` > `getByText` > `getByTestId`); structure test bodies with `test.step()` for GWT; no hardcoded waits, no CSS selectors, no test interdependencies (FR-008 through FR-014)
  - **Outline Step 6**: Determine output paths — default to `e2e/`, page objects in `e2e/pages/`, fixtures in `e2e/fixtures.ts`
  - **Outline Step 7**: Display summary of generated files
  - **Done When**: checklist of completion criteria for US1

**Checkpoint**: Command generates correct test files from a spec with acceptance scenarios. Each file has page objects, fixtures, and `test.step()` GWT structure.

---

## Phase 3: User Story 2 - Traceability (Priority: P2)

**Goal**: Every generated test traces back to its source acceptance scenario with structured naming, header comments, and GWT block comments.

**Independent Test**: Generate tests from a spec with known stories/scenarios. Verify test names match `US{N}-S{M}: description` pattern, file headers contain spec path and story title, and each test has a GWT block comment.

### Implementation for User Story 2

- [x] T005 [US2] Extend the command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` to add traceability instructions:
  - Test naming convention: `US{N}-S{M}: <scenario description>` (FR-015)
  - Traceability header in each generated file: `@generated by speckit.trasgospec.acceptance-tests` sentinel, `@spec` path, `@story` reference, `@generated-at` timestamp, per the format in `specs/014-acceptance-test-generation/research.md` (FR-016)
  - Full GWT scenario text as a block comment immediately before each `test()` function (FR-017)
  - File naming: `us{N}-{story-slug}.spec.ts` (e.g., `us1-core-test-generation.spec.ts`)

**Checkpoint**: All generated tests have traceable names, header blocks, and scenario comments.

---

## Phase 4: User Story 3 - Existing Project Detection (Priority: P2)

**Goal**: Detect and integrate with existing Playwright configuration, page objects, and fixtures instead of overwriting or duplicating.

**Independent Test**: Set up a project with `playwright.config.ts` (testDir: `tests/e2e`), existing page objects, and existing fixtures. Run the command. Verify tests are written to `tests/e2e/`, existing POs are reused, and existing fixtures are extended.

### Implementation for User Story 3

- [x] T006 [US3] Extend the command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` to add project detection instructions:
  - Detect `playwright.config.ts` (or `.js`) and read `testDir`, `baseURL`, `projects` settings to determine output paths (FR-018)
  - Scan for existing page objects in `{testDir}/pages/` and reuse them rather than creating duplicates (FR-019)
  - Scan for existing fixtures file and extend it rather than creating a parallel one (FR-019)
  - Never modify files not generated by this command — identify own files by the `@generated` sentinel (FR-020)
  - When Playwright is not installed: warn, provide `npm init playwright@latest` command, generate files anyway with a setup note (FR-021)
  - When config uses `.js` instead of `.ts`: generate JavaScript test files (FR-008)
  - When config defines multiple projects (chromium, firefox, mobile): generate browser-agnostic tests (FR-018)

**Checkpoint**: Command correctly adapts to existing Playwright setups and never overwrites manual files.

---

## Phase 5: User Story 4 - Testing Surface Contract Integration (Priority: P2)

**Goal**: When testing surface contracts exist in the feature's `contracts/` directory, use them as the authoritative source for POM selectors and generate provider-verification tests.

**Independent Test**: Create a `contracts/testing-surface-checkout-form.md` with a Parts table (3 parts). Run the command. Verify POM uses only declared locators and a provider-verification test file is generated.

### Implementation for User Story 4

- [x] T007 [US4] Extend the command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` to add contract integration instructions:
  - Check for `contracts/testing-surface-*.md` files in the active feature directory (FR-029)
  - Parse the `## Parts` Markdown table: extract Part, Locator Strategy, Role, Accessible Name, Test ID, Cardinality per parsing rules in `specs/014-acceptance-test-generation/contracts/testing-surface-contract-template.md` (FR-029)
  - Generate POM classes using only declared locator strategies — do not infer selectors from frontend code when contracts exist (FR-029)
  - Generate a provider-verification test file per contract that asserts each declared part renders with the correct role/name/testId (FR-030)
  - Fall back to frontend code analysis when no contracts exist (FR-031)
  - Respect cardinality in assertions: `exactlyOne` → `toBeVisible()`, `zeroOrOne` → conditional check, `many` → `toHaveCount()` with minimum (FR-032)

**Checkpoint**: Contract-based generation produces POM with declared selectors and provider-verification tests.

---

## Phase 6: User Story 5 - Test Update on Spec Change (Priority: P3)

**Goal**: Detect previously generated test files and perform incremental updates when the spec changes — add new, annotate removed, preserve manual customizations.

**Independent Test**: Generate tests from a 3-scenario spec. Modify the spec (add 1, remove 1, change wording of 1). Re-run. Verify new test added, removed test has `test.skip`, modified test has updated comment, and unaffected tests are preserved.

### Implementation for User Story 5

- [x] T008 [US5] Extend the command file `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` to add incremental update instructions:
  - Detect previously generated files by the `@generated by speckit.trasgospec.acceptance-tests` sentinel in the header block (FR-022)
  - For new scenarios: add new `test()` function to existing file (FR-023)
  - For removed scenarios: annotate with `test.skip` and comment `// Scenario removed from spec on YYYY-MM-DD` — do not delete (FR-023)
  - For modified scenarios (wording changed): update the block comment to reflect new wording, preserve the test implementation body (FR-023)
  - For unaffected tests: preserve byte-identical — no changes (FR-024)
  - For tests with manual customizations: preserve all custom code in unaffected tests (FR-024)
  - Update the `@generated-at` timestamp in the header block
  - If spec is unchanged: produce no file modifications (idempotent, SC-005)

**Checkpoint**: Incremental updates correctly handle add/remove/modify scenarios without losing manual work.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Bundle validation and end-to-end verification

- [x] T009 Validate bundle manifest with `specify bundle validate --path bundle --offline` and fix any issues
- [x] T010 Run quickstart validation scenarios from `specs/014-acceptance-test-generation/quickstart.md` — verify command registration, test generation, traceability, contract integration, and incremental updates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on Setup (T001 for manifest, T002 for template) — this is the MVP
- **US2 (Phase 3)**: Depends on US1 (extends the same command file)
- **US3 (Phase 4)**: Depends on US1 (extends the same command file)
- **US4 (Phase 5)**: Depends on US1 (extends the same command file); T003 for template
- **US5 (Phase 6)**: Depends on US2 (needs traceability header to detect generated files)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends on Setup only — can start after T001, T002
- **US2 (P2)**: Depends on US1 — extends the command file with traceability sections
- **US3 (P2)**: Depends on US1 — extends the command file with detection sections. Can run in parallel with US2.
- **US4 (P2)**: Depends on US1 + T003 — extends the command file with contract sections. Can run in parallel with US2/US3.
- **US5 (P3)**: Depends on US2 — needs traceability header format defined before incremental updates can detect generated files

### Within Each User Story

- All user story tasks modify the same command file
- Each task adds new instruction sections to the command file's Outline
- No parallelism within a story (single file)

### Parallel Opportunities

- T002 and T003 (templates) can run in parallel
- US2, US3, US4 can potentially run in parallel after US1 (different sections of the command file)
- In practice, sequential is safer since all tasks modify the same file

---

## Parallel Example: Setup Phase

```bash
# Launch template creation tasks in parallel:
Task: "Create acceptance-test-template.md in bundle/presets/trasgospec/templates/"
Task: "Create testing-surface-contract.md in bundle/presets/trasgospec/templates/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: US1 Core Test Generation (T004)
3. **STOP and VALIDATE**: Test with a sample spec and React project
4. Command generates working test files — MVP complete

### Incremental Delivery

1. Setup → templates and manifest ready
2. Add US1 → core test generation works → MVP
3. Add US2 → tests are traceable to spec scenarios
4. Add US3 → integrates with existing Playwright projects
5. Add US4 → contract-driven selectors
6. Add US5 → incremental updates preserve manual work
7. Polish → bundle validates, quickstart passes

### Acceptance Gate Per Story

Each user story's implementation phase is complete when its acceptance scenarios (from spec.md) would pass as E2E tests. The command file contains the AI agent instructions that produce the correct output for each story's scenarios.

---

## Notes

- All tasks modify bundle files — no application source code or unit tests
- The command file is a single Markdown document — tasks are sequential additions of instruction sections
- Templates are standalone files that can be created in parallel
- Bundle validation (T009) catches manifest/structural issues before distribution
- Quickstart validation (T010) is the end-to-end acceptance gate
