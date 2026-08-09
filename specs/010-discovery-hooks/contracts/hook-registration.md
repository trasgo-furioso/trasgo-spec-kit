# Contract: Hook Registration for Discovery

**Feature**: 010-discovery-hooks | **Date**: 2026-08-09

## extensions.yml Hook Entries

Three new entries to add under `hooks:` in `.specify/extensions.yml`:

### before_discovery

```yaml
before_discovery:
- extension: trasgospec
  command: speckit.trasgospec.flow-gate
  enabled: true
  optional: false
  priority: 10
  prompt: Execute speckit.trasgospec.flow-gate?
  description: GitHub Flow — require feature branch
  condition: null
```

### after_discovery

```yaml
after_discovery:
- extension: trasgospec
  command: speckit.trasgospec.status
  enabled: true
  optional: false
  priority: 5
  prompt: Execute speckit.trasgospec.status?
  description: Lifecycle — advance status to Opportunity
  condition: null
- extension: trasgospec
  command: speckit.trasgospec.flow-nudge
  enabled: true
  optional: true
  priority: 10
  prompt: Execute speckit.trasgospec.flow-nudge?
  description: Suggest next steps after discovery
  condition: null
```

## extension.yml Hook Declarations

Two new entries to add under `hooks:` in `bundle/extensions/trasgospec/extension.yml`:

```yaml
before_discovery:
  command: "speckit.trasgospec.flow-gate"
  optional: false
  description: "GitHub Flow — require feature branch"
after_discovery:
  - command: "speckit.trasgospec.status"
    optional: false
    priority: 5
    description: "Lifecycle — advance status to Opportunity"
  - command: "speckit.trasgospec.flow-nudge"
    optional: true
    priority: 10
    description: "Suggest next steps after discovery"
```
