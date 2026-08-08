# Quickstart: Bundle Install Validation

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## Prerequisites

- Spec Kit CLI installed (`specify` command available)
- Python 3.11+ installed
- direnv installed and hooked into shell
- Git 2.9+ installed

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

### 3. Activate git hooks

```bash
bash scripts/setup.sh
```

Expected: `core.hooksPath` configured to `.githooks`.

### 4. Validate the bundle manifest

```bash
specify bundle validate --path bundle
```

Expected: All checks pass, no errors.

### 5. Build the bundle artifact

```bash
specify bundle build --path bundle --output .
```

Expected: Produces `trasgospec-<version>.zip` in the repository root.

## Validation Scenarios

### Scenario 1: Install from local path (US1)

```bash
# Create a clean test project
mkdir /tmp/test-project && cd /tmp/test-project
specify init --integration claude

# Install from local bundle directory
specify bundle install /path/to/trasgospec/bundle

# Verify
specify bundle list
```

Expected: `trasgospec` appears in the list with version, component
count, and install timestamp.

### Scenario 2: Install from catalog (US1)

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

### Scenario 4: Automated build on push (US2)

```bash
# Make a change to bundle files
echo "# test" >> bundle/README.md
git add bundle/README.md
git commit -m "test: trigger build"

# Push (hook runs automatically)
git push
```

Expected: Hook validates bundle, builds zip, updates catalog.json,
creates a separate "chore: build bundle" commit, push succeeds.

### Scenario 5: No build for non-bundle changes (US3)

```bash
# Make a change outside bundle/
echo "# test" >> README.md
git add README.md
git commit -m "docs: update readme"

# Push (hook skips silently)
git push
```

Expected: No validation, no build, no extra commit. Push proceeds
immediately.

### Scenario 6: Developer hook setup (US4)

```bash
# In a fresh clone
bash scripts/setup.sh

# Verify
git config core.hooksPath
```

Expected: Output is `.githooks`. Running setup.sh again produces
the same result without errors.

### Scenario 7: Version consistency (US5)

```bash
# After a successful build, compare versions
grep 'version:' bundle/bundle.yml
grep '"version"' catalog.json
```

Expected: Both show the same version string.

## Running Tests

```bash
cd trasgospec

# All tests
.venv/bin/pytest tests/ -v

# Unit tests only (hook + setup script)
.venv/bin/pytest tests/unit/ -v

# Integration tests only (bundle install)
.venv/bin/pytest tests/integration/ -v
```

Expected: All tests pass.

## Key Files Reference

- Bundle manifest: see [bundle-manifest.md](contracts/bundle-manifest.md)
- Catalog file: see [catalog-file.md](contracts/catalog-file.md)
- Catalog update contract: see [catalog-update.md](contracts/catalog-update.md)
- Hook exit codes: see [hook-exit-codes.md](contracts/hook-exit-codes.md)
- Data model: see [data-model.md](data-model.md)
