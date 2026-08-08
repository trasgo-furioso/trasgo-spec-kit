# Contract: Hook Registration in extensions.yml

## Overview

When the trasgospec bundle is installed, it registers flow enforcement hooks in `.specify/extensions.yml`. This contract documents the expected hook entries.

## Hook Entries

### Mandatory Gate Hooks

The flow-gate hook is registered on `after_specify` (create/switch branch after spec creation) and seven `before_*` phases (block execution on `main`).

```yaml
hooks:
  after_specify:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — create/switch to feature branch after spec creation"
      optional: false
      enabled: true
  before_clarify:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_checklist:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_plan:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_tasks:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_implement:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_converge:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
  before_analyze:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: true
```

### Optional Nudge Hooks (after_*)

Registered on three milestone phases. Suggests PR actions.

```yaml
  after_plan:
    - extension: trasgospec
      command: speckit.trasgospec.flow-nudge
      description: "Suggest opening a draft PR for this feature"
      optional: true
      enabled: true
  after_implement:
    - extension: trasgospec
      command: speckit.trasgospec.flow-nudge
      description: "Suggest marking PR as ready for review"
      optional: true
      enabled: true
  after_analyze:
    - extension: trasgospec
      command: speckit.trasgospec.flow-nudge
      description: "Suggest PR is ready for final review"
      optional: true
      enabled: true
```

**Note**: `after_specify` has both a gate hook (mandatory) and no nudge hook. `after_plan` has both a nudge hook (optional) and no gate hook. There is no overlap — gate and nudge serve different purposes at different points.

## Idempotency Rules

1. Before adding a hook entry, check if an entry with the same `extension` AND `command` already exists at that hook point
2. If a matching entry exists, do not add a duplicate
3. If a matching entry exists with different `optional`/`enabled`/`description` values, do not overwrite — the user may have customized it
4. Hook entries from other extensions at the same hook point MUST be preserved

## Disabling Hooks

Users can disable individual hooks by setting `enabled: false`:

```yaml
  before_clarify:
    - extension: trasgospec
      command: speckit.trasgospec.flow-gate
      description: "GitHub Flow — require feature branch"
      optional: false
      enabled: false  # Disabled by user
```

The skill's hook dispatcher checks `enabled` before executing. Setting `enabled: false` is preferred over removing the entry (removal would cause re-registration on next bundle install).

## Settings

The `gh_integration` setting lives in the same file under `settings`:

```yaml
settings:
  auto_execute_hooks: true
  gh_integration: true  # default; set to false to disable gh CLI usage
```
