# Contract: Bundle Manifest (`bundle.yml`)

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## Format

YAML file at the bundle root directory.

## Schema

```yaml
id: trasgospec
name: Trasgo Spec Kit
version: "0.1.0"
role: developer
integration: claude

requirements:
  speckit_version: ">=0.15.0"

provides:
  skills:
    - id: trasgospec
      version: "0.1.0"
```

## Field Contracts

| Field | Constraint |
|-------|-----------|
| `id` | Non-empty string, unique across catalogs |
| `name` | Non-empty human-readable string |
| `version` | Valid semver (MAJOR.MINOR.PATCH) |
| `role` | Non-empty string describing target persona |
| `integration` | Must match target project's active integration |
| `requirements.speckit_version` | Valid semver range |
| `provides.skills[].id` | Non-empty string, unique within bundle |
| `provides.skills[].version` | Valid semver |

## Validation Rules

- `specify bundle validate` MUST confirm all fields present and valid.
- Component IDs in `provides` MUST resolve to local bundled files or
  active catalog entries.
- `integration` field causes install to abort if the target project
  uses a different integration.

## Consumers

- `specify bundle install` — reads manifest, installs components
- `specify bundle validate` — validates structure and references
- `specify bundle build` — packages manifest + components into `.zip`
- `specify bundle info` — displays expanded component set
