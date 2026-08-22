---
description: Generate Playwright E2E tests from spec.md acceptance scenarios.
---

## User Input

```text
$ARGUMENTS
```

## Goal

Convert Given/When/Then acceptance scenarios from the active feature's spec.md into production-ready Playwright E2E test files. Generate Page Object Model classes with composition (not inheritance), accessibility-first selectors, and `test.step()` GWT structure. Each generated test traces back to a specific user story and scenario, serving as the "definition of done" for that story's implementation phase.

## Outline

### Step 1: Locate the Active Spec

1. Read `.specify/feature.json` from the repository root to get `feature_directory`.
2. Construct the spec path: `{feature_directory}/spec.md`.
3. If the file does not exist, ERROR: "No spec.md found at `{path}`. Run `/speckit-specify` first."

### Step 2: Parse Acceptance Scenarios

1. Read the spec.md file.
2. Scan for user story headings matching the pattern: `### User Story N - Title (Priority: PX)`
   - Extract: story number (N), title, priority (PX).
3. Within each user story section, find the `**Acceptance Scenarios**:` heading.
4. Parse the numbered list under it. Each item follows the pattern:
   ```
   N. **Given** <given_text>, **When** <action_text>, **Then** <expected_text>
   ```
   - Support both inline (single line) and multi-line variants (continued on next line).
   - Extract: scenario number, given text, when text, then text, raw full text.
5. Associate each scenario with its parent user story (number, title, priority).
6. For malformed scenarios (missing `**Given**`, `**When**`, or `**Then**` in bold):
   - Warn: "Malformed scenario at line {N} in story {title}: missing {clause}. Skipping."
   - Skip the malformed scenario but continue processing others.
7. If NO well-formed scenarios are found in the entire spec:
   - WARN: "No Given/When/Then acceptance scenarios found in spec.md."
   - Suggest: "Add acceptance scenarios to your user stories using `/speckit-clarify`."
   - EXIT without generating files.
8. Display a parsing summary:
   ```
   Parsed {N} scenarios from {M} user stories:
     US1 - {title}: {count} scenarios
     US2 - {title}: {count} scenarios
   ```

### Step 3: Check for Testing Surface Contracts

1. Check if `{feature_directory}/contracts/` exists.
2. If it does, scan for files matching `testing-surface-*.md`.
3. For each contract file found:
   a. Parse the `## Parts` section as a Markdown table.
   b. For each row (skipping header and separator):
      - Extract: Part name, Locator Strategy, Role, Accessible Name, Test ID, Cardinality.
      - Cells with `--`, `—`, or empty values are null.
   c. Validate: every part MUST have at least one non-null locator (Role+Name, or Test ID).
   d. Store the parsed parts indexed by component name (from the file name slug).
4. If contracts are found, display:
   ```
   Found {N} testing surface contract(s):
     {component}: {count} parts
   ```
5. If no contracts directory or no matching files, proceed silently — selectors will be inferred from frontend code (Step 4).

### Step 4: Detect Project Context

1. **Playwright configuration**:
   - Look for `playwright.config.ts` or `playwright.config.js` in the project root.
   - If found, read it and extract:
     - `testDir` (default: `e2e` if not specified)
     - `baseURL` (if set)
     - `projects` (note browser configurations but do not modify)
   - Note the file extension (`.ts` vs `.js`) to determine output language.
   - If NOT found:
     - Check `package.json` for `@playwright/test` in dependencies/devDependencies.
     - If Playwright is not installed:
       - WARN: "Playwright is not installed. Run `npm init playwright@latest` to set up."
       - Continue generating files with a note that they require Playwright setup.
     - Use default: `testDir = 'e2e'`, language = TypeScript.

2. **Framework detection** (only when NO testing surface contracts exist for a component):
   - Check `package.json` dependencies for: `react`, `next`, `vue`, `nuxt`, `svelte`, `@sveltejs/kit`, `@angular/core`.
   - Check for config files: `next.config.js/ts/mjs`, `vite.config.ts/js`, `nuxt.config.ts`, `svelte.config.js`, `angular.json`.
   - Check for framework-specific file extensions: `.vue`, `.svelte`, `.tsx`, `.jsx`.
   - Set framework to the detected value, or `null` if none detected.

3. **Existing test infrastructure**:
   - Scan `{testDir}/pages/` for existing page object files (`*.page.ts` or `*.page.js`).
   - Scan for existing fixtures: `{testDir}/fixtures.ts` or `{testDir}/fixtures.js`.
   - Record paths for reuse decisions in Step 6.

4. **Monorepo detection**:
   - If multiple `package.json` files with frontend dependencies are detected at different paths:
     - ASK the developer: "Multiple frontend apps detected. Which app should I generate tests for?"
     - List the detected app roots.
     - Wait for response before continuing.

### Step 5: Resolve the Test Template

1. Resolve `acceptance-test-template` through the template resolution stack:
   - Check `.specify/templates/overrides/acceptance-test-template.md` first.
   - Then check `.specify/presets/trasgospec/templates/acceptance-test-template.md`.
   - If neither exists, use the hardcoded defaults described in this command file.
2. The template defines: traceability header format, test file structure, page object structure, fixture structure, anti-patterns to avoid.

### Step 6: Generate Test Files

For each user story with parsed scenarios:

#### 6a. Determine file paths

- Test file: `{testDir}/us{N}-{story-slug}.spec.ts` (e.g., `e2e/us1-core-test-generation.spec.ts`)
- Page objects directory: `{testDir}/pages/`
- Fixtures file: `{testDir}/fixtures.ts`

#### 6b. Check for existing generated files (incremental update)

For each target test file path:
1. If the file exists, read it and check for the `@generated by speckit.trasgospec.acceptance-tests` sentinel on line 2.
2. If the sentinel is present — this is a previously generated file. Perform incremental update:
   - Compare current spec scenarios with existing tests (match by `US{N}-S{M}` pattern in test names).
   - **New scenarios** (in spec but not in file): Add new `test()` functions at the end of the `describe` block.
   - **Removed scenarios** (in file but not in spec): Annotate with `test.skip` and add comment: `// Scenario removed from spec on YYYY-MM-DD`.
   - **Modified scenarios** (wording changed): Update the block comment above the test, but preserve the test implementation body.
   - **Unchanged scenarios**: Preserve byte-identical — make no changes.
   - Update the `@generated-at` timestamp in the header block.
3. If the sentinel is NOT present — this is a manually written file. Do NOT modify it. WARN: "File `{path}` exists but is not agent-generated. Skipping to avoid overwriting manual work."
4. If the file does not exist — create it fresh (Step 6c).
5. If the spec is completely unchanged since last generation (all scenarios match): produce no file modifications.

#### 6c. Generate new test file

For each user story, create a `.spec.ts` file with this structure:

1. **Traceability header** (from template):
   ```typescript
   /**
    * @generated by speckit.trasgospec.acceptance-tests
    * @spec {repo-relative spec path}
    * @story US{N} - {Story Title}
    * @generated-at {ISO 8601 timestamp}
    *
    * DO NOT DELETE this header block. It identifies this file as agent-generated
    * and enables incremental updates when the spec changes.
    */
   ```

2. **Import statement**:
   - If a fixtures file exists or will be generated: `import { test, expect } from './fixtures';`
   - If no fixtures needed: `import { test, expect } from '@playwright/test';`

3. **Describe block**: `test.describe('US{N} - {Story Title}', () => { ... });`

4. **For each scenario**, generate a test function:
   ```typescript
   /**
    * Scenario {M}:
    * Given {given text from spec}
    * When {when text from spec}
    * Then {then text from spec}
    */
   test('US{N}-S{M}: {short scenario description}', async ({ {fixture names} }) => {
     await test.step('Given {given text}', async () => {
       // Arrange: navigate, set up state
       // Use page object methods for navigation and setup
     });

     await test.step('When {when text}', async () => {
       // Act: perform the user action
       // Use page object action methods
     });

     await test.step('Then {then text}', async () => {
       // Assert: verify the expected outcome
       // Use expect() with web-first assertions
     });
   });
   ```

5. **Derive the scenario description** for the test name:
   - Take the Then clause and summarize it to a concise description (under 80 chars).
   - Example: "Given authenticated user, When clicks checkout, Then order confirmation shown" → `US1-S3: shows order confirmation after checkout`

6. **Generate implementation code within test steps**:
   - **If testing surface contracts exist for relevant components**: Use the declared locator strategies from the contract to build page object interactions. Do NOT infer selectors from frontend code.
   - **If no contracts but frontend code exists**: Analyze components and routing to generate selectors using `getByRole`, `getByLabel`, `getByText`, or `getByTestId` as appropriate.
   - **If no contracts and no frontend code (tests-first)**: Generate placeholder implementations with TODO comments:
     ```typescript
     await test.step('Given {text}', async () => {
       // TODO: Implement when frontend components are built
       // Suggested: await page.goto('/expected-route');
     });
     ```

#### 6d. Generate page objects

For each page or component referenced in the scenarios:

1. **If a testing surface contract exists**:
   - Create a page object class with locators derived from the contract's Parts table.
   - Map Locator Strategy to Playwright methods:
     - `role` → `page.getByRole('{role}', { name: '{accessibleName}' })`
     - `label` → `page.getByLabel('{accessibleName}')`
     - `testId` → `page.getByTestId('{testId}')`
   - Add action methods for each Supported Action in the contract.
   - Use composition — the class is standalone, injected via fixtures.

2. **If no contract but frontend code exists**:
   - Analyze the component to identify interactive elements.
   - Use accessibility-first selector hierarchy: `getByRole` > `getByLabel` > `getByText` > `getByTestId`.
   - Name methods after user capabilities (e.g., `signIn()`, `addToCart()`), not generic wrappers.

3. **If no contract and no frontend code**:
   - Generate skeleton page objects with placeholder selectors:
     ```typescript
     // TODO: Update selectors when components are implemented
     this.submitButton = page.getByRole('button', { name: 'Submit' });
     ```

4. **Reuse existing page objects**:
   - If `{testDir}/pages/` contains an existing page object that covers the same page/component:
     - Import and use it instead of creating a new one.
     - Display: "Reusing existing page object: `{path}`"

5. **Write to**: `{testDir}/pages/{page-slug}.page.ts` (e.g., `e2e/pages/login.page.ts`)

#### 6e. Generate or extend fixtures

1. **If `{testDir}/fixtures.ts` already exists**:
   - Read it and check if it already exports a `test` object with `extend`.
   - Add new page object fixtures to the existing `extend<>()` type parameter and factory functions.
   - Do NOT create a parallel fixtures file.

2. **If no fixtures file exists**:
   - Create `{testDir}/fixtures.ts` with:
     ```typescript
     import { test as base, expect } from '@playwright/test';
     import { PageName } from './pages/page-slug.page';

     type PageFixtures = {
       pageName: PageName;
     };

     export const test = base.extend<PageFixtures>({
       pageName: async ({ page }, use) => {
         await use(new PageName(page));
       },
     });

     export { expect };
     ```

#### 6f. Generate provider-verification tests (when contracts exist)

For each testing surface contract:

1. Create a verification test file: `{testDir}/contracts/verify-{component-slug}.spec.ts`
2. For each part in the contract, generate an assertion:
   - `exactlyOne` cardinality:
     ```typescript
     test('renders {partName} with correct role and name', async ({ page }) => {
       await page.goto('{route}');
       const locator = page.getByRole('{role}', { name: '{name}' });
       await expect(locator).toBeVisible();
       await expect(locator).toHaveCount(1);
     });
     ```
   - `zeroOrOne` cardinality:
     ```typescript
     test('{partName} renders with correct role when present', async ({ page }) => {
       await page.goto('{route}');
       const locator = page.getByRole('{role}', { name: '{name}' });
       const count = await locator.count();
       if (count > 0) {
         await expect(locator).toBeVisible();
       }
     });
     ```
   - `many` cardinality:
     ```typescript
     test('renders multiple {partName} elements', async ({ page }) => {
       await page.goto('{route}');
       const locator = page.getByRole('{role}', { name: '{name}' });
       await expect(locator).not.toHaveCount(0);
     });
     ```

### Step 7: Display Summary

After all files are generated/updated, display:

```
Acceptance tests generated for {feature_name}:

  Test files:
    {path1} — {count} tests (US{N} - {title})
    {path2} — {count} tests (US{N} - {title})

  Page objects:
    {path1} — {count} locators
    {path2} — {count} locators (reused existing)

  Fixtures:
    {path} — {count} page objects registered

  Contract verification (if applicable):
    {path} — {count} part assertions

  Total: {total_tests} tests across {total_files} files
```

If any scenarios were skipped (malformed), list them:
```
  Skipped (malformed):
    Line {N}: {reason}
```

## Output Rules

### MUST

- Use `test.step()` for Given/When/Then sections (visible in traces and reports)
- Use `getByRole`, `getByLabel`, `getByText` before `getByTestId`
- Use composition via `test.extend<>()` for page object injection
- Include `@generated` sentinel in every generated file header
- Include full GWT scenario text as block comment before each test
- Name tests as `US{N}-S{M}: {description}`
- Name files as `us{N}-{story-slug}.spec.ts`
- Respect cardinality in contract-driven assertions
- Preserve manual customizations in unaffected tests during updates

### MUST NOT

- Use `page.waitForTimeout()` or any hardcoded waits
- Use CSS selectors (`.class`, `#id`, `div > span`)
- Use `extends BasePage` or any inheritance chain
- Use `.nth(N)` for business items (use filter by content)
- Use `await locator.isVisible()` (use `await expect(locator).toBeVisible()`)
- Create shared mutable state between tests
- Modify files without the `@generated` sentinel
- Generate generic wrapper methods (`click(selector)`, `fill(selector, value)`)

## Done When

- [ ] All well-formed acceptance scenarios have corresponding tests
- [ ] Each test file has the traceability header with `@generated` sentinel
- [ ] Page objects use accessibility-first selectors or contract-declared locators
- [ ] Fixtures inject page objects via `test.extend<>()`
- [ ] Test bodies use `test.step()` for GWT sections
- [ ] No hardcoded waits, CSS selectors, or inheritance in generated output
- [ ] Provider-verification tests generated for each testing surface contract (if any)
- [ ] Summary displayed showing all generated files and test counts
