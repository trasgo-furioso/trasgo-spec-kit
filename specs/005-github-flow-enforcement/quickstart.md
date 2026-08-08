# Quickstart: GitHub Flow Enforcement

## Prerequisites

- Git repository with a `main` branch
- Spec Kit project (`.specify/` directory exists)
- Trasgospec bundle installed
- (Optional) `gh` CLI installed and authenticated

## Validation Scenarios

### 1. Verify flow-context.sh output

```bash
# From repo root, on a feature branch
bash bundle/extensions/trasgospec/scripts/bash/flow-context.sh
```

**Expected**: Single-line JSON with `current_branch`, `is_main`, `spec_dir`, etc. See [flow-context-output.md](contracts/flow-context-output.md) for full schema.

### 2. Verify after_specify creates branch

```bash
# On main
git checkout main

# Run specify
# /speckit-specify "test feature"
```

**Expected**: Specify creates spec.md with `**Feature Branch**: \`005-test-feature\``. The mandatory `after_specify` hook fires, reads the branch name from spec.md, creates branch `005-test-feature`, and switches to it.

### 3. Verify gate blocks on main for other skills

```bash
# Switch to main
git checkout main

# Run a non-specify flow-aware skill
# /speckit-plan
```

**Expected**: The mandatory `before_plan` hook fires. The flow-gate command blocks execution and offers to create/switch to the branch named in spec.md.

### 3b. Verify gate passes on feature branch

```bash
# Switch to correct feature branch
git checkout 005-github-flow-enforcement

# Run any flow-aware skill
# /speckit-plan
```

**Expected**: The hook passes silently and the skill proceeds normally.

### 4. Verify nudge after plan (gh enabled)

```bash
# On a feature branch with plan.md created
# /speckit-plan
```

**Expected**: After plan completes, the optional `after_plan` hook offers to open a draft PR. If accepted and `gh` is available, it runs `gh pr create --draft`.

### 5. Verify nudge after plan (gh disabled)

```bash
# Set gh_integration to false in .specify/extensions.yml
# settings:
#   gh_integration: false
```

```bash
# /speckit-plan
```

**Expected**: After plan completes, the optional hook outputs the PR title, description, and a copy-paste `gh` command. Does not attempt to run `gh`.

### 6. Verify read-only commands unaffected

```bash
# On main branch
git checkout main

# Run read-only commands
# /speckit-trasgospec-roadmap
# /speckit-trasgospec-hello
```

**Expected**: Both commands execute normally with no branch warnings or blocks.

### 7. Verify hook registration

```bash
# Check extensions.yml after bundle install
cat .specify/extensions.yml
```

**Expected**: `hooks` section contains 1 `after_specify` entry + 7 `before_*` entries (flow-gate, mandatory) and 3 `after_*` entries (flow-nudge, optional).

### 8. Run test suite

```bash
.venv/bin/pytest tests/unit/test_flow_context.py tests/unit/test_flow_gate.py tests/unit/test_flow_nudge.py -v
```

**Expected**: All tests pass, validating JSON contracts, branch gating logic, and PR nudge behavior.
