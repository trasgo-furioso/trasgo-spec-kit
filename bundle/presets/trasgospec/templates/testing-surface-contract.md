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

---

## Parsing Rules (for acceptance-tests command)

1. Detect files matching `contracts/testing-surface-*.md` in the feature directory
2. Parse the `## Parts` section as a Markdown table
3. For each row, extract: Part, Locator Strategy, Role, Accessible Name, Test ID, Cardinality
4. Skip header row and separator row
5. Cells with `--` or empty values are treated as null/not-applicable
6. Locator Strategy determines which Playwright method to use:
   - `role` -> `page.getByRole(role, { name: accessibleName })`
   - `label` -> `page.getByLabel(accessibleName)`
   - `testId` -> `page.getByTestId(testId)`
   - `role + label` -> `page.getByRole(role, { name: accessibleName })`
7. Cardinality determines assertion type:
   - `exactlyOne` -> `await expect(locator).toBeVisible()`
   - `zeroOrOne` -> conditional: `if (await locator.count() > 0) { ... }`
   - `many` -> `await expect(locator).toHaveCount(expected, { minimum: true })`
