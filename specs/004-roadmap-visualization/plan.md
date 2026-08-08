# Implementation Plan: Bundle Extension Components

**Branch**: `004-bundle-extensions` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-bundle-extensions/spec.md`

## Summary

The trasgo-spec-kit bundle declares components as `provides.skills` in `bundle.yml`, but the Spec Kit installer only contributes extensions and presets — not skills. This restructuring converts both bundle components (hello and roadmap) into proper extensions with `extension.yml` manifests and reorganizes files into the `extensions/` directory layout, so `specify bundle install trasgospec` delivers working commands.

## Technical Context

**Language/Version**: Bash 3.2+ (macOS compatible), YAML/Markdown config files

**Primary Dependencies**: GitHub Spec Kit >=0.15.0 (bundle installer, extension resolver)

**Storage**: Filesystem — YAML manifests, Markdown command files, Bash scripts

**Testing**: pytest (existing test suite in `tests/unit/` and `tests/integration/`)

**Target Platform**: Any platform with Spec Kit installed (macOS, Linux)

**Project Type**: Spec Kit bundle (installable extension package)

**Performance Goals**: N/A (configuration restructuring, no runtime performance concerns)

**Constraints**: Must maintain backward compatibility with the existing `scan-specs.sh` script contract; must pass `specify bundle validate`

**Scale/Scope**: 2 extensions, 2 command files, 1 script, 2 manifests, 1 bundle manifest update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | Converting skills to extensions uses Spec Kit's native extension mechanism — no custom runtime behavior |
| II. Spec Kit Native | PASS | Extensions with `extension.yml` manifests follow documented Spec Kit patterns |
| III. Documentation-Driven | PASS | Design is based on analysis of SicarioSpec example bundle (a working reference) |
| IV. Idempotent & Traceable | PASS | Extension install/uninstall is handled by Spec Kit's built-in installer |
| V. Version-Pinned | PASS | Extension versions will be pinned in `bundle.yml` |
| VI. TDD | PASS | Existing test suite covers bundle validation; new tests will be added per TDD cycle |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/004-bundle-extensions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── extension-manifest.md  # Extension manifest contract
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/
├── bundle.yml                              # Updated: provides.extensions
├── README.md
├── extensions/
│   ├── trasgospec-hello/
│   │   ├── extension.yml                   # NEW: extension manifest
│   │   └── commands/
│   │       └── speckit.trasgospec.hello.md  # NEW: hello command definition
│   └── trasgospec-roadmap/
│       ├── extension.yml                   # NEW: extension manifest
│       ├── commands/
│       │   └── speckit.trasgospec.roadmap.md  # MOVED from bundle/commands/
│       └── scripts/
│           └── bash/
│               └── scan-specs.sh           # MOVED from bundle/scripts/bash/

tests/
├── unit/
│   ├── test_scan_specs.py                  # EXISTING
│   ├── test_setup.py                       # EXISTING
│   └── test_pre_push_hook.py               # EXISTING
└── integration/
    └── ...                                 # EXISTING
```

**Structure Decision**: Extensions live inside `bundle/extensions/{id}/` with self-contained directory trees. The existing `bundle/commands/` and `bundle/skills/` directories are removed after migration. The `bundle/scripts/` top-level directory is removed; scripts move into their owning extension.

### Files to Remove

- `bundle/skills/trasgospec/SKILL.md` — replaced by `extensions/trasgospec-hello/`
- `bundle/skills/trasgospec-roadmap/SKILL.md` — replaced by `extensions/trasgospec-roadmap/`
- `bundle/skills/` directory (empty after migration)
- `bundle/commands/speckit.trasgospec.roadmap.md` — moved into extension
- `bundle/commands/` directory (empty after migration)
- `bundle/scripts/bash/scan-specs.sh` — moved into extension
- `bundle/scripts/` directory (empty after migration)
