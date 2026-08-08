# Data Model: Bundle Extension Components

## Entities

### Extension Manifest (`extension.yml`)

Declares the identity and capabilities of a single extension within the bundle.

| Field | Description | Required |
|-------|-------------|----------|
| schema_version | Manifest schema version (always "1.0") | Yes |
| extension.id | Unique extension identifier | Yes |
| extension.name | Human-readable extension name | Yes |
| extension.version | Semantic version string | Yes |
| extension.description | What the extension does | Yes |
| extension.author | Extension author/org | No |
| extension.license | License identifier | No |
| extension.category | Extension category (e.g., "utility") | No |
| extension.effect | Read/write capability declaration | No |
| requires.speckit_version | Minimum Spec Kit version constraint | Yes |
| provides.commands[] | Array of command registrations | Yes |
| provides.commands[].name | Dot-namespaced command ID | Yes |
| provides.commands[].file | Path to command definition file (relative to extension root) | Yes |
| provides.commands[].description | Command description | Yes |
| provides.commands[].aliases | Alternate invocation names | No |
| hooks | Lifecycle hook registrations | No |
| tags | Searchable tags | No |

### Command Definition (`.md` file)

Instructions for the AI agent to execute when the command is invoked.

| Section | Description | Required |
|---------|-------------|----------|
| YAML frontmatter: description | What the command does | Yes |
| YAML frontmatter: scripts.sh | Path to bash script (relative to extension root) | Only for script-backed commands |
| Markdown body | Agent instructions for executing the command | Yes |

### Bundle Manifest (`bundle.yml`)

Top-level manifest declaring all components the bundle provides.

| Field | Description | Required |
|-------|-------------|----------|
| schema_version | Manifest schema version ("1.0") | Yes |
| bundle.id | Bundle identifier | Yes |
| bundle.name | Human-readable name | Yes |
| bundle.version | Semantic version | Yes |
| bundle.description | Bundle description | Yes |
| bundle.author | Author | No |
| bundle.license | License | No |
| bundle.role | Target user role | No |
| bundle.integration | AI integration target | No |
| requires.speckit_version | Minimum Spec Kit version | Yes |
| provides.extensions[] | Array of extension declarations | Yes |
| provides.extensions[].id | Extension ID (must match extension.yml) | Yes |
| provides.extensions[].version | Extension version (must match extension.yml) | Yes |

## Relationships

```
bundle.yml
  └── provides.extensions[]
       ├── trasgospec-hello (id + version)
       │    └── extensions/trasgospec-hello/extension.yml
       │         └── provides.commands[]
       │              └── speckit.trasgospec.hello
       │                   └── commands/speckit.trasgospec.hello.md (prompt-only)
       │
       └── trasgospec-roadmap (id + version)
            └── extensions/trasgospec-roadmap/extension.yml
                 └── provides.commands[]
                      └── speckit.trasgospec.roadmap
                           ├── commands/speckit.trasgospec.roadmap.md (agent instructions)
                           └── scripts/bash/scan-specs.sh (deterministic script)
```

## State Transitions

No runtime state transitions. The extensions are static configuration artifacts resolved at bundle install time. The installer transitions the bundle from "downloaded" to "installed with N contributed components" based on the presence and validity of extension manifests.
