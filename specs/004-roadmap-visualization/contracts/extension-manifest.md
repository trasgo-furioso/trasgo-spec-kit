# Contract: Extension Manifest (`extension.yml`)

## Overview

Each extension in the bundle MUST have an `extension.yml` manifest at `extensions/{extension-id}/extension.yml`. The installer uses this manifest to register the extension's commands and hooks into the target project.

## Schema

```yaml
schema_version: "1.0"

extension:
  id: "{extension-id}"           # MUST match directory name and bundle.yml reference
  name: "{Human-Readable Name}"
  version: "{semver}"            # MUST match version in bundle.yml
  description: "{description}"
  author: "{author}"             # Optional
  license: "{license}"           # Optional
  category: "{category}"         # Optional (e.g., "utility", "security")
  effect: "{read-only|read-write}" # Optional

requires:
  speckit_version: "{version-constraint}"  # e.g., ">=0.15.0"

provides:
  commands:
    - name: "speckit.{bundle-id}.{command-name}"  # Dot-namespaced
      file: "commands/{command-file}.md"           # Relative to extension root
      description: "{what it does}"
      aliases: ["{short-name}"]                    # Optional

hooks:                            # Optional lifecycle hooks
  after_specify:
    command: "speckit.{bundle-id}.{command}"
    optional: true
    description: "{hook description}"

tags: ["{tag1}", "{tag2}"]        # Optional
```

## Validation Rules

1. `extension.id` MUST match the containing directory name
2. `extension.id` MUST match the corresponding entry in `bundle.yml` `provides.extensions[].id`
3. `extension.version` MUST match `provides.extensions[].version` in `bundle.yml`
4. Every file referenced in `provides.commands[].file` MUST exist at the specified path relative to the extension directory
5. Command names MUST use dot-namespaced format: `speckit.{bundle-id}.{name}`
6. `schema_version` MUST be `"1.0"`

## Command File Contract

Command `.md` files referenced from the manifest follow this structure:

### Prompt-Only Command (no script)

```markdown
---
description: {what the command does}
---

{Agent instructions in markdown}
```

### Script-Backed Command

```markdown
---
description: {what the command does}
scripts:
  sh: {path-to-script-relative-to-extension-root}
---

{Agent instructions referencing {SCRIPT} placeholder}
```

The `{SCRIPT}` placeholder in the markdown body is resolved to the actual script path at runtime.

## Trasgospec Extension Manifests

### trasgospec-hello

- **ID**: `trasgospec-hello`
- **Commands**: `speckit.trasgospec.hello` (prompt-only, no script)
- **Purpose**: Bundle installation verification

### trasgospec-roadmap

- **ID**: `trasgospec-roadmap`
- **Commands**: `speckit.trasgospec.roadmap` (script-backed)
- **Script**: `scripts/bash/scan-specs.sh`
- **Purpose**: Feature roadmap visualization
