# Research: Bundle Extension Components

## R1: Why does `provides.skills` result in 0 components?

**Decision**: Skills are not a recognized component type for the bundle installer's contribution mechanism.

**Rationale**: The SicarioSpec example bundle (a known working bundle) exclusively uses `provides.extensions` and `provides.presets`. After installing trasgospec with `provides.skills`, the bundle record shows `"contributed_components": []`. The installer downloads and registers the bundle but does not know how to extract or install skill-type components. Extensions and presets have dedicated registry files (`.specify/extensions/.registry`, `.specify/presets/.registry`) and installation directories — skills have no equivalent infrastructure.

**Alternatives considered**:
- Declaring skills alongside extensions: No evidence that the installer processes skills at all; extensions are the correct vehicle for commands.
- Filing a bug against Spec Kit: The behavior appears by design — extensions are the documented component type for commands.

## R2: Extension manifest structure

**Decision**: Follow the `extension.yml` schema used by SicarioSpec (`schema_version: "1.0"`).

**Rationale**: The SicarioSpec `sicario-guard` extension successfully installs with this manifest structure:
- `extension:` block with id, name, version, description, author, license, category, effect
- `requires:` block with speckit_version
- `provides.commands:` array with name, file, description, and optional aliases
- Optional `hooks:` block for lifecycle integration
- Optional `tags:` array

**Alternatives considered**:
- Minimal manifest (id + version only): Would miss required fields that the installer validates.
- Custom manifest format: Would violate Principle II (Spec Kit Native).

## R3: Hello command — extension vs standalone command

**Decision**: The hello command becomes a pure-prompt extension (no script). The command `.md` file contains only agent instructions, no `scripts` key in frontmatter.

**Rationale**: The SicarioSpec `sicario.init.md` command demonstrates that commands can be pure markdown instructions without a backing script. The hello command's sole purpose is to echo a verification message — no deterministic computation is needed.

**Alternatives considered**:
- Adding a trivial script that echoes JSON: Over-engineering per constitution; the command is purely presentational.
- Keeping it as a SKILL.md: Skills don't get installed by the bundle installer.

## R4: Script path references in extension-scoped commands

**Decision**: Script paths in command frontmatter are relative to the bundle root, not the extension directory. The roadmap command's `scripts.sh` key will reference `extensions/trasgospec-roadmap/scripts/bash/scan-specs.sh`.

**Rationale**: The SicarioSpec example does not include script-backed commands, so there's no direct reference. However, the existing working command at `bundle/commands/speckit.trasgospec.roadmap.md` uses `bundle/scripts/bash/scan-specs.sh` — a path relative to the repo root during development. After bundle packaging and installation, the installer extracts extensions into `.specify/extensions/{id}/` and command file paths in `extension.yml` are relative to the extension root. The script path in the command frontmatter should therefore be relative to the installed extension location.

**Alternatives considered**:
- Absolute paths: Not portable across installations.
- Bundle-root-relative paths: Would break after extraction into `.specify/extensions/`.

## R5: Impact on existing tests

**Decision**: Existing unit tests for `scan-specs.sh` remain valid — the script content doesn't change, only its filesystem location. Test fixtures may need path updates.

**Rationale**: `test_scan_specs.py` tests the script's behavior (JSON output, edge cases) by invoking it directly. As long as the script path in test fixtures is updated, all tests should continue passing. Integration tests that reference `bundle/commands/` or `bundle/skills/` paths will need updating.

**Alternatives considered**:
- Rewriting tests: Unnecessary — the script logic is unchanged.
- Keeping the script in the old location: Would break the extension packaging contract.

## R6: Bundle build automation impact

**Decision**: The pre-push hook builds a zip from `bundle/`. Since extensions now live under `bundle/extensions/`, they will be included automatically.

**Rationale**: Reviewing the build process: the hook runs `specify bundle validate` and then packages the `bundle/` directory. The new `extensions/` subdirectory will be picked up by the zip operation. No build script changes are expected.

**Alternatives considered**:
- Modifying the build script: Only if validation fails, which would indicate a structural issue to fix in the extensions themselves.
