# Quickstart: Bundle Install Validation

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## Prerequisites

- Spec Kit CLI installed (`specify` command available)
- Python 3.11+ installed
- direnv installed and hooked into shell
- Git installed

## Setup

### 1. Clone and enter the project

```bash
cd trasgospec
```

direnv auto-activates the `.venv` on entry.

### 2. Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Validate the bundle manifest

```bash
specify bundle validate
```

Expected: All checks pass, no errors.

### 4. Build the bundle artifact

```bash
specify bundle build
```

Expected: Produces `trasgospec-0.1.0.zip` in the output directory.

## Validation Scenarios

### Scenario 1: Install from local path (US1)

```bash
# Create a clean test project
mkdir /tmp/test-project && cd /tmp/test-project
specify init --integration claude

# Install from local bundle directory
specify bundle install /path/to/trasgospec

# Verify
specify bundle list
```

Expected: `trasgospec` appears in the list with version `0.1.0`,
component count `1`, and install timestamp.

### Scenario 2: Install from catalog (US1 + US2)

```bash
# Create a clean test project
mkdir /tmp/test-project && cd /tmp/test-project
specify init --integration claude

# Add the self-hosted catalog
specify bundle catalog add \
  https://raw.githubusercontent.com/<owner>/trasgospec/main/catalog.json \
  --policy install-allowed

# Search for the bundle
specify bundle search trasgospec

# Install from catalog
specify bundle install trasgospec

# Verify
specify bundle list
```

Expected: Bundle found in search with `community` trust indicator.
After install, appears in list.

### Scenario 3: Idempotent reinstall (US1)

```bash
# Run install again on the same project
specify bundle install trasgospec

# Verify no duplicates
specify bundle list
```

Expected: No errors, no duplicate components, same list output.

### Scenario 4: Clean removal (US3)

```bash
# Remove the bundle
specify bundle remove trasgospec

# Verify
specify bundle list
```

Expected: `trasgospec` no longer appears in the list.

## Running Integration Tests

```bash
cd trasgospec
pytest tests/integration/ -v
```

Expected: All tests pass. Tests cover US1, US2, and US3 acceptance
scenarios using Given/When/Then → Arrange/Act/Assert.

## Key Files Reference

- Bundle manifest: see [bundle-manifest.md](contracts/bundle-manifest.md)
- Catalog file: see [catalog-file.md](contracts/catalog-file.md)
- Data model: see [data-model.md](data-model.md)
