# Data Model: Discovery Command Hooks

**Feature**: 010-discovery-hooks | **Date**: 2026-08-09

## Entities

### Hook Registration Entry

Existing schema — no modifications required. Each entry under `hooks.before_discovery` or `hooks.after_discovery` in `.specify/extensions.yml` follows:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `extension` | string | yes | — | Bundle ID (e.g., `trasgospec`) |
| `command` | string | yes | — | Dot-namespaced command ID (e.g., `speckit.trasgospec.flow-gate`) |
| `enabled` | boolean | no | `true` | User-togglable; `false` suppresses dispatch |
| `optional` | boolean | yes | — | `false` = mandatory (blocks), `true` = presented to user |
| `priority` | integer | no | 10 | Lower = runs first |
| `prompt` | string | no | — | Display text for optional hooks |
| `description` | string | no | — | Human-readable purpose |
| `condition` | string/null | no | `null` | Reserved for HookExecutor; not evaluated by command |

### Discovery Lifecycle (with hooks)

```
┌─────────────────────────┐
│  before_discovery hooks  │  ← flow-gate (branch enforcement)
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  Discovery conversation  │  ← Interactive Q&A, incremental saves
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     │             │
  aborted      completed
     │             │
     ▼             ▼
  (no hooks)  ┌───────────────────────┐
              │  after_discovery hooks │  ← status (Discovery→Opportunity), flow-nudge
              └───────────────────────┘
```

### State Transitions

| From | To | Trigger | Hook |
|------|----|---------|------|
| (any branch) | feature branch | `before_discovery` | `speckit.trasgospec.flow-gate` |
| Discovery | Opportunity | `after_discovery` | `speckit.trasgospec.status` |

### Relationships

- **Hook Registration** → **Extension Command**: Each registration references a command by its dot-namespaced ID
- **Discovery Lifecycle** → **Hook Registration**: The command file reads registrations from extensions.yml at the appropriate lifecycle points
- **After-discovery hooks** → **PRD completion**: Post-hooks only fire when prd.md is successfully written (not on abort)
