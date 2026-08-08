# Quickstart: Bundle Extension Components

## Prerequisites

- Spec Kit >= 0.15.0 installed
- A clean Spec Kit project (`specify init` completed)
- Access to the trasgo-spec-kit catalog URL

## Validation Scenarios

### 1. Bundle validates before packaging

```bash
cd bundle/
specify bundle validate
```

**Expected**: No errors. The validator confirms `bundle.yml` references valid extensions with matching `extension.yml` manifests.

### 2. Bundle installs with components

```bash
# In a target project (not the bundle repo itself):
specify bundle catalog add https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/refs/heads/main/catalog.json --policy install-allowed
specify bundle install trasgospec
```

**Expected**: Output shows `2 added, 0 already present` (or similar non-zero count).

### 3. Bundle list shows components

```bash
specify bundle list
```

**Expected**: `trasgospec vX.Y.Z (2 components, installed ...)`.

### 4. Hello command works

Invoke `/speckit-trasgospec-hello` in the AI agent.

**Expected**: Response includes "Hello from Trasgo Spec Kit! Bundle install verified."

### 5. Roadmap command works

Invoke `/speckit-trasgospec-roadmap` in the AI agent (in a project with at least one spec).

**Expected**: A markdown table with ID, Title, Status, and Created columns.

### 6. Idempotent reinstall

```bash
specify bundle install trasgospec
```

**Expected**: `0 added, 2 already present`.

### 7. Bundle structure verification

After implementation, verify the directory layout:

```bash
ls bundle/extensions/trasgospec-hello/
# Expected: extension.yml, commands/

ls bundle/extensions/trasgospec-roadmap/
# Expected: extension.yml, commands/, scripts/

# Old directories should not exist:
ls bundle/skills/ 2>&1    # Should fail (directory removed)
ls bundle/commands/ 2>&1  # Should fail (directory removed)
```
