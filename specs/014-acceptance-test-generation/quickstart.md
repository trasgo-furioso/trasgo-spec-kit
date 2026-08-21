# Quickstart: Acceptance Test Generation

**Date**: 2026-08-21 | **Feature**: 014-acceptance-test-generation

## Prerequisites

- Trasgo Spec Kit bundle installed (`specify bundle install trasgospec`)
- A feature with a spec.md containing acceptance scenarios in GWT format
- (Optional) Testing surface contracts in `contracts/testing-surface-*.md`

## Validation Scenarios

### Scenario 1: Basic Test Generation (US1)

**Setup**: Create a minimal spec with 2 user stories and GWT scenarios.

```bash
# Verify the command is registered
specify extension list --verbose
# Look for: speckit.trasgospec.acceptance-tests
```

**Run**:
```bash
# Invoke the command (via speckit-implement or manually)
/speckit-trasgospec-acceptance-tests
```

**Expected outcome**:
- Test files created in `e2e/` (or configured testDir)
- One `.spec.ts` per user story (e.g., `us1-core-test-generation.spec.ts`)
- Each test uses `test.step()` for Given/When/Then sections
- Page objects in `e2e/pages/` using composition via fixtures
- Fixtures file at `e2e/fixtures.ts` using `test.extend<>()`

### Scenario 2: Traceability Verification (US2)

**Setup**: Same as Scenario 1.

**Verify**:
```bash
# Check traceability header
head -8 e2e/us1-*.spec.ts
# Should show @generated sentinel, @spec path, @story, @generated-at

# Check test names
grep "test(" e2e/us1-*.spec.ts
# Should match pattern: US1-S1: ..., US1-S2: ..., etc.

# Check GWT block comments
grep -B4 "test(" e2e/us1-*.spec.ts
# Should show scenario text as block comment before each test
```

### Scenario 3: Contract-Based Generation (US4)

**Setup**: Create a testing surface contract.

```bash
mkdir -p specs/014-acceptance-test-generation/contracts
# Create contracts/testing-surface-checkout-form.md with Parts table
```

**Run**: Same command invocation.

**Verify**:
- POM uses only declared locator strategies from contract
- Provider-verification test file exists asserting each part
- No selectors inferred from frontend code

### Scenario 4: Incremental Update (US5)

**Setup**: Generate tests, then modify the spec (add a scenario, remove one, change wording of one).

**Run**: Re-invoke the command.

**Verify**:
- New scenario has a new test added
- Removed scenario has `test.skip` with date comment
- Modified scenario has updated comment block, preserved implementation
- Unaffected tests are byte-identical to previous generation

### Scenario 5: No Playwright Installed (Edge Case)

**Setup**: Project without Playwright in `package.json`.

**Run**: Invoke the command.

**Verify**:
- Warning displayed about missing Playwright
- Installation command shown (`npm init playwright@latest`)
- Test files still generated with a note about setup requirement

## Bundle Validation

```bash
# Validate the bundle manifest after adding the new command
specify bundle validate --path bundle --offline

# Verify template resolution
specify preset resolve acceptance-test-template
specify preset resolve testing-surface-contract
```

## File Inventory

After successful implementation, these files should exist in the bundle:

| File | Type | Description |
|------|------|-------------|
| `bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md` | Command | AI agent instructions |
| `bundle/extensions/trasgospec/extension.yml` | Manifest | Updated with new command entry |
| `bundle/presets/trasgospec/templates/acceptance-test-template.md` | Template | Test file output structure |
| `bundle/presets/trasgospec/templates/testing-surface-contract.md` | Template | Selector contract format |
