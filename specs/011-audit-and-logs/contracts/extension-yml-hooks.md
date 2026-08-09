# Contract: extension.yml Hook Registrations

## New Hooks Added to extension.yml

The audit-commit command is registered as an `after_*` hook for all artifact-producing skills. These entries are declared in the bundle's `extension.yml` and merged into the project's `.specify/extensions.yml` during `specify bundle install`.

### Hook Entries

Each entry follows this structure:

```yaml
after_<phase>:
  - extension: trasgospec
    command: speckit.trasgospec.audit-commit
    enabled: true
    optional: false
    priority: 20
    prompt: Execute speckit.trasgospec.audit-commit?
    description: "Audit — auto-commit spec artifacts"
    condition: null
```

### Phases Covered

| Phase | Hook Key | Existing Hooks (lower priority) |
|-------|----------|--------------------------------|
| discovery | `after_discovery` | status (5), flow-nudge (10) |
| specify | `after_specify` | flow-gate (10) |
| clarify | `after_clarify` | (none) |
| checklist | `after_checklist` | (none) |
| plan | `after_plan` | status (5), flow-nudge (10) |
| tasks | `after_tasks` | (none) |
| implement | `after_implement` | status (5), flow-nudge (10) |
| converge | `after_converge` | (none) |

### Priority Ordering

All audit hooks use `priority: 20`, ensuring they execute after:
- Status advancement hooks (priority 5)
- Flow-nudge hooks (priority 10)

This means the audit commit captures all artifact changes, including those made by earlier hooks.
