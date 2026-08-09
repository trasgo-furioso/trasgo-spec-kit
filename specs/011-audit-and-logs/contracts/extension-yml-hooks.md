# Contract: extension.yml Hook Registrations

## New Hooks Added to extension.yml

The commit command is registered as an `after_*` hook for all artifact-producing skills. These entries are declared in the bundle's `extension.yml` and merged into the project's `.specify/extensions.yml` during `specify bundle install`.

### Hook Entry Template

```yaml
after_<phase>:
  - extension: trasgospec
    command: speckit.trasgospec.commit
    enabled: true
    optional: false
    priority: 20
    prompt: Execute speckit.trasgospec.commit?
    description: "Audit — auto-commit and push"
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

All commit hooks use `priority: 20`, ensuring they execute after:
- Status advancement hooks (priority 5)
- Flow-nudge hooks (priority 10)

This means the commit captures all changes, including those made by earlier hooks.

### New Command Registration

```yaml
- name: "speckit.trasgospec.commit"
  file: "commands/speckit.trasgospec.commit.md"
  description: "Auto-commit and push repository changes with structured messages."
  aliases: ["trasgospec.commit"]
```
