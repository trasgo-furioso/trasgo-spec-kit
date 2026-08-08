# Tasks: Bundle Extension Components

**Input**: Design documents from `specs/004-bundle-extensions/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/extension-manifest.md

**Tests**: Required per constitution (Principle VI: TDD). Tests use pytest exclusively.

**Organization**: Tasks grouped by user story. Adapted during implementation: command namespace validation requires a single extension (`trasgospec`) with both commands, and bundle install resolves extensions through a separate extension catalog.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create extension directory structure

- [x] T001 Create extension directory tree: `bundle/extensions/trasgospec/commands/` and `bundle/extensions/trasgospec/scripts/bash/`

---

## Phase 2: User Story 2 & 3 - Extension with Hello + Roadmap Commands (TDD)

**Goal**: Create a single `trasgospec` extension with both commands (hello prompt-only, roadmap script-backed). Single extension required because Spec Kit validates that command namespace matches extension id.

### Tests (RED first)

- [x] T002 [P] [US2] Write tests validating trasgospec extension.yml structure, required fields, and both commands registered in `tests/unit/test_extension_manifests.py`
- [x] T003 [P] [US2] Write tests validating command files and script files exist at paths declared in extension.yml in `tests/unit/test_extension_manifests.py`

### Implementation (GREEN)

- [x] T004 [US2] Create extension manifest in `bundle/extensions/trasgospec/extension.yml` (id: trasgospec, two commands: speckit.trasgospec.hello + speckit.trasgospec.roadmap)
- [x] T005 [P] [US2] Create hello command definition in `bundle/extensions/trasgospec/commands/speckit.trasgospec.hello.md` (prompt-only)
- [x] T006 [US3] Copy `bundle/commands/speckit.trasgospec.roadmap.md` to `bundle/extensions/trasgospec/commands/` and update script path to `scripts/bash/scan-specs.sh` (relative to extension root)
- [x] T007 [US3] Copy `bundle/scripts/bash/scan-specs.sh` to `bundle/extensions/trasgospec/scripts/bash/scan-specs.sh`
- [x] T008 [US3] Update `SCAN_SPECS_SCRIPT` path in `tests/unit/test_scan_specs.py` and all 3 roadmap integration tests to `bundle/extensions/trasgospec/scripts/bash/scan-specs.sh`
- [x] T009 Verify all extension manifest tests and scan-specs tests pass

**Checkpoint**: trasgospec extension with 2 commands is valid and tested

---

## Phase 3: User Story 1 - Bundle Install Delivers Working Commands (TDD)

**Goal**: Update bundle manifest, create extension catalog, and verify the full install flow delivers components.

### Tests (RED first)

- [x] T010 [P] [US1] Write tests validating bundle.yml declares `provides.extensions` (not `provides.skills`), IDs match extension.yml, versions match in `tests/unit/test_bundle_manifest.py`

### Implementation (GREEN)

- [x] T011 [US1] Update `bundle/bundle.yml`: replace `provides.skills` with `provides.extensions` listing trasgospec (v0.2.0)
- [x] T012 [US1] Create `extension-catalog.json` at repo root with trasgospec extension entry and download_url
- [x] T013 [US1] Build `trasgospec-extension-0.2.0.zip` from `bundle/extensions/trasgospec/`
- [x] T014 [US1] Verify bundle manifest tests pass
- [x] T015 [US1] Run `specify bundle validate` and confirm `✓ is well-formed and valid`

### Integration Tests

- [x] T016 [US1] Update `tests/integration/conftest.py`: add `_TEST_EXTENSION_CATALOG` serving extension catalog + zip via local HTTP server, add `extension_catalog_url` and `project_with_extension_catalog` fixtures, update `project_with_catalog` to add both catalogs
- [x] T017 [US1] Update `tests/integration/test_us1_install.py`: use `project_with_extension_catalog` fixture for local path installs, add `test_local_path_install_delivers_components` asserting non-zero count
- [x] T018 [US1] Update `tests/integration/test_edge_cases.py`: add extension catalog to mismatch test, add `TestMissingExtensionCatalog` test class
- [x] T019 [US1] Run full integration test suite: 72/72 pass

**Checkpoint**: Bundle installs with 1 component (1 extension, 2 commands), all tests pass

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Clean up old structure, update documentation, final validation

- [x] T020 Remove old directories: `bundle/skills/`, `bundle/commands/`, `bundle/scripts/`
- [x] T021 Update `bundle/README.md` with extension catalog install step and updated component list
- [x] T022 Update root `README.md` with extension catalog install step and updated component list
- [x] T023 Run full test suite: 72/72 pass

---

## Implementation Notes

### Key Discoveries During Implementation

1. **Single extension required**: Spec Kit validates that command names use the extension's namespace (`speckit.{extension-id}.*`). Two separate extensions (`trasgospec-hello`, `trasgospec-roadmap`) would require command names like `speckit.trasgospec-hello.verify` instead of `speckit.trasgospec.hello`. A single `trasgospec` extension with both commands is the correct pattern.

2. **Extension catalog required**: `specify bundle install` resolves extensions through the extension catalog stack, NOT from bundled content. Extensions must be published to an extension catalog (separate from the bundle catalog) with a `download_url` pointing to an extension zip.

3. **Two-catalog install flow**: Users must add both the bundle catalog (`catalog.json`) AND the extension catalog (`extension-catalog.json`) before installing. Integration tests arrange this via a local HTTP server fixture.
