# Contract: Catalog File (`catalog.json`)

**Date**: 2026-08-07 | **Feature**: 001-bundle-install

## Format

JSON file hosted at a publicly accessible URL
(raw.githubusercontent.com).

## Schema

```json
{
  "bundles": [
    {
      "id": "trasgospec",
      "name": "Trasgo Spec Kit",
      "description": "Scaffold Spec Kit bundle for the claude integration with a /trasgospec hello command",
      "version": "0.1.0",
      "role": "developer",
      "repository": "https://github.com/<owner>/trasgospec",
      "release_url": "https://github.com/<owner>/trasgospec/releases/download/v0.1.0/trasgospec-0.1.0.zip"
    }
  ]
}
```

## Field Contracts

| Field | Constraint |
|-------|-----------|
| `bundles` | Non-empty array of bundle entries |
| `bundles[].id` | Must match `bundle.yml` id |
| `bundles[].name` | Must match `bundle.yml` name |
| `bundles[].version` | Must match `bundle.yml` version |
| `bundles[].description` | Non-empty string |
| `bundles[].role` | Must match `bundle.yml` role |
| `bundles[].repository` | Valid URL to source repository |
| `bundles[].release_url` | Valid URL to downloadable `.zip` artifact |

## Hosting

- File lives at repository root: `catalog.json`
- Accessed via: `https://raw.githubusercontent.com/<owner>/trasgospec/main/catalog.json`
- Consumers add it: `specify bundle catalog add <url> --policy install-allowed`

## Consumers

- `specify bundle search` — reads catalog to list available bundles
- `specify bundle info` — reads catalog to show bundle details
- `specify bundle install` — reads catalog to resolve bundle artifact URL

## Trust

- Bundles from self-hosted catalogs display a `community` trust
  indicator (not `verified`).
