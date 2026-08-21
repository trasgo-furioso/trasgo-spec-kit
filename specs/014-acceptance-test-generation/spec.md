# Feature Specification: Acceptance Test Generation

**Feature Branch**: `014-acceptance-test-generation`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "AI agent that converts acceptance criteria in spec.md files into Playwright E2E tests following Given=Arrange, When=Act, Then=Assert pattern. Analyzes the frontend implementation and creates user-perspective tests using Page Object Model and accessibility-first selectors. Generates the acceptance tests for implementation phases that tell the implementer agent when to stop."

## Problem Statement

**Pain Point**: Acceptance scenarios in spec.md are written in natural language (Given/When/Then) but remain purely documentary. There is no automated bridge between the specification and executable tests. Developers must manually interpret each scenario, decide on selectors, build page objects, and write Playwright code -- a tedious, error-prone translation that is frequently skipped or done inconsistently. When specs change, tests drift out of sync with no mechanism to detect or reconcile the gap.

**Who**: Developers and AI agents using trasgospec for spec-driven development who build user-facing web applications. Both implementer agents (who execute `/speckit-implement`) and human developers who want a concrete "definition of done" before writing production code.

**Current Alternatives**: Manual test writing from scratch. Some teams copy-paste acceptance scenarios into test comments and write code around them, but this is ad-hoc, unstructured, and has no tooling support. No existing Spec Kit command bridges the spec-to-test gap.

**Desired Outcome**: A single command (`/speckit-trasgospec-acceptance-tests`) that reads the active spec's acceptance scenarios, analyzes the project's frontend stack, and generates production-ready Playwright E2E test files with Page Object Model pattern. Each test traces back to a specific user story and scenario number. When all generated tests pass, the implementation is complete -- the tests ARE the definition of done.

## User Scenarios & Testing

### User Story 1 - Core Test Generation from Acceptance Scenarios (Priority: P1)

A developer has a spec.md with user stories containing Given/When/Then acceptance scenarios. They run `/speckit-trasgospec-acceptance-tests`. The agent reads the active feature's spec.md via `.specify/feature.json`, parses all acceptance scenarios, analyzes the project's frontend code to understand the framework (React, Vue, Svelte, Next.js, vanilla JS, etc.), component structure, and routing, then generates TypeScript Playwright test files organized by user story. Each test file uses the Page Object Model pattern with composition (not inheritance), accessibility-first selectors (`getByRole`, `getByLabel`, `data-testid`), and custom fixtures via `test.extend`.

**Why this priority**: This is the entire value proposition. Without parsing scenarios and generating tests, nothing else matters. The framework detection determines whether generated page objects are correct and usable.

**Independent Test**: Create a spec.md with two user stories (3 scenarios each), a minimal React project with routes and components, run the command, and verify that test files are generated with correct structure, one `describe` block per user story, one `test` per scenario, and page objects that reference actual components.

**Acceptance Scenarios**:

1. **Given** an active feature with a spec.md containing 3 user stories with 2 acceptance scenarios each, **When** the developer runs `/speckit-trasgospec-acceptance-tests`, **Then** the agent generates one test file per user story (3 files) in the project's e2e test directory, each containing 2 tests mapped to the scenarios
2. **Given** a spec.md with acceptance scenarios in `**Given** ... **When** ... **Then** ...` format, **When** the agent parses the spec, **Then** each scenario is mapped to Arrange (Given), Act (When), Assert (Then) sections within the test body with clear inline comments marking each section
3. **Given** a React project with component files in `src/components/` and routes in `src/app/`, **When** the agent analyzes the frontend, **Then** generated page objects reference actual route paths and use selectors that match the component structure (e.g., `getByRole('button', { name: 'Submit' })` for a button the component renders)
4. **Given** a Vue project with `.vue` single-file components and Vue Router, **When** the agent analyzes the frontend, **Then** generated page objects adapt navigation methods to match Vue Router paths and use selectors appropriate for the Vue template structure
5. **Given** a project with no identifiable frontend framework (e.g., static HTML or server-rendered pages), **When** the agent analyzes the project, **Then** it generates page objects using generic selectors (`getByRole`, `getByText`, `data-testid`) without framework-specific assumptions and warns the developer that selectors may need manual tuning
6. **Given** a spec.md with acceptance scenarios, **When** tests are generated, **Then** each page object class uses composition over inheritance -- page objects are standalone classes composed via fixture injection, not extended from a `BasePage` class

---

### User Story 2 - Traceability Between Tests and Spec Scenarios (Priority: P2)

Each generated test is traceable to its source acceptance scenario. Test names include the user story number and scenario number. Each test file has a header comment referencing the spec.md path and user story title. This allows developers and reviewers to navigate from a failing test directly to the requirement it validates.

**Why this priority**: Without traceability, generated tests are just code -- they lose the connection to the specification that gives them authority as "definition of done." This is what makes the tests more than a test suite; it makes them the executable spec.

**Independent Test**: Generate tests from a spec with known user stories and scenarios, then verify that every test name contains the story and scenario identifiers and that file headers reference the spec.

**Acceptance Scenarios**:

1. **Given** a spec.md with "User Story 3 - Cart Checkout Flow" containing scenario 2, **When** tests are generated, **Then** the test is named following the pattern `US3-S2: <scenario description>` (e.g., `test('US3-S2: shows order confirmation after successful payment', ...)`)
2. **Given** generated test files, **When** the developer reads the file header, **Then** it contains a comment block with the spec.md relative path, user story title, and generation timestamp
3. **Given** a spec.md with 5 user stories, **When** tests are generated, **Then** each test file is named after the user story slug (e.g., `us1-cart-checkout-flow.spec.ts`) for easy discovery
4. **Given** a generated test file, **When** the developer reads any individual test, **Then** the Given/When/Then scenario text from the spec appears as a block comment immediately before the test function

---

### User Story 3 - Existing Project Detection and Integration (Priority: P2)

The agent detects whether Playwright is already configured in the project and adapts accordingly. If `playwright.config.ts` exists, the agent reads it to determine the test directory, base URL, and project settings. If existing page objects or test utilities exist, the agent reuses them rather than creating duplicates. If Playwright is not configured, the agent warns the developer and generates test files anyway with setup instructions.

**Why this priority**: Real projects are not greenfield. The agent must integrate into existing test infrastructure without overwriting or conflicting. This is what makes the command usable in practice rather than just in demos.

**Independent Test**: Set up a project with an existing `playwright.config.ts` that uses `tests/e2e/` as the test directory and has existing page objects in `tests/e2e/pages/`. Run the command and verify tests are generated in the correct directory and reuse existing page objects where applicable.

**Acceptance Scenarios**:

1. **Given** a project with `playwright.config.ts` that sets `testDir: './tests/e2e'`, **When** the agent generates tests, **Then** test files are written to `tests/e2e/` (not the default `e2e/`) and page objects to `tests/e2e/pages/`
2. **Given** a project with an existing `LoginPage` page object in `tests/e2e/pages/login.page.ts`, **When** the agent generates tests that involve login, **Then** it imports and uses the existing `LoginPage` rather than creating a new one
3. **Given** a project with existing Playwright fixtures in `tests/e2e/fixtures.ts`, **When** the agent generates tests, **Then** it extends the existing fixtures rather than creating a parallel fixture file
4. **Given** a project with no `playwright.config.ts` and no Playwright in `package.json`, **When** the agent runs, **Then** it warns the developer that Playwright is not installed, outputs the installation command (`npm init playwright@latest`), and generates test files anyway with a note that they require Playwright setup to run
5. **Given** a project with `playwright.config.ts` that defines multiple `projects` (e.g., chromium, firefox, mobile), **When** the agent generates tests, **Then** it does not modify the projects configuration and generates tests that are project-agnostic (no browser-specific logic)

---

### User Story 4 - Test Update on Spec Change (Priority: P3)

When the spec.md is updated (scenarios added, modified, or removed), the developer re-runs `/speckit-trasgospec-acceptance-tests`. The agent detects existing test files from a previous generation, compares the current spec scenarios against them, and performs an incremental update: adds tests for new scenarios, updates test names and comments for modified scenarios, and marks removed scenarios with a `test.skip` annotation and a comment explaining the scenario was removed from the spec. Page objects are updated only when new pages or interactions are introduced.

**Why this priority**: Specs evolve. Without update support, developers must delete and regenerate all tests, losing any manual customizations they added. Incremental updates preserve manual work while keeping tests in sync with the spec.

**Independent Test**: Generate tests from a 3-scenario spec, then modify the spec (add 1 scenario, remove 1, change wording of 1), re-run the command, and verify the test file reflects all three changes correctly.

**Acceptance Scenarios**:

1. **Given** existing generated tests for user story 1 with scenarios 1-3, **When** the spec is updated to add scenario 4 to user story 1 and the developer re-runs the command, **Then** a new test for scenario 4 is added to the existing test file without modifying tests for scenarios 1-3
2. **Given** existing generated tests with a scenario that was removed from the spec, **When** the developer re-runs the command, **Then** the orphaned test is annotated with `test.skip` and a comment `// Scenario removed from spec on YYYY-MM-DD` rather than deleted
3. **Given** existing generated tests where a scenario's Given/When/Then wording changed, **When** the developer re-runs the command, **Then** the test's comment block is updated to reflect the new wording, but the test implementation is preserved (the developer manually adjusts the code if needed)
4. **Given** existing generated tests with manual customizations (additional assertions, helper calls, setup logic), **When** the developer re-runs the command after a spec change, **Then** the manual customizations are preserved in tests that were not affected by the spec change

---

### Edge Cases

- What happens when the spec.md has no acceptance scenarios? The agent warns that no Given/When/Then scenarios were found, suggests the developer add acceptance scenarios using `/speckit-clarify`, and exits without generating files.
- What happens when acceptance scenarios are ambiguous or malformed (e.g., missing the When clause, or Given/When/Then not in bold)? The agent attempts best-effort parsing, warns about each malformed scenario with its line number, and generates tests only for well-formed scenarios.
- What happens when the frontend code does not exist yet (tests-first approach)? The agent generates test files with page objects based on the scenario descriptions using placeholder selectors (commented `data-testid` attributes). A header comment explains that page objects use inferred selectors that must be updated once components are implemented.
- What happens when there are many user stories with many scenarios (e.g., 10 stories, 50 scenarios)? The agent processes all of them, generating one file per user story. It displays a progress summary after each user story is processed.
- What happens when the e2e test directory already has non-generated test files? The agent never modifies files it did not generate. It identifies its own files by the traceability header comment block.
- What happens when the project uses a monorepo with multiple frontend apps? The agent asks the developer which app to target if it detects multiple `package.json` files with frontend dependencies.
- What happens when Playwright is installed but the config uses JavaScript instead of TypeScript? The agent detects the config file extension (`.ts` vs `.js`) and generates test files in the same language.

## Requirements

### Functional Requirements

**Spec Parsing**

- **FR-001**: System MUST read the active feature's spec.md path from `.specify/feature.json` and parse all acceptance scenarios from the file
- **FR-002**: System MUST parse scenarios in the `**Given** ... **When** ... **Then** ...` format used in trasgospec specs, supporting both inline and multi-line variants
- **FR-003**: System MUST associate each parsed scenario with its parent user story (number, title, and priority)
- **FR-004**: System MUST warn and skip malformed scenarios (missing clauses, unparseable format) without failing the entire generation

**Frontend Analysis**

- **FR-005**: System MUST detect the frontend framework by analyzing `package.json` dependencies, config files (e.g., `next.config.js`, `vite.config.ts`, `nuxt.config.ts`), and file extensions (`.vue`, `.svelte`, `.tsx`)
- **FR-006**: System MUST analyze the project's component structure, routing configuration, and existing patterns to inform page object generation
- **FR-007**: System MUST operate without a detected framework, falling back to generic HTML/accessibility selectors

**Test Generation**

- **FR-008**: System MUST generate TypeScript Playwright test files unless the existing config uses JavaScript
- **FR-009**: System MUST organize tests as one file per user story, with one `test()` per acceptance scenario
- **FR-010**: System MUST generate Page Object Model classes using composition (standalone classes injected via fixtures), not inheritance
- **FR-011**: System MUST use accessibility-first selectors in page objects: `getByRole`, `getByLabel`, `getByText` preferred over CSS selectors; `data-testid` as fallback
- **FR-012**: System MUST generate custom fixtures via `test.extend<>()` that inject page objects into tests
- **FR-013**: System MUST NOT use hardcoded waits (`page.waitForTimeout`), brittle CSS selectors (`.class > div:nth-child(2)`), or create test interdependencies (shared mutable state between tests)
- **FR-014**: System MUST structure each test body with clearly commented Arrange (Given), Act (When), and Assert (Then) sections

**Traceability**

- **FR-015**: System MUST name each test with the pattern `US{N}-S{M}: <scenario description>`
- **FR-016**: System MUST include a header comment block in each generated file with: spec.md path, user story title, generation timestamp, and a marker identifying the file as agent-generated
- **FR-017**: System MUST include the full Given/When/Then text as a block comment before each test function

**Integration**

- **FR-018**: System MUST detect `playwright.config.ts` (or `.js`) and read `testDir`, `baseURL`, and `projects` settings to determine output paths
- **FR-019**: System MUST detect and reuse existing page objects and fixtures rather than creating duplicates
- **FR-020**: System MUST NOT modify files it did not generate (identified by the traceability header marker)
- **FR-021**: When Playwright is not installed, the system MUST warn, provide the installation command, and still generate test files

**Incremental Updates**

- **FR-022**: System MUST detect previously generated test files by their traceability header marker
- **FR-023**: System MUST add tests for new scenarios, update comments for modified scenarios, and annotate removed scenarios with `test.skip` rather than deleting them
- **FR-024**: System MUST preserve manual customizations in tests unaffected by spec changes

**Constitution Compliance**

- **FR-025**: This command is an AI-agent-only command (no bash script), following the precedent of `speckit.trasgospec.hello`. The command file contains YAML frontmatter (description only, no `scripts` key) and markdown body with agent instructions
- **FR-026**: System MUST use the template resolution stack for the generated test file structure: check `.specify/templates/overrides/acceptance-test-template` first, then preset templates (`bundle/presets/trasgospec/templates/acceptance-test-template`), then fall back to hardcoded defaults. The template defines the output structure (imports, describe blocks, fixture setup pattern) and can be overridden by users per Principle VII
- **FR-027**: System MUST NOT register any hooks -- this is a manually invoked command, not a lifecycle hook

### Key Entities

- **Acceptance Scenario**: A single Given/When/Then test case extracted from a user story in spec.md. The atomic unit of generation.
- **Page Object**: A TypeScript class representing a page or component surface. Uses composition via fixture injection. Contains locator methods and action methods.
- **Fixture File**: A TypeScript file using `test.extend<>()` to inject page objects into the test context. One fixture file per test suite or shared across the project.
- **Traceability Header**: A block comment at the top of each generated file that identifies it as agent-generated and maps it to the source spec.
- **Test File**: A `.spec.ts` file containing one `describe` block per user story and one `test` per acceptance scenario.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of well-formed acceptance scenarios in spec.md are represented as individual Playwright tests in the generated output -- no scenario is silently dropped
- **SC-002**: Every generated test name contains the user story and scenario identifiers (e.g., `US1-S2`) enabling bidirectional navigation between spec and test
- **SC-003**: Generated tests compile without errors when Playwright and TypeScript are properly configured in the project
- **SC-004**: Generated page objects use zero CSS selectors -- 100% accessibility-first selectors (`getByRole`, `getByLabel`, `getByText`) or `data-testid` attributes
- **SC-005**: Re-running the command on an unchanged spec produces no file modifications (idempotent generation)
- **SC-006**: Re-running the command after a spec change only modifies tests affected by the change -- unaffected tests remain byte-identical
- **SC-007**: Generated tests contain zero instances of `page.waitForTimeout` or `page.waitFor(N)` hardcoded waits

## Assumptions

- The project uses `npm` or compatible package manager (`yarn`, `pnpm`) with a `package.json` at the project root or app root
- Acceptance scenarios in spec.md follow the `**Given** ... **When** ... **Then** ...` bold-keyword format established in existing trasgospec specs
- The active feature is identified via `.specify/feature.json` (same mechanism used by all other trasgospec commands)
- Playwright is the target test framework -- the command does not generate tests for Cypress, Selenium, or other E2E frameworks
- TypeScript is the default language for generated tests; JavaScript is used only when the existing Playwright config is `.js`
- The developer may run this command before implementing the frontend (tests-first) -- generated page objects will use inferred selectors
- Page objects do not extend a base class; composition via `test.extend` fixtures is the canonical pattern
- The command is manually invoked (not a lifecycle hook) -- it is not part of the automatic `before_*`/`after_*` hook chain
- The command does not install Playwright or any dependencies -- it only generates files
- The `e2e/` directory is the default test output path when no Playwright config exists
