# Quickstart: Discovery Command Hooks

**Feature**: 010-discovery-hooks | **Date**: 2026-08-09

## Prerequisites

- Trasgo Spec Kit bundle installed (`.specify/extensions/trasgospec/` exists)
- Python venv set up (`.venv/` exists with pytest)
- On the `010-discovery-hooks` branch

## Validation Scenarios

### 1. Unit Tests Pass

```bash
.venv/bin/pytest tests/unit/test_discovery_hooks.py -v
.venv/bin/pytest tests/unit/test_hook_registration.py -v
```

**Expected**: All tests green. Tests verify:
- Command file contains "Pre-Execution Checks" section
- Command file contains "Mandatory Post-Execution Hooks" section
- Command file references `hooks.before_discovery` and `hooks.after_discovery`
- Post-hooks block contains abort guard
- extensions.yml has `before_discovery` and `after_discovery` entries
- Hook counts are correct

### 2. Bundle Validates

```bash
specify bundle validate --path bundle --offline
```

**Expected**: Validation passes with no errors.

### 3. extensions.yml Parses Correctly

```bash
python3 -c "import yaml; d=yaml.safe_load(open('.specify/extensions.yml')); print('before_discovery:', 'before_discovery' in d.get('hooks',{})); print('after_discovery:', 'after_discovery' in d.get('hooks',{}))"
```

**Expected**: Both print `True`.

### 4. Hook Keys Present in Command File

```bash
grep -c 'before_discovery\|after_discovery' bundle/extensions/trasgospec/commands/speckit.trasgospec.discovery.md
```

**Expected**: At least 2 matches.

### 5. Functional Smoke Test

On a feature branch, run:

```
/speckit-trasgospec-discovery test-feature
```

**Expected**: The flow-gate hook fires before the discovery conversation begins. Observe the "Automatic Pre-Hook: trasgospec" block in the output.

### 6. Abort Path (No Post-Hooks)

Start a discovery session and abort before writing prd.md.

**Expected**: No `after_discovery` hooks are dispatched. The session ends cleanly without status transitions.

### 7. Completion Path (Post-Hooks Fire)

Complete a discovery session that writes prd.md.

**Expected**: After prd.md is written, the `after_discovery` hooks dispatch:
- Mandatory: `speckit.trasgospec.status` fires (Discovery to Opportunity transition)
- Optional: `speckit.trasgospec.flow-nudge` is presented to the user
