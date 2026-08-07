# Data Model: Bundle Install

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## Entities

### Bundle Manifest (`bundle.yml`)

The root configuration file declaring the bundle's identity and
component set.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique bundle identifier: `trasgospec` |
| `name` | string | yes | Human-readable: `Trasgo Spec Kit` |
| `version` | semver | yes | Bundle version: `0.1.0` |
| `role` | string | yes | Target persona: `developer` |
| `integration` | string | yes | Target integration: `claude` |
| `speckit_version` | string | yes | Minimum SK version constraint |
| `provides` | object | yes | Component declarations (see below) |

### Provides (Component Set)

Nested under `provides` in `bundle.yml`. Each key is a component type;
each entry has an `id` and `version`.

| Component Type | ID | Version | Description |
|---------------|----|---------|-------------|
| `skills` | `trasgospec` | `0.1.0` | The `/trasgospec` hello command |

For the scaffold, only one skill is declared. Future versions add
extensions, presets, workflows, and steps here.

### Catalog File (`catalog.json`)

A JSON file containing bundle metadata for discovery.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bundles` | array | yes | List of bundle entries |

**Bundle Entry fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Matches `bundle.yml` id: `trasgospec` |
| `name` | string | yes | Human-readable name |
| `description` | string | yes | Short bundle description |
| `version` | semver | yes | Matches `bundle.yml` version |
| `role` | string | yes | Target persona |
| `repository` | URL | yes | GitHub repo URL |
| `release_url` | URL | yes | URL to built `.zip` artifact |

### Trasgospec Skill (`SKILL.md`)

A Spec Kit skill file that defines the `/trasgospec` command.

| Field | Type | Description |
|-------|------|-------------|
| Skill name | string | `trasgospec` |
| Trigger | string | `/trasgospec` command invocation |
| Output | string | Hello/greeting message |

### Provenance Record

Managed by Spec Kit internally. Written at install time, read at
remove/update time.

| Field | Type | Description |
|-------|------|-------------|
| Component ID | string | Installed component identifier |
| Bundle ID | string | Source bundle that contributed it |
| Version | semver | Installed version |
| Timestamp | ISO 8601 | Installation time |

## Relationships

```
Bundle Manifest (bundle.yml)
  └── provides
       └── Skill: trasgospec

Catalog File (catalog.json)
  └── bundles[]
       └── entry → references bundle artifact (.zip)

Provenance Record
  └── links installed component → source bundle
```

## State Transitions

The bundle has no internal state machine. State is managed by Spec Kit:

```
Not Installed → [specify bundle install] → Installed
Installed → [specify bundle install] → Installed (idempotent, no-op)
Installed → [specify bundle remove] → Not Installed
Installed → [specify bundle update] → Installed (refreshed)
```
