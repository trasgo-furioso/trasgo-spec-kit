# Contract: Catalog Update

Defines how the pre-push hook updates `catalog.json` after a successful bundle build.

## Input

Fields read from `bundle/bundle.yml`:

```yaml
bundle:
  id: <string>         # Used as catalog key
  name: <string>       # Synced to catalog
  version: <string>    # Synced to catalog + used in download URL
  description: <string> # Synced to catalog
  role: <string>       # Synced to catalog
```

## Output

Updated `catalog.json` structure (schema_version 1.0):

```json
{
  "schema_version": "1.0",
  "bundles": {
    "<bundle-id>": {
      "id": "<bundle.id>",
      "name": "<bundle.name>",
      "description": "<bundle.description>",
      "version": "<bundle.version>",
      "role": "<bundle.role>",
      "download_url": "https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<bundle-id>-<version>.zip"
    }
  }
}
```

## Download URL Construction

```
https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<bundle-id>-<version>.zip
```

Where:
- `<owner>` and `<repo>` are extracted from the git remote URL (`origin`)
- `<bundle-id>` comes from `bundle.id` in `bundle.yml`
- `<version>` comes from `bundle.version` in `bundle.yml`

### Remote URL Parsing

| Remote Format | Example | Extraction |
|---------------|---------|------------|
| SSH | `git@github.com:owner/repo.git` | Parse after `:`, strip `.git` |
| HTTPS | `https://github.com/owner/repo.git` | Parse path, strip `.git` |

## Sync Rules

- All synced fields are overwritten unconditionally from `bundle.yml`
- `schema_version` is never modified
- If `catalog.json` does not exist, it is created with the full structure
- The `bundles` object key matches `bundle.id`
- Only the bundle matching `bundle.id` is updated; other bundle entries (if any) are preserved
