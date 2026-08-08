# Contract: scan-specs.sh JSON Output

**Version**: 1.0.0
**Producer**: `bundle/scripts/bash/scan-specs.sh`
**Consumer**: `bundle/commands/speckit.trasgospec.roadmap.md` (AI agent)

## Output Format

Single-line JSON on stdout. No other output on stdout (diagnostics go
to stderr).

### Schema

```json
{
  "specs_dir": "<string>",
  "specs": [
    {
      "id": "<string>",
      "title": "<string>",
      "status": "<string>",
      "created": "<string>"
    }
  ]
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `specs_dir` | string | yes | Relative path to the specs directory (e.g., `specs`) |
| `specs` | array | yes | Ordered array of spec entries. Empty array `[]` when no specs found. |
| `specs[].id` | string | yes | Directory name (e.g., `001-bundle-install`) |
| `specs[].title` | string | yes | Extracted from `# Feature Specification:` heading. Fallback: directory name without numeric prefix. |
| `specs[].status` | string | yes | Extracted from `**Status**:` field. Fallback: `"Unknown"`. |
| `specs[].created` | string | yes | Extracted from `**Created**:` field. Fallback: `"Unknown"`. |

### Ordering

The `specs` array is sorted by directory name in natural ascending
order (alphabetical, which preserves both sequential `001-`, `002-`
and timestamp `20260808-` ordering).

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success. JSON emitted on stdout. |
| 1 | Error (e.g., specs directory not found). Diagnostic on stderr. |

### Examples

**Multiple specs**:
```json
{"specs_dir":"specs","specs":[{"id":"001-bundle-install","title":"Bundle Install","status":"Draft","created":"2026-08-07"},{"id":"002-roadmap-visualization","title":"Roadmap Visualization","status":"Draft","created":"2026-08-08"}]}
```

**No specs found**:
```json
{"specs_dir":"specs","specs":[]}
```

**Spec with missing metadata**:
```json
{"specs_dir":"specs","specs":[{"id":"003-incomplete","title":"003-incomplete","status":"Unknown","created":"Unknown"}]}
```
