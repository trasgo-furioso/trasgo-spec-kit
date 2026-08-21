# Data Model: Acceptance Test Generation

**Date**: 2026-08-21 | **Feature**: 014-acceptance-test-generation

## Entities

### AcceptanceScenario

The atomic unit parsed from spec.md. One scenario = one generated test.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| storyNumber | number | Parsed from `### User Story N` heading | User story index (1-based) |
| storyTitle | string | Parsed from heading after `N - ` | e.g., "Core Test Generation" |
| storyPriority | string | Parsed from `(Priority: PX)` | P1, P2, P3, etc. |
| scenarioNumber | number | Parsed from numbered list position | Scenario index within story (1-based) |
| given | string | Parsed from `**Given**` to `**When**` | Arrange/precondition text |
| when | string | Parsed from `**When**` to `**Then**` | Act/action text |
| then | string | Parsed from `**Then**` to end of line/item | Assert/expected outcome text |
| rawText | string | Full original line | For traceability comments |
| lineNumber | number | Line in spec.md | For warning messages on malformed scenarios |

**Lifecycle**: Created during spec parsing. Immutable after creation. Used to generate test functions.

### TestFile

One file per user story. Contains the describe block and all tests for that story's scenarios.

| Field | Type | Derived From | Description |
|-------|------|--------------|-------------|
| storyNumber | number | AcceptanceScenario.storyNumber | Which story this file covers |
| storySlug | string | Slugified storyTitle | e.g., "core-test-generation" |
| fileName | string | `us{N}-{slug}.spec.ts` | Output file name |
| outputPath | string | testDir + fileName | Full path in project |
| headerComment | string | Traceability template | `@generated` block with spec path, story, timestamp |
| tests | Test[] | AcceptanceScenarios for this story | Individual test functions |

### Test

One test function per acceptance scenario within a TestFile.

| Field | Type | Derived From | Description |
|-------|------|--------------|-------------|
| name | string | `US{N}-S{M}: {description}` | Test function name |
| givenStep | string | Scenario.given | `test.step('Given ...')` content |
| whenStep | string | Scenario.when | `test.step('When ...')` content |
| thenStep | string | Scenario.then | `test.step('Then ...')` content |
| scenarioComment | string | Scenario.rawText | Block comment before test function |
| status | enum | Comparison with existing | `new`, `unchanged`, `modified`, `removed` |

### PageObject

A TypeScript class representing a page or component's testing surface.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| name | string | Component/page name | e.g., "LoginPage", "CheckoutForm" |
| fileName | string | `{name-slug}.page.ts` | Output file name |
| sourcePage | string | Route path or URL | Navigation target |
| parts | Part[] | Contract or frontend analysis | Locators and actions |
| composedObjects | string[] | Other POs used by this one | For composition imports |

### Part (from Testing Surface Contract)

A single interactive element declared in a contract or inferred from code.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| name | string | Contract Parts table | Logical name (e.g., "placeOrder") |
| locatorStrategy | enum | Contract or inference | `role`, `label`, `testId`, `text` |
| role | string? | Contract or ARIA | ARIA role (e.g., "button") |
| accessibleName | string? | Contract or label | Accessible name or i18n key |
| testId | string? | Contract | `data-testid` value |
| cardinality | enum | Contract | `exactlyOne`, `zeroOrOne`, `many` |

### ProjectContext

Detected project configuration used to determine output paths and code style.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| framework | string? | package.json + config files | "react", "vue", "svelte", "next", "nuxt", null |
| testDir | string | playwright.config or default | e.g., "tests/e2e" or "e2e" |
| baseURL | string? | playwright.config | e.g., "http://localhost:3000" |
| language | enum | playwright.config extension | `typescript` or `javascript` |
| hasPlaywright | boolean | package.json check | Whether Playwright is installed |
| existingPageObjects | string[] | File scan of testDir/pages/ | Paths to existing PO files |
| existingFixtures | string? | File scan for fixtures.ts | Path to existing fixture file |

## Relationships

```
spec.md
  └── has many → AcceptanceScenario (parsed from GWT format)
                   └── grouped by storyNumber → TestFile (one per story)
                                                  └── has many → Test (one per scenario)
                                                  └── uses → PageObject[] (via fixtures)

contracts/testing-surface-*.md
  └── has many → Part (from Parts table)
                  └── used by → PageObject (locators derived from parts)
                  └── verified by → ProviderVerificationTest

ProjectContext
  └── determines → output paths, language, framework-specific PO patterns
  └── discovers → existing PageObjects and Fixtures (for reuse)
```

## State Transitions

### Test Status (during incremental update)

```
[new scenario in spec] → new → generated into test file
[scenario unchanged]   → unchanged → test preserved byte-identical
[scenario wording changed] → modified → comment block updated, implementation preserved
[scenario removed from spec] → removed → test annotated with test.skip
```

### File Generation Decision

```
[no existing file] → CREATE new test file with all scenarios
[existing file, no spec changes] → SKIP (idempotent, no modifications)
[existing file, spec changed] → UPDATE (incremental: add/modify/skip per scenario)
```
