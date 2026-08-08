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
| `description` | string | yes | Short bundle description |
| `role` | string | yes | Target persona: `developer` |
| `integration` | string | yes | Target integration: `claude` |
| `author` | string | no | Bundle author |
| `license` | string | no | License identifier |
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

A JSON file containing bundle metadata for discovery. Updated by the
pre-push hook after each successful build.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | yes | Must be `"1.0"` |
| `bundles` | object | yes | Object keyed by bundle ID |

**Bundle Entry fields**:

| Field | Type | Required | Source | Update Rule |
|-------|------|----------|--------|-------------|
| `id` | string | yes | bundle.id | Sync from manifest |
| `name` | string | yes | bundle.name | Sync from manifest |
| `description` | string | yes | bundle.description | Sync from manifest |
| `version` | semver | yes | bundle.version | Sync from manifest |
| `role` | string | yes | bundle.role | Sync from manifest |
| `download_url` | URL | yes | Computed | `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<id>-<version>.zip` |

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

### Bundle Artifact (zip file)

Produced by `specify bundle build --path bundle --output .`. Placed at repository root.

| Attribute | Value |
|-----------|-------|
| Location | Repository root (`.`) |
| Filename pattern | `<bundle-id>-<version>.zip` (determined by `specify bundle build`) |
| Git tracking | Requires `.gitignore` negation pattern |
| Lifecycle | Overwritten on each build; only latest version committed |

### Pre-Push Hook State

No persistent state. The hook reads git stdin and computes everything per invocation.

| Input | Source | Purpose |
|-------|--------|---------|
| remote_name | Arg 1 | Identify target remote |
| remote_url | Arg 2 | Parse owner/repo for download URL |
| local_ref | stdin field 1 | Identify branch being pushed |
| local_sha | stdin field 2 | Compute diff range |
| remote_ref | stdin field 3 | Identify target branch |
| remote_sha | stdin field 4 | Compute diff range (base) |

## Relationships

```
Bundle Manifest (bundle.yml)
  ├── provides
  │    └── Skill: trasgospec
  │
  ├──reads──→ Pre-Push Hook ──produces──→ Bundle Artifact (zip)
  │                │
  │                └──updates──→ Catalog Entry (catalog.json)
  │                                  │
  └────────syncs fields to───────────┘

Catalog File (catalog.json)
  └── bundles.<id>
       └── entry → references bundle artifact (.zip)

Provenance Record
  └── links installed component → source bundle
```

## State Transitions

### Bundle Install State

The bundle has no internal state machine. State is managed by Spec Kit:

```
Not Installed → [specify bundle install] → Installed
Installed → [specify bundle install] → Installed (idempotent, no-op)
Installed → [specify bundle remove] → Not Installed
Installed → [specify bundle update] → Installed (refreshed)
```

### Pre-Push Hook Flow

```
Push initiated
  → Read stdin refs
  → Check if pushing to main branch
    → No: EXIT 0 (skip)
  → Diff commits for bundle/ changes
    → None found: EXIT 0 (skip)
  → Verify `specify` CLI available
    → Not found: EXIT 1 (block push, error message)
  → Run `specify bundle validate --path bundle`
    → Fails: EXIT 1 (block push, show errors)
  → Run `specify bundle build --path bundle --output .`
    → Fails: EXIT 1 (block push, show errors)
  → Parse bundle.yml for metadata
  → Parse git remote for owner/repo
  → Update catalog.json fields
  → Stash working tree changes (if any)
  → git add <zip> catalog.json
  → git commit -m "chore: build bundle vX.Y.Z"
  → Restore stash (if applied)
  → EXIT 0 (push proceeds with new commit)
```
