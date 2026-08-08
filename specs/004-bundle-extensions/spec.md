# Feature Specification: Roadmap Visualization

**Feature Branch**: `004-bundle-extensions`

**Created**: 2026-08-08

**Status**: Complete

**Input**: Restructure the trasgo-spec-kit bundle so its two components (hello and roadmap) are registered as extensions with proper extension.yml manifests, enabling the spec-kit installer to recognize and install them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bundle Install Delivers Working Commands (Priority: P1)

A developer adds the trasgo-spec-kit catalog and runs `specify bundle install trasgospec`. After installation completes, the installer reports the correct number of contributed components and the bundle's commands are immediately available for use in the project.

**Why this priority**: This is the core value proposition — without successful component installation, the entire bundle is unusable. Currently the bundle installs with 0 components, meaning no functionality is delivered.

**Independent Test**: Install the bundle in a clean spec-kit project and verify the install summary shows contributed components and that commands are registered.

**Acceptance Scenarios**:

1. **Given** a spec-kit project with the trasgo-spec-kit catalog added, **When** the user runs `specify bundle install trasgospec`, **Then** the installer reports at least 1 extension added and the install count is non-zero.
2. **Given** the bundle is installed, **When** the user lists available commands, **Then** the trasgospec commands appear in the command list.
3. **Given** the bundle is already installed, **When** the user runs `specify bundle install trasgospec` again, **Then** the installer reports 0 added and the correct number already present (idempotent install).

---

### User Story 2 - Hello Command Verifies Installation (Priority: P2)

A developer who has installed the bundle invokes the hello command (`/speckit-trasgospec-hello`) to verify the bundle was installed correctly. The command responds with a confirmation message.

**Why this priority**: The hello command is the simplest verification path — it proves the extension mechanism works end-to-end without requiring any project state.

**Independent Test**: After bundle install, invoke `/speckit-trasgospec-hello` and confirm it produces the expected greeting.

**Acceptance Scenarios**:

1. **Given** the trasgospec bundle is installed, **When** the user invokes the hello command, **Then** the system responds with "Hello from Trasgo Spec Kit! Bundle install verified."
2. **Given** the trasgospec bundle is NOT installed, **When** the user attempts to invoke the hello command, **Then** the command is not found.

---

### User Story 3 - Roadmap Command Displays Feature Specs (Priority: P2)

A developer invokes the roadmap command (`/speckit-trasgospec-roadmap`) to see a consolidated table of all feature specs in the project. The command runs a script to scan specs and renders the results.

**Why this priority**: The roadmap command is the bundle's primary value-add feature. It depends on the same extension installation mechanism as the hello command but exercises the full command+script pattern.

**Independent Test**: In a project with at least one feature spec, invoke `/speckit-trasgospec-roadmap` and confirm a markdown table with spec data is rendered.

**Acceptance Scenarios**:

1. **Given** a project with feature specs in `specs/`, **When** the user invokes the roadmap command, **Then** a markdown table is displayed with ID, Title, Status, and Created columns.
2. **Given** a project with no feature specs, **When** the user invokes the roadmap command, **Then** a message indicates no features have been specified yet.
3. **Given** the bundle is installed, **When** the roadmap command runs, **Then** the associated script (`scan-specs.sh`) is executed from the correct path and its JSON output is parsed.

---

### Edge Cases

- What happens when the bundle is installed over a previous version that used skills instead of extensions? The install should cleanly contribute the new extensions regardless of prior skill-based installs.
- What happens when the scan-specs script is missing or not executable? The roadmap command should report the error gracefully.
- What happens when bundle.yml declares an extension but the corresponding extension.yml manifest is missing from the bundle archive? The installer should report a validation error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The bundle MUST declare its components as extensions under `provides.extensions` in `bundle.yml`, not as skills under `provides.skills`.
- **FR-002**: Each extension MUST have an `extension.yml` manifest file located at `extensions/{extension-id}/extension.yml` within the bundle directory.
- **FR-003**: The trasgospec-hello extension manifest MUST register a command named `speckit.trasgospec.hello` that maps to its command definition file.
- **FR-004**: The trasgospec-roadmap extension manifest MUST register a command named `speckit.trasgospec.roadmap` that maps to its command definition file and declares its associated script.
- **FR-005**: Command definition files MUST follow the Spec Kit command format with YAML frontmatter containing `description` and, where applicable, `scripts` keys.
- **FR-006**: The hello command MUST be a pure-prompt command (no script) that responds with a verification message when invoked.
- **FR-007**: The roadmap command MUST delegate all deterministic work to the `scan-specs.sh` script and only handle presentation, following the constitution's separation of concerns pattern.
- **FR-008**: The bundle archive (zip) MUST include the complete extension directory structure so the installer can extract and register extensions.
- **FR-009**: Extension manifests MUST follow the `schema_version: "1.0"` format consistent with the Spec Kit extension schema.

### Key Entities

- **Extension Manifest** (`extension.yml`): Declares extension identity (id, name, version, description), required spec-kit version, and provided commands with their file paths and optional aliases.
- **Command Definition** (`.md` file): Contains YAML frontmatter (description, scripts) and markdown body with agent instructions for executing the command.
- **Bundle Manifest** (`bundle.yml`): Top-level manifest that lists all extensions provided by the bundle with their IDs and versions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `specify bundle install trasgospec` reports at least 1 component added (currently reports 0).
- **SC-002**: After installation, `specify bundle list` shows the correct component count matching the number of extensions declared in `bundle.yml`.
- **SC-003**: Both bundle commands are invocable after installation without additional manual setup.
- **SC-004**: The bundle passes `specify bundle validate` with no errors before and after the restructuring.

## Assumptions

- The Spec Kit installer recognizes extensions declared in `bundle.yml` under `provides.extensions` and looks for corresponding `extension.yml` manifests in the `extensions/` directory of the bundle archive.
- Skills declared under `provides.skills` are either not supported by the current installer version or are handled differently from extensions and presets (based on observed behavior of 0 components installed).
- The existing command file (`speckit.trasgospec.roadmap.md`) and script (`scan-specs.sh`) are functionally correct and only need to be relocated into the extension directory structure.
- The hello command can be implemented as a command definition file with prompt-only instructions (no backing script required), following the same pattern as the existing SKILL.md content.
- The bundle build automation (pre-push hook) will correctly package the new extension directory structure into the zip archive without modifications to the build scripts.
