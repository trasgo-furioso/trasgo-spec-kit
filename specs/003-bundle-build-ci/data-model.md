# Data Model: Bundle Build CI

## Entities

### Bundle Manifest (`bundle/bundle.yml`)

Source of truth for bundle metadata. Read-only from the hook's perspective.

| Field | Type | Example | Used By Hook |
|-------|------|---------|--------------|
| bundle.id | string | `trasgospec` | Yes — catalog key |
| bundle.name | string | `Trasgo Spec Kit` | Yes — catalog sync |
| bundle.version | string | `0.2.0` | Yes — catalog sync, zip filename |
| bundle.description | string | `Journey-first product...` | Yes — catalog sync |
| bundle.role | string | `developer` | Yes — catalog sync |
| bundle.author | string | `Trasgo Furioso [...]` | No |
| bundle.license | string | `MIT` | No |
| bundle.integration | string | `claude` | No |

### Catalog Entry (`catalog.json`)

Updated by the hook after a successful build. Structure per `schema_version: 1.0`.

| Field | Type | Source | Update Rule |
|-------|------|--------|-------------|
| schema_version | string | Static | Never changed |
| bundles.\<id\>.id | string | bundle.id | Sync from manifest |
| bundles.\<id\>.name | string | bundle.name | Sync from manifest |
| bundles.\<id\>.description | string | bundle.description | Sync from manifest |
| bundles.\<id\>.version | string | bundle.version | Sync from manifest |
| bundles.\<id\>.role | string | bundle.role | Sync from manifest |
| bundles.\<id\>.download_url | string | Computed | `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<id>-<version>.zip` |

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
    │
    ├──reads──→ Pre-Push Hook ──produces──→ Bundle Artifact (zip)
    │                │
    │                └──updates──→ Catalog Entry (catalog.json)
    │                                  │
    └────────syncs fields to───────────┘
```

## State Transitions

The hook has no persistent state, but the build process follows this flow:

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
