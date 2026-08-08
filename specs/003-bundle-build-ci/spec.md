# Feature Specification: Bundle Build CI

**Feature Branch**: `003-bundle-build-ci`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "given developer made changes to bundle directory, when developer pushes to git, then 'specify bundle validate --path bundle && specify bundle build --path bundle --output .' must be run to create the zip file and the catalog.json must be updated to point to it"

## Clarifications

### Session 2026-08-08

- Q: Should the download URL in catalog.json point to the zip file committed in the repository or use GitHub tag archive URLs? → A: Raw file URL — commit zip to repo, download URL uses raw.githubusercontent.com path inferred from the main branch.
- Q: Should this run as a CI pipeline or a local git hook? → A: Local git hook — runs where everything is already installed, no CI dependency.
- Q: Should the hook trigger on pre-push or pre-commit? → A: Pre-push hook — runs before push, blocks push on validation failure.
- Q: Should artifacts be amended into the outgoing commit or committed separately? → A: New separate commit — create a "chore: build bundle" commit before push proceeds.
- Q: How should the git hook be installed since .git/hooks/ is not tracked? → A: Via a repo-level setup script and `core.hooksPath` configuration. This is internal developer tooling, not a bundle feature exposed to consumers.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Bundle Build on Push (Priority: P1)

A developer working on the Trasgo Spec Kit bundle makes changes to files inside the `bundle/` directory (commands, scripts, skills, or the bundle manifest). When they push those changes, a local pre-push git hook automatically validates the bundle structure and builds a distributable zip artifact. The resulting zip file is placed in the repository root, `catalog.json` is updated with a download URL pointing to the raw file on the main branch, and a separate commit is created with these artifacts before the push proceeds.

**Why this priority**: This is the core automation that eliminates manual build steps and ensures every pushed bundle change results in a valid, distributable artifact. Without this, developers must remember to run validation and build commands manually, risking broken or stale distributions.

**Independent Test**: Can be fully tested by pushing a change to any file in the `bundle/` directory and verifying that the zip artifact is produced, a separate build commit is created, and `catalog.json` references the correct raw.githubusercontent.com URL.

**Acceptance Scenarios**:

1. **Given** a developer has modified files in the `bundle/` directory, **When** they push to the remote repository, **Then** the pre-push hook runs `specify bundle validate --path bundle` to check bundle integrity, followed by `specify bundle build --path bundle --output .` to produce the zip artifact in the repository root.
2. **Given** the bundle build completes successfully, **When** the zip artifact is produced, **Then** `catalog.json` is updated so the bundle entry's download URL points to the raw file on the main branch (e.g., `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<zip-filename>`).
3. **Given** the build artifacts are ready, **When** the hook creates the build commit, **Then** a new separate commit containing the zip and updated `catalog.json` is added before the push proceeds.
4. **Given** the bundle validation fails, **When** the push is attempted, **Then** the build step is skipped, the push is blocked, and the developer is notified of the validation errors.

---

### User Story 2 - No Build for Non-Bundle Changes (Priority: P2)

A developer pushes changes that do not touch the `bundle/` directory (e.g., documentation updates, test changes, spec edits). The pre-push hook detects that no bundle-related files changed and skips the validation and build steps entirely, allowing the push to proceed without delay.

**Why this priority**: Avoiding unnecessary builds reduces push time and prevents false notifications. It ensures the automation only runs when meaningful bundle changes occur.

**Independent Test**: Can be tested by pushing a commit that only modifies files outside the `bundle/` directory and verifying that no validation, build, or catalog update occurs and no additional commit is created.

**Acceptance Scenarios**:

1. **Given** a developer has only modified files outside the `bundle/` directory, **When** they push to the remote repository, **Then** the pre-push hook skips validation, build, and catalog update steps entirely.

---

### User Story 3 - Developer Hook Setup (Priority: P2)

A developer clones the Trasgo Spec Kit repository and runs a repo-level setup script to activate the pre-push hook. The script configures `git core.hooksPath` to point to a tracked hooks directory (e.g., `.githooks/`), making the automated bundle build active. This is a one-time developer setup step, not a bundle feature exposed to consumers.

**Why this priority**: Without the hook activated, the automated build from US1 never triggers. This is the delivery mechanism that makes the entire feature functional. Ranked P2 because it's a one-time prerequisite, not the ongoing automation itself.

**Independent Test**: Can be tested by running the setup script in a fresh clone and verifying that the pre-push hook is active and triggers on push.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repository, **When** they run the setup script, **Then** git is configured to use the tracked hooks directory and the pre-push hook is active.
2. **Given** the hook setup has already been performed, **When** the developer runs the setup script again, **Then** the configuration is applied idempotently without errors.
3. **Given** the developer is not in a git repository, **When** they run the setup script, **Then** the script exits with a clear error message.

---

### User Story 4 - Catalog Version Consistency (Priority: P3)

When the pre-push hook updates `catalog.json`, the version recorded in the catalog entry matches the version declared in `bundle/bundle.yml`. This ensures consumers always see accurate version information and can trust the catalog as a source of truth.

**Why this priority**: Version mismatches between the manifest and catalog erode trust and can cause installation failures. This story ensures data integrity across distribution artifacts.

**Independent Test**: Can be tested by comparing the `version` field in `bundle/bundle.yml` against the `version` field in the updated `catalog.json` after a successful build.

**Acceptance Scenarios**:

1. **Given** a successful bundle build has completed, **When** `catalog.json` is updated, **Then** the version in the catalog entry matches the version declared in `bundle/bundle.yml`.
2. **Given** a successful bundle build has completed, **When** `catalog.json` is updated, **Then** the bundle description in the catalog entry matches the description in `bundle/bundle.yml`.

---

### Edge Cases

- What happens when `bundle/bundle.yml` has a syntax error that prevents version extraction?
- How does the system handle a push that includes both bundle and non-bundle changes?
- What happens if the `specify` CLI is not installed on the developer's machine?
- What happens if `catalog.json` does not exist yet when the hook runs?
- What happens if the pre-push hook's auto-commit fails (e.g., dirty working tree)?
- What happens if the developer has not run the setup script (hooks directory not configured)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pre-push git hook MUST run `specify bundle validate --path bundle` on every push that includes changes to files within the `bundle/` directory.
- **FR-002**: The pre-push hook MUST run `specify bundle build --path bundle --output .` after successful validation to produce the distributable zip artifact.
- **FR-003**: The pre-push hook MUST update `catalog.json` after a successful build so the bundle entry reflects the current version and the download URL points to the raw file on the main branch.
- **FR-004**: The pre-push hook MUST skip validation and build steps when a push contains no changes to files within the `bundle/` directory.
- **FR-005**: The pre-push hook MUST block the push and notify the developer when bundle validation fails.
- **FR-006**: The pre-push hook MUST ensure the version in `catalog.json` matches the version declared in `bundle/bundle.yml` after every successful build.
- **FR-007**: The pre-push hook MUST verify that the Spec Kit CLI (`specify`) is available locally before attempting validation or build operations.
- **FR-008**: The pre-push hook MUST create a new separate commit containing the zip artifact and updated `catalog.json` before the push proceeds, keeping the developer's original commits intact.
- **FR-009**: The download URL in `catalog.json` MUST follow the pattern `https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/main/<zip-filename>`, inferred from the repository's remote URL and main branch.
- **FR-010**: The pre-push hook script MUST be stored in a tracked directory (e.g., `.githooks/`) so it is version-controlled and shared across all developers.
- **FR-011**: A repo-level setup script MUST configure `git core.hooksPath` to point to the tracked hooks directory, activating the pre-push hook.
- **FR-012**: The setup script MUST be idempotent — running it multiple times produces the same result without errors.

### Key Entities

- **Bundle Artifact**: The zip file produced by `specify bundle build`, placed in the repository root. Represents the distributable unit that consumers download and install.
- **Catalog Entry**: The JSON object in `catalog.json` describing a bundle's metadata (id, name, version, description, download URL). Serves as the discovery mechanism for bundle consumers. The download URL points to the raw file on the main branch.
- **Bundle Manifest**: The `bundle/bundle.yml` file that declares the bundle's identity, version, and component set. Acts as the source of truth for bundle metadata.
- **Pre-Push Hook**: The local git hook that orchestrates validation, build, catalog update, and auto-commit before a push proceeds. Stored in a tracked hooks directory, activated via `core.hooksPath`.
- **Setup Script**: A repo-level script that configures the developer's local git to use the tracked hooks directory. Internal developer tooling, not part of the distributed bundle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every push that modifies `bundle/` files triggers validation and build via the local pre-push hook with zero manual intervention.
- **SC-002**: After a successful build, `catalog.json` accurately reflects the current bundle version and a valid raw.githubusercontent.com download URL.
- **SC-003**: Pushes that do not modify `bundle/` files complete without triggering any bundle-related processing or additional commits.
- **SC-004**: Validation failures block the push and produce clear, actionable error output visible to the developer.
- **SC-005**: Build artifacts are committed in a separate commit distinct from the developer's original work.
- **SC-006**: A new developer can activate the hook setup with a single script invocation after cloning the repository.

## Assumptions

- The Spec Kit CLI (`specify`) is installed locally on the developer's machine.
- The `catalog.json` download URL uses the raw.githubusercontent.com pattern, inferred from the git remote URL and main branch name.
- The developer's working tree is clean enough to allow the hook to create an auto-commit (no conflicting staged changes).
- The pre-push hook only processes pushes to the main branch; pushes to feature branches do not trigger the build.
- The `bundle/` directory path is stable and will not change without a corresponding update to the hook.
- The git remote uses a GitHub-hosted repository (required for the raw.githubusercontent.com URL pattern).
- Developers are expected to run the setup script once after cloning; this is documented in the project README or contributing guide.
