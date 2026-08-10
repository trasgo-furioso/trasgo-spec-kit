# Feature Specification: Bundle Install

**Feature Branch**: `001-bundle-install`

**Created**: 2026-08-07

**Status**: Delivered

**Input**: User description: "given a project directory, when a user installs trasgo spec kit bundle using speckit catalog and bundle management tools, then trasgo bundle appears on the bundle list"

## Clarifications

### Session 2026-08-07

- Q: How is the bundle distributed before it is on the official catalog? → A: Self-hosted catalog file on GitHub with `specify bundle catalog add <url> --policy install-allowed`. The catalog file is hosted as a raw file in the repository (raw.githubusercontent.com).
- Q: Does the bundle target the `claude` integration specifically or is it integration-agnostic? → A: Claude-specific. The bundle targets the `claude` integration only.
- Q: What components does the bundle declare? → A: Minimal scaffold — a single custom `/trasgospec` hello command for testing the install flow. Existing repo files are default Spec Kit assets and MUST NOT be included in the bundle. More capabilities will be added later.

### Session 2026-08-08 (Build Automation)

- Q: Should the download URL in catalog.json point to the zip file committed in the repository or use GitHub tag archive URLs? → A: Raw file URL — commit zip to repo, download URL uses raw.githubusercontent.com path inferred from the main branch.
- Q: Should this run as a CI pipeline or a local git hook? → A: Local git hook — runs where everything is already installed, no CI dependency.
- Q: Should the hook trigger on pre-push or pre-commit? → A: Pre-push hook — runs before push, blocks push on validation failure.
- Q: Should artifacts be amended into the outgoing commit or committed separately? → A: New separate commit — create a "chore: build bundle" commit before push proceeds.
- Q: How should the git hook be installed since .git/hooks/ is not tracked? → A: Via a repo-level setup script and `core.hooksPath` configuration. This is internal developer tooling, not a bundle feature exposed to consumers.

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

### User Story 2 - Automated Bundle Build on Push (Priority: P1)

A developer working on the Trasgo Spec Kit bundle makes changes to files inside the `bundle/` directory (commands, scripts, skills, or the bundle manifest). When they push those changes, a local pre-push git hook automatically validates the bundle structure and builds a distributable zip artifact. The resulting zip file is placed in the repository root, `catalog.json` is updated with a download URL pointing to the raw file on the main branch, and a separate commit is created with these artifacts before the push proceeds.

**Why this priority**: This is the core automation that eliminates manual build steps and ensures every pushed bundle change results in a valid, distributable artifact. Without this, developers must remember to run validation and build commands manually, risking broken or stale distributions.

**Independent Test**: Can be fully tested by pushing a change to any file in the `bundle/` directory and verifying that the zip artifact is produced, a separate build commit is created, and `catalog.json` references the correct raw.githubusercontent.com URL.

**Acceptance Scenarios**:

1. **Given** a developer has modified files in the `bundle/` directory, **When** they push to the remote repository, **Then** the pre-push hook runs `specify bundle validate --path bundle` to check bundle integrity, followed by `specify bundle build --path bundle --output .` to produce the zip artifact in the repository root.
2. **Given** the bundle build completes successfully, **When** the zip artifact is produced, **Then** `catalog.json` is updated so the bundle entry's download URL points to the raw file on the main branch (e.g., `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<zip-filename>`).
3. **Given** the build artifacts are ready, **When** the hook creates the build commit, **Then** a new separate commit containing the zip and updated `catalog.json` is added before the push proceeds.
4. **Given** the bundle validation fails, **When** the push is attempted, **Then** the build step is skipped, the push is blocked, and the developer is notified of the validation errors.

---

### User Story 3 - No Build for Non-Bundle Changes (Priority: P2)

A developer pushes changes that do not touch the `bundle/` directory (e.g., documentation updates, test changes, spec edits). The pre-push hook detects that no bundle-related files changed and skips the validation and build steps entirely, allowing the push to proceed without delay.

**Why this priority**: Avoiding unnecessary builds reduces push time and prevents false notifications. It ensures the automation only runs when meaningful bundle changes occur.

**Independent Test**: Can be tested by pushing a commit that only modifies files outside the `bundle/` directory and verifying that no validation, build, or catalog update occurs and no additional commit is created.

**Acceptance Scenarios**:

1. **Given** a developer has only modified files outside the `bundle/` directory, **When** they push to the remote repository, **Then** the pre-push hook skips validation, build, and catalog update steps entirely.

---

### User Story 4 - Developer Hook Setup (Priority: P2)

A developer clones the Trasgo Spec Kit repository and runs a repo-level setup script to activate the pre-push hook. The script configures `git core.hooksPath` to point to a tracked hooks directory (e.g., `.githooks/`), making the automated bundle build active. This is a one-time developer setup step, not a bundle feature exposed to consumers.

**Why this priority**: Without the hook activated, the automated build from US2 never triggers. This is the delivery mechanism that makes the entire feature functional. Ranked P2 because it's a one-time prerequisite, not the ongoing automation itself.

**Independent Test**: Can be tested by running the setup script in a fresh clone and verifying that the pre-push hook is active and triggers on push.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repository, **When** they run the setup script, **Then** git is configured to use the tracked hooks directory and the pre-push hook is active.
2. **Given** the hook setup has already been performed, **When** the developer runs the setup script again, **Then** the configuration is applied idempotently without errors.
3. **Given** the developer is not in a git repository, **When** they run the setup script, **Then** the script exits with a clear error message.

---

### User Story 5 - Catalog Version Consistency (Priority: P3)

When the pre-push hook updates `catalog.json`, the version recorded in the catalog entry matches the version declared in `bundle/bundle.yml`. This ensures consumers always see accurate version information and can trust the catalog as a source of truth.

**Why this priority**: Version mismatches between the manifest and catalog erode trust and can cause installation failures. This story ensures data integrity across distribution artifacts.

**Independent Test**: Can be tested by comparing the `version` field in `bundle/bundle.yml` against the `version` field in the updated `catalog.json` after a successful build.

**Acceptance Scenarios**:

1. **Given** a successful bundle build has completed, **When** `catalog.json` is updated, **Then** the version in the catalog entry matches the version declared in `bundle/bundle.yml`.
2. **Given** a successful bundle build has completed, **When** `catalog.json` is updated, **Then** the bundle description in the catalog entry matches the description in `bundle/bundle.yml`.

---

### Edge Cases

- What happens when the user attempts to install the bundle in a directory that is not a Spec Kit project? The install command MUST initialize the project first, then install the bundle.
- What happens when the bundle targets a specific integration but the project uses a different one? The install MUST abort with no changes and a clear error message.
- What happens when the catalog source is unreachable during install? The install MUST fail with a clear network error; no partial state is written.
- What happens when a component declared in the bundle manifest cannot be resolved in any catalog? The install MUST fail, and components installed during that run are removed on a best-effort basis.
- What happens when the user runs bundle validate on the Trasgo bundle manifest? It MUST report whether the manifest is well-formed and all component references resolve.
- What happens when the user has not added the Trasgo catalog source before attempting install by catalog id? The install MUST fail with a clear error indicating the bundle identifier is not found in any active catalog.
- What happens when `bundle/bundle.yml` has a syntax error that prevents version extraction? The hook MUST block the push with a clear error message.
- How does the system handle a push that includes both bundle and non-bundle changes? The hook MUST detect the bundle changes and run the build.
- What happens if the `specify` CLI is not installed on the developer's machine? The hook MUST block the push with a clear error indicating the CLI is missing.
- What happens if `catalog.json` does not exist yet when the hook runs? The hook MUST create it from scratch with the full structure.
- What happens if the pre-push hook's auto-commit fails (e.g., dirty working tree)? The hook MUST block the push with a clear error message.
- What happens if the developer has not run the setup script (hooks directory not configured)? The hook simply does not run — pushes proceed normally without build automation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST produce a valid `bundle.yml` manifest with metadata (`id`, `name`, `version`, `role`), requirements (`speckit_version`), and a `provides` section declaring the `/trasgospec` skill as the initial component with a pinned version.
- **FR-002**: The bundle MUST be installable via `specify bundle install` using either a catalog identifier or a local path to the bundle directory, manifest file, or built `.zip` artifact.
- **FR-003**: After installation, `specify bundle list` MUST display the Trasgo Spec Kit bundle with its version, component count, and install timestamp.
- **FR-004**: Installation MUST be idempotent — components already present are skipped without error.
- **FR-005**: `specify bundle validate` MUST confirm the bundle manifest is well-formed and all component references resolve.
- **FR-006**: `specify bundle build` MUST produce a versioned `.zip` artifact that can be installed directly.
- **FR-007**: The bundle MUST record provenance for every component it installs, enabling clean removal and update tracking.
- **FR-008**: Failed installations MUST NOT leave orphaned provenance records; partially installed components MUST be removed on a best-effort basis.
- **FR-009**: The bundle MUST work with the catalog stack (project, user, built-in scopes) for discovery and resolution.
- **FR-010**: The project MUST include a catalog JSON file in the repository that is accessible as a raw file via GitHub, with `schema_version` and a `bundles` object keyed by bundle ID containing the Trasgo entry (`id`, `name`, `description`, `version`, `role`, `download_url`).
- **FR-011**: The bundle MUST include a `/trasgospec` skill that outputs a hello/greeting message when invoked, serving as a minimal testable component to verify the install flow.
- **FR-012**: The bundle MUST NOT include default Spec Kit assets (templates, scripts, default workflows) that are already provided by `specify init`. It MUST only declare custom components.
- **FR-013**: The pre-push git hook MUST run `specify bundle validate --path bundle` on every push that includes changes to files within the `bundle/` directory.
- **FR-014**: The pre-push hook MUST run `specify bundle build --path bundle --output .` after successful validation to produce the distributable zip artifact.
- **FR-015**: The pre-push hook MUST update `catalog.json` after a successful build so the bundle entry reflects the current version and the download URL points to the raw file on the main branch.
- **FR-016**: The pre-push hook MUST skip validation and build steps when a push contains no changes to files within the `bundle/` directory.
- **FR-017**: The pre-push hook MUST block the push and notify the developer when bundle validation fails.
- **FR-018**: The pre-push hook MUST ensure the version in `catalog.json` matches the version declared in `bundle/bundle.yml` after every successful build.
- **FR-019**: The pre-push hook MUST verify that the Spec Kit CLI (`specify`) is available locally before attempting validation or build operations.
- **FR-020**: The pre-push hook MUST create a new separate commit containing the zip artifact and updated `catalog.json` before the push proceeds, keeping the developer's original commits intact.
- **FR-021**: The download URL in `catalog.json` MUST follow the pattern `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<zip-filename>`, inferred from the repository's remote URL and main branch.
- **FR-022**: The pre-push hook script MUST be stored in a tracked directory (e.g., `.githooks/`) so it is version-controlled and shared across all developers.
- **FR-023**: A repo-level setup script MUST configure `git core.hooksPath` to point to the tracked hooks directory, activating the pre-push hook.
- **FR-024**: The setup script MUST be idempotent — running it multiple times produces the same result without errors.

### Key Entities

- **Bundle Manifest** (`bundle.yml`): Declares the bundle's identity (`id`, `name`, `version`, `role`), requirements (`speckit_version`), target integration (`claude`), and the `provides` section listing custom components with pinned versions. For the initial scaffold, the only provided component is the `/trasgospec` skill.
- **Catalog File** (`catalog.json`): A JSON file hosted as a raw GitHub file with `schema_version` and a `bundles` object keyed by bundle ID. Each entry includes `id`, `name`, `description`, `version`, `role`, and `download_url` pointing to the built `.zip` artifact.
- **Catalog Source**: A project-scoped catalog registration added by the consumer via `specify bundle catalog add <raw-github-url> --policy install-allowed`, enabling discovery and installation.
- **Trasgospec Skill**: The `/trasgospec` command — a minimal skill that outputs a hello message. Serves as the testable proof that the bundle install flow works end-to-end.
- **Provenance Record**: Per-component tracking data written at install time, linking each installed component back to the bundle that contributed it.
- **Bundle Artifact**: The zip file produced by `specify bundle build`, placed in the repository root. Represents the distributable unit that consumers download and install.
- **Pre-Push Hook**: The local git hook that orchestrates validation, build, catalog update, and auto-commit before a push proceeds. Stored in a tracked hooks directory, activated via `core.hooksPath`.
- **Setup Script**: A repo-level script that configures the developer's local git to use the tracked hooks directory. Internal developer tooling, not part of the distributed bundle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can discover, install, and verify the Trasgo Spec Kit bundle in under 5 minutes starting from a clean Spec Kit project.
- **SC-002**: After installation, 100% of declared components are present and functional in the target project.
- **SC-003**: Running the install command a second time completes without errors and without duplicating any components.
- **SC-004**: The bundle passes validation (`specify bundle validate`) with zero errors when all referenced components are available.
- **SC-005**: Every push that modifies `bundle/` files triggers validation and build via the local pre-push hook with zero manual intervention.
- **SC-006**: After a successful build, `catalog.json` accurately reflects the current bundle version and a valid raw.githubusercontent.com download URL.
- **SC-007**: Pushes that do not modify `bundle/` files complete without triggering any bundle-related processing or additional commits.
- **SC-008**: Validation failures block the push and produce clear, actionable error output visible to the developer.
- **SC-009**: Build artifacts are committed in a separate commit distinct from the developer's original work.
- **SC-010**: A new developer can activate the hook setup with a single script invocation after cloning the repository.

## Assumptions

- The target user has Spec Kit installed (at the version specified in `bundle.yml` requirements) and is familiar with its CLI tools (`specify` commands).
- The project uses the Spec Kit bundle management infrastructure (catalogs, manifests, provenance) as documented — no custom tooling is required.
- The Trasgo Spec Kit bundle composes only existing Spec Kit primitives; it introduces no custom runtime behavior (per Constitution Principle I). The `/trasgospec` hello command is a skill (a Spec Kit component type), not custom runtime code.
- This is a scaffold bundle — the initial version contains only the `/trasgospec` test skill. More capabilities will be added in future versions.
- The existing Spec Kit assets in this repository (templates, scripts, workflows, skills) are default assets from `specify init` and MUST NOT be included in the bundle's `provides` section.
- The bundle targets the `claude` integration exclusively. Projects using a different integration will be rejected at install time.
- The Trasgo bundle is not on the official Spec Kit catalog initially; distribution relies on a self-hosted catalog JSON file in the GitHub repository, accessed via raw.githubusercontent.com.
- The GitHub repository hosting the catalog file and release artifacts is publicly accessible (or accessible to the target audience).
- The Spec Kit CLI (`specify`) is installed locally on the developer's machine.
- The `catalog.json` download URL uses the raw.githubusercontent.com pattern, inferred from the git remote URL and main branch name.
- The developer's working tree is clean enough to allow the hook to create an auto-commit (no conflicting staged changes).
- The pre-push hook only processes pushes to the main branch; pushes to feature branches do not trigger the build.
- The `bundle/` directory path is stable and will not change without a corresponding update to the hook.
- The git remote uses a GitHub-hosted repository (required for the raw.githubusercontent.com URL pattern).
- Developers are expected to run the setup script once after cloning; this is documented in the project README or contributing guide.
