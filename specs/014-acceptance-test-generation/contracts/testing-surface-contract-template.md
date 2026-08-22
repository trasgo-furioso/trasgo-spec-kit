# Contract: Testing Surface Contract Template

## Overview

Defines the structure of the `testing-surface-contract` preset template used by `/speckit-plan` to generate UI testing surface contracts during Phase 1. Each contract declares the parts, roles, test IDs, states, and actions that a UI component exposes for testing.

## File Location

```
bundle/presets/trasgospec/templates/testing-surface-contract.md
```

## Template Structure

```markdown
# Contract: Testing Surface — {COMPONENT_NAME}

**Date**: {DATE} | **Feature**: {FEATURE_ID}

## Overview

Declares the testing surface that the `{COMPONENT_NAME}` component MUST expose
and that Page Object Models MUST use. Both the component implementation and
acceptance tests reference this contract as the single source of truth.

## Parts

| Part | Locator Strategy | Role | Accessible Name | Test ID | Cardinality |
|------|-----------------|------|-----------------|---------|-------------|
| {part_name} | {role / label / testId} | {aria_role} | {accessible_name} | {data_testid} | {exactlyOne / zeroOrOne / many} |

## States

| Part | State | ARIA Attribute | Values |
|------|-------|---------------|--------|
| {part_name} | {state_name} | {aria_attribute} | {possible_values} |

## Supported Actions

| Part | Action | User Gesture |
|------|--------|-------------|
| {part_name} | {action_name} | {gesture_description} |

## Provider Obligations (Component)

- Each part MUST render with the declared `testId` as `data-testid`
- Each role-located part MUST expose the declared ARIA role
- Accessible names MUST resolve via label association, visible text, or `aria-label`
- Removing or renaming a part is a BREAKING change requiring contract version bump

## Consumer Obligations (POM / Acceptance Tests)

- MUST use only declared parts for element location
- MUST NOT use CSS classes, tag names, or DOM structure for selectors
- SHOULD prefer role+name locators; fall back to testId only when documented

## Consumers

- `speckit.trasgospec.acceptance-tests` command (generates POM from Parts table)
- Component developer (implements parts per Provider Obligations)
- Provider-verification tests (assert contract satisfaction at render time)
```

## Placeholder Definitions

| Placeholder | Source | Description |
|-------------|--------|-------------|
| `{COMPONENT_NAME}` | speckit-plan analysis | PascalCase component name (e.g., "CheckoutForm") |
| `{DATE}` | Generation date | ISO date |
| `{FEATURE_ID}` | Feature directory name | e.g., "014-acceptance-test-generation" |
| `{part_name}` | Identified UI element | camelCase logical name (e.g., "placeOrder") |
| `{role / label / testId}` | Selector strategy | Primary locator method for this part |
| `{aria_role}` | ARIA role | e.g., "button", "textbox", "status" |
| `{accessible_name}` | Label/name | i18n key or visible text |
| `{data_testid}` | Test ID attribute | Dot-namespaced (e.g., "checkout.place-order") |
| `{exactlyOne / zeroOrOne / many}` | Cardinality | How many instances expected |

## Parsing Rules (for acceptance-tests command)

The acceptance-tests command parses contracts as follows:

1. Detect files matching `contracts/testing-surface-*.md` in the feature directory
2. Parse the `## Parts` section as a Markdown table
3. For each row, extract: Part, Locator Strategy, Role, Accessible Name, Test ID, Cardinality
4. Skip header row and separator row
5. Cells with `—` or empty values are treated as null/not-applicable
6. Locator Strategy determines which Playwright method to use:
   - `role` → `page.getByRole(role, { name: accessibleName })`
   - `label` → `page.getByLabel(accessibleName)`
   - `testId` → `page.getByTestId(testId)`
   - `role + label` → `page.getByRole(role, { name: accessibleName })` (compound)

## Template Resolution Order

1. `.specify/templates/overrides/testing-surface-contract.md` (user override)
2. `.specify/presets/trasgospec/templates/testing-surface-contract.md` (installed preset)
3. Hardcoded default in the speckit-plan skill (fallback)

## Consumers

- `/speckit-plan` (resolves template during Phase 1 contract generation)
- `speckit.trasgospec.acceptance-tests` (parses generated contracts for POM selectors)
- Component developers (reference contracts during implementation)
- Users (override template via `.specify/templates/overrides/`)

## Validation Rules

- Contract MUST have a `## Parts` section with a valid Markdown table
- Every part MUST have at least one non-null locator (Role, Accessible Name, or Test ID)
- Cardinality MUST be one of: `exactlyOne`, `zeroOrOne`, `many`
- Part names MUST be unique within a contract
- File name MUST follow `testing-surface-{component-slug}.md` pattern
