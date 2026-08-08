# Quickstart: Bundle Build CI Validation

## Prerequisites

- Git 2.9+ (for `core.hooksPath` support)
- Spec Kit CLI (`specify`) installed and on PATH
- Python 3.11+ with pytest (for running tests)
- Repository cloned with a GitHub remote

## Setup

### 1. Activate hooks

```bash
./scripts/setup.sh
```

Verify:
```bash
git config core.hooksPath
# Expected: .githooks
```

### 2. Verify hook is executable

```bash
ls -la .githooks/pre-push
# Expected: -rwxr-xr-x ... .githooks/pre-push
```

## Validation Scenarios

### Scenario 1: Bundle change triggers build (US1)

```bash
# Make a trivial bundle change
echo "# test" >> bundle/bundle.yml

# Commit and push
git add bundle/bundle.yml
git commit -m "test: trigger bundle build"
git push origin main
```

**Expected**:
- stderr shows `[bundle-build] Validating bundle...` progress
- A new commit `chore: build bundle vX.Y.Z` appears in log
- `catalog.json` has updated version and raw.githubusercontent.com download URL
- Zip artifact exists at repo root

**Verify**:
```bash
git log --oneline -2
# Should show: chore: build bundle vX.Y.Z
#              test: trigger bundle build

cat catalog.json | grep download_url
# Should contain: raw.githubusercontent.com/.../refs/heads/main/trasgospec-X.Y.Z.zip
```

### Scenario 2: Non-bundle change skips build (US2)

```bash
echo "# test" >> README.md
git add README.md
git commit -m "test: non-bundle change"
git push origin main
```

**Expected**:
- No `[bundle-build]` output on stderr
- No additional commit created
- Push proceeds normally

### Scenario 3: Validation failure blocks push (US1-AS4)

```bash
# Corrupt bundle manifest
echo "invalid: yaml: [" >> bundle/bundle.yml
git add bundle/bundle.yml
git commit -m "test: invalid bundle"
git push origin main
```

**Expected**:
- stderr shows validation errors
- Push is blocked (non-zero exit)
- No zip artifact produced
- No auto-commit created

### Scenario 4: Setup idempotency (US3)

```bash
./scripts/setup.sh
./scripts/setup.sh
git config core.hooksPath
# Expected: .githooks (same result, no errors)
```

### Scenario 5: Catalog version matches manifest (US4)

After a successful build:
```bash
# Extract version from bundle.yml
grep 'version:' bundle/bundle.yml | head -1

# Extract version from catalog.json
grep '"version"' catalog.json
```

**Expected**: Both versions match.

## Running Tests

```bash
.venv/bin/pytest tests/unit/test_pre_push_hook.py -v
.venv/bin/pytest tests/unit/test_setup.py -v
```
