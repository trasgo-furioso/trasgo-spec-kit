# Feature Specification: Bundle Install

**Feature Branch**: `001-bundle-install`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "given a project directory, when a user installs trasgo spec kit bundle using speckit catalog and bundle management tools, then trasgo bundle appears on the bundle list"

## Clarifications

### Session 2026-08-07

- Q: How is the bundle distributed before it is on the official catalog? → A: Self-hosted catalog file on GitHub with `specify bundle catalog add <url> --policy install-allowed`. The catalog file is hosted as a raw file in the repository (raw.githubusercontent.com).
- Q: Does the bundle target the `claude` integration specifically or is it integration-agnostic? → A: Claude-specific. The bundle targets the `claude` integration only.
- Q: What components does the bundle declare? → A: Minimal scaffold — a single custom `/trasgospec` hello command for testing the install flow. Existing repo files are default Spec Kit assets and MUST NOT be included in the bundle. More capabilities will be added later.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Trasgo Bundle from Self-Hosted Catalog (Priority: P1)

A user with an existing Spec Kit project wants to install the Trasgo Spec Kit bundle. Since the bundle is not yet on the official Spec Kit catalog, the user first adds the Trasgo project's self-hosted catalog source (a raw file on GitHub) with `install-allowed` policy, then installs the bundle. After installation, running the bundle list command confirms the bundle is present with the correct version and component count.

**Why this priority**: This is the core value proposition — the bundle MUST be installable through Spec Kit's standard catalog and bundle management tools via a self-hosted catalog source. Without this, the bundle has no distribution path.

**Independent Test**: Can be fully tested by adding the Trasgo catalog source, running the install command against a clean Spec Kit project, and verifying the bundle appears in the list output.

**Acceptance Scenarios**:

1. **Given** a directory with an initialized Spec Kit project, **When** the user adds the Trasgo catalog source via `specify bundle catalog add <url> --policy install-allowed` and then runs the bundle install command with the Trasgo Spec Kit bundle identifier, **Then** the bundle installs successfully and all declared components are applied to the project.
2. **Given** a successful installation, **When** the user runs the bundle list command, **Then** the Trasgo Spec Kit bundle appears with its version, component count, and install timestamp.
3. **Given** a project that already has the Trasgo bundle installed, **When** the user runs the install command again, **Then** the installation is idempotent — no duplicate components are created and no errors occur.
4. **Given** a directory that is not yet a Spec Kit project, **When** the user runs `specify bundle install` with the Trasgo bundle identifier (after adding the catalog source), **Then** the project is initialized first and then the bundle is installed in a single command.

---

### Edge Cases

- What happens when the user attempts to install the bundle in a directory that is not a Spec Kit project? The install command MUST initialize the project first, then install the bundle.
- What happens when the bundle targets a specific integration but the project uses a different one? The install MUST abort with no changes and a clear error message.
- What happens when the catalog source is unreachable during install? The install MUST fail with a clear network error; no partial state is written.
- What happens when a component declared in the bundle manifest cannot be resolved in any catalog? The install MUST fail, and components installed during that run are removed on a best-effort basis.
- What happens when the user runs bundle validate on the Trasgo bundle manifest? It MUST report whether the manifest is well-formed and all component references resolve.
- What happens when the user has not added the Trasgo catalog source before attempting install by catalog id? The install MUST fail with a clear error indicating the bundle identifier is not found in any active catalog.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST produce a valid `bundle.yml` manifest with metadata (`id`, `name`, `version`, `role`), requirements (`speckit_version`), and a `provides` section declaring the `/trasgospec` skill as the initial component with a pinned version.
- **FR-002**: The bundle MUST be installable via `specify bundle install` using either a catalog identifier or a local path to the bundle directory, manifest file, or built `.zip` artifact.
- **FR-003**: After installation, `specify bundle list` MUST display the Trasgo Spec Kit bundle with its version, component count, and install timestamp.
- **FR-004**: Installation MUST be idempotent — components already present are skipped without error.
- **FR-008**: `specify bundle validate` MUST confirm the bundle manifest is well-formed and all component references resolve.
- **FR-009**: `specify bundle build` MUST produce a versioned `.zip` artifact that can be installed directly.
- **FR-010**: The bundle MUST record provenance for every component it installs, enabling clean removal and update tracking.
- **FR-011**: Failed installations MUST NOT leave orphaned provenance records; partially installed components MUST be removed on a best-effort basis.
- **FR-012**: The bundle MUST work with the catalog stack (project, user, built-in scopes) for discovery and resolution.
- **FR-013**: The project MUST include a catalog JSON file in the repository that is accessible as a raw file via GitHub, with `schema_version` and a `bundles` object keyed by bundle ID containing the Trasgo entry (`id`, `name`, `description`, `version`, `role`, `download_url`).
- **FR-014**: The bundle MUST include a `/trasgospec` skill that outputs a hello/greeting message when invoked, serving as a minimal testable component to verify the install flow.
- **FR-015**: The bundle MUST NOT include default Spec Kit assets (templates, scripts, default workflows) that are already provided by `specify init`. It MUST only declare custom components.

### Key Entities

- **Bundle Manifest** (`bundle.yml`): Declares the bundle's identity (`id`, `name`, `version`, `role`), requirements (`speckit_version`), target integration (`claude`), and the `provides` section listing custom components with pinned versions. For the initial scaffold, the only provided component is the `/trasgospec` skill.
- **Catalog File** (`catalog.json`): A JSON file hosted as a raw GitHub file with `schema_version` and a `bundles` object keyed by bundle ID. Each entry includes `id`, `name`, `description`, `version`, `role`, and `download_url` pointing to the built `.zip` artifact.
- **Catalog Source**: A project-scoped catalog registration added by the consumer via `specify bundle catalog add <raw-github-url> --policy install-allowed`, enabling discovery and installation.
- **Trasgospec Skill**: The `/trasgospec` command — a minimal skill that outputs a hello message. Serves as the testable proof that the bundle install flow works end-to-end.
- **Provenance Record**: Per-component tracking data written at install time, linking each installed component back to the bundle that contributed it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can discover, install, and verify the Trasgo Spec Kit bundle in under 5 minutes starting from a clean Spec Kit project.
- **SC-002**: After installation, 100% of declared components are present and functional in the target project.
- **SC-003**: Running the install command a second time completes without errors and without duplicating any components.
- **SC-005**: The bundle passes validation (`specify bundle validate`) with zero errors when all referenced components are available.

## Assumptions

- The target user has Spec Kit installed (at the version specified in `bundle.yml` requirements) and is familiar with its CLI tools (`specify` commands).
- The project uses the Spec Kit bundle management infrastructure (catalogs, manifests, provenance) as documented — no custom tooling is required.
- The Trasgo Spec Kit bundle composes only existing Spec Kit primitives; it introduces no custom runtime behavior (per Constitution Principle I). The `/trasgospec` hello command is a skill (a Spec Kit component type), not custom runtime code.
- This is a scaffold bundle — the initial version contains only the `/trasgospec` test skill. More capabilities will be added in future versions.
- The existing Spec Kit assets in this repository (templates, scripts, workflows, skills) are default assets from `specify init` and MUST NOT be included in the bundle's `provides` section.
- The bundle targets the `claude` integration exclusively. Projects using a different integration will be rejected at install time.
- The Trasgo bundle is not on the official Spec Kit catalog initially; distribution relies on a self-hosted catalog JSON file in the GitHub repository, accessed via raw.githubusercontent.com.
- The GitHub repository hosting the catalog file and release artifacts is publicly accessible (or accessible to the target audience).
