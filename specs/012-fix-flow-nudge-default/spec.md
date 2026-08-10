# Feature Specification: Fix Flow-Nudge Default Execution

**Feature Branch**: `012-fix-flow-nudge-default`

**Created**: 2026-08-10

**Status**: In Progress

**Input**: User description: "Bugfix — continuation of 009-spec-lifecycle-management. Flow-nudge hooks are registered as optional: true, which means the skill hook processor only displays a suggestion block instead of auto-executing the command. PRs are never created automatically."

## Problem Statement *(mandatory)*

**Pain Point**: The deliver hooks (formerly `flow-nudge`) registered under `after_plan`, `after_implement`, `after_analyze`, and `after_discovery` are set to `optional: true` in the extension manifest. The Spec Kit hook processing logic only auto-executes mandatory hooks (`optional: false`) — optional hooks are rendered as passive suggestion blocks ("To execute: /command"). This means deliver never actually runs during the workflow, so PRs are never created, marked ready, or flagged for final review automatically.

**Who**: Any user running the trasgospec workflow who expects PR lifecycle actions (draft creation, mark-ready, final-review nudge) to happen automatically at workflow milestones.

**Current Alternatives**: Users must manually notice the suggestion block in the output and then run the deliver command themselves. Most users miss this entirely.

**Desired Outcome**: The deliver command executes automatically by default at each workflow milestone — creating PRs, marking them ready, or flagging final review — without prompting for confirmation. The `optional` flag in extensions.yml serves as the user's feature flag: when set to `optional: true`, the command displays a suggestion block instead. When `gh` CLI is unavailable, the command also falls back to the suggestion block. All artifact-producing commands use templates distributed with the bundle: `pr-template.md` for PR title/body and `commit-template.md` for commit message format. Users can override any template via the Spec Kit preset resolution stack.

**Continuation**: This is a bugfix continuation of [009-spec-lifecycle-management](../009-spec-lifecycle-management/spec.md), which introduced the lifecycle status system and hook-driven transitions. The deliver hooks were configured as optional during that feature's implementation, but the intended behavior was automatic execution.

## Clarifications

### Session 2026-08-10

- Q: When mandatory (`optional: false`), should the deliver command prompt for confirmation before creating a PR? → A: No. It must execute without asking. The `optional` flag in extensions.yml is the user's feature flag — when mandatory, the command creates the PR directly and reports any errors back.
- Q: Where should the PR body template (`pr-template.md`) be placed in the bundle for distribution? → A: In the bundle's preset `templates/` directory, following the Spec Kit template resolution stack (`specify preset resolve pr-template`). Users can override it in `.specify/templates/overrides/`.
- Q: When `gh pr create` fails, should the command block the workflow or set status to Blocked? → A: Display the error and continue workflow without status change. PR creation failure is transient.
- Q: Should the PR title format be hardcoded or customizable? → A: Title pattern in `pr-template.md` frontmatter (e.g., `title: "feat({{spec_dir}}): {{spec_title}}"`). Both title and body customizable in one file.
- Q: Which placeholders should pr-template.md support? → A: Only `{{spec_title}}` and `{{spec_summary}}`. Branch, PR number, and other context is already on GitHub.
- Q: Should the command be renamed now that it executes PR actions instead of nudging? → A: Yes. Rename `flow-nudge` to `deliver` (`speckit.trasgospec.deliver`). The command now delivers PRs, not nudges. Artifact renames deferred to implementation.
- Q: Should the template pattern extend to other artifact-producing commands? → A: Yes. `trasgospec.commit` must use a `commit-template.md` that defaults to the current format (`<path> - <description>`, one line per file, no tags/prefixes/trailers). Users can override it via the preset resolution stack.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deliver Runs Automatically at Workflow Milestones (Priority: P1)

When a user completes a workflow phase (plan, implement, analyze, discovery), the deliver hook executes automatically as a mandatory post-hook, performing the appropriate PR action (create draft, mark ready, flag final review) without prompting for confirmation. The `optional` flag in extensions.yml is the user's feature flag to opt out.

**Why this priority**: This is the core bug — the hook never runs, and even when manually invoked, it prompts for confirmation instead of just acting.

**Independent Test**: Can be tested by running a skill (e.g., `/speckit-plan`) on a feature branch and verifying that deliver executes automatically during the post-hook phase, creates the draft PR without prompting, and reports the result.

**Acceptance Scenarios**:

1. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.deliver` under `after_plan` with `optional: false`, **When** a user completes `/speckit-plan`, **Then** the deliver command is auto-executed and creates a draft PR without prompting for confirmation.
2. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.deliver` under `after_implement` with `optional: false`, **When** a user completes `/speckit-implement`, **Then** the deliver command is auto-executed and marks the PR as ready for review without prompting.
3. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.deliver` under `after_analyze` with `optional: false`, **When** a user completes `/speckit-analyze`, **Then** the deliver command is auto-executed.
4. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.deliver` under `after_discovery` with `optional: false`, **When** a user completes `/speckit-trasgospec-discovery`, **Then** the deliver command is auto-executed.

---

### User Story 2 - Graceful Fallback When gh Is Unavailable (Priority: P2)

When deliver runs automatically but the `gh` CLI is not installed, the command displays a suggestion block with the manual command instead of failing.

**Why this priority**: Not all users have `gh` installed. The command must degrade gracefully rather than error out when running as a mandatory hook.

**Independent Test**: Can be tested by removing `gh` from PATH and running a workflow phase, verifying deliver displays a suggestion block with the manual command.

**Acceptance Scenarios**:

1. **Given** `gh` is not available on the system, **When** deliver runs as a mandatory hook after `/speckit-plan`, **Then** it displays a suggestion block with the `gh pr create` command the user can run manually, and exits successfully (does not block the workflow).
2. **Given** `gh` is available but `gh_integration` is set to `false` in the extension config, **When** deliver runs, **Then** it displays the suggestion block instead of executing `gh` commands.

---

### User Story 3 - User Override to Optional (Priority: P3)

A user who prefers not to receive automatic PR delivery can override the hook to `optional: true` in their local extension configuration, restoring the suggestion-only behavior.

**Why this priority**: Users should retain control over their workflow. The override mechanism is an existing Spec Kit capability that just needs to work correctly with the new default.

**Independent Test**: Can be tested by setting `optional: true` on a deliver hook in the local extension config and verifying the hook is displayed as a suggestion rather than auto-executed.

**Acceptance Scenarios**:

1. **Given** a user has overridden `after_plan.deliver` to `optional: true` in their local configuration, **When** the user completes `/speckit-plan`, **Then** deliver is displayed as an optional suggestion block ("To execute: /speckit-trasgospec-deliver") and is not auto-executed.

---

### User Story 4 - PR Body Driven by Template (Priority: P2)

The PR body content is generated from a `pr-template.md` template distributed with the bundle, allowing users to customize PR output without modifying bundle code.

**Why this priority**: Consistent, customizable PR bodies improve team workflows. The template system is a core Spec Kit primitive that should be used for any generated artifact.

**Independent Test**: Can be tested by verifying the bundle includes `pr-template.md` in its preset, that `specify preset resolve pr-template` resolves it, and that the deliver command uses the resolved template to compose the PR body.

**Acceptance Scenarios**:

1. **Given** the bundle distributes a `pr-template.md` in its preset templates, **When** a user installs the bundle, **Then** `specify preset resolve pr-template` resolves to the installed template.
2. **Given** the deliver command creates a draft PR, **When** it composes the PR body, **Then** it uses the resolved `pr-template.md` to structure the body content, interpolating spec metadata (title, summary).
3. **Given** a user has placed a custom `pr-template.md` in `.specify/templates/overrides/`, **When** deliver creates a PR, **Then** it uses the user's override template instead of the bundle default.

---

### User Story 5 - Commit Message Driven by Template (Priority: P2)

The commit message format is generated from a `commit-template.md` template distributed with the bundle, allowing users to customize commit output without modifying bundle code. The default template produces the current format: one line per file, `<repo-relative-path> - <description>`, no tags, prefixes, or trailers.

**Why this priority**: Commit message format is a team convention. The template system allows teams to adopt their own conventions (e.g., conventional commits, Jira ticket prefixes) without forking the bundle.

**Independent Test**: Can be tested by verifying the bundle includes `commit-template.md` in its preset, that `specify preset resolve commit-template` resolves it, and that the commit command uses the resolved template to compose the commit message.

**Acceptance Scenarios**:

1. **Given** the bundle distributes a `commit-template.md` in its preset templates, **When** a user installs the bundle, **Then** `specify preset resolve commit-template` resolves to the installed template.
2. **Given** the commit command creates a commit, **When** it composes the commit message, **Then** it uses the resolved `commit-template.md` to structure the message, defaulting to the current one-line-per-file format.
3. **Given** a user has placed a custom `commit-template.md` in `.specify/templates/overrides/`, **When** the commit command creates a commit, **Then** it uses the user's override template instead of the bundle default.

---

### Edge Cases

- What happens if the deliver script exits with a non-zero code during a mandatory hook? The hook processor should display the error but not block the overall workflow completion, since PR delivery is advisory.
- What happens if a PR already exists and is up to date? The deliver script returns `suggested_action: none`, and the command displays nothing or a brief confirmation.
- What happens if the user is on the main branch when deliver runs? The deliver script detects no feature branch context and returns an appropriate no-action response.
- What happens if `gh pr create` fails (auth expired, rate limited, network error)? The command displays the error and continues the workflow without changing feature status. PR creation failures are transient and do not warrant a "Blocked" lifecycle state.
- What happens if `pr-template.md` cannot be resolved? The command falls back to a hardcoded minimal PR body (title + spec summary).
- What happens if `commit-template.md` cannot be resolved? The commit command falls back to the hardcoded default format (`<path> - <description>`, one line per file).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The command `speckit.trasgospec.flow-nudge` MUST be renamed to `speckit.trasgospec.deliver` (invoked as `/speckit-trasgospec-deliver`, alias `trasgospec.deliver`). All associated artifacts (command file, script, hook registrations) MUST use the new name.
- **FR-002**: All `speckit.trasgospec.deliver` hook registrations in the bundle's `extension.yml` MUST use `optional: false` as the default.
- **FR-003**: The installed copy of the extension manifest (`.specify/extensions/trasgospec/extension.yml`) MUST reflect the same `optional: false` default after bundle installation.
- **FR-004**: When invoked, the deliver command MUST execute the suggested PR action (create draft, mark ready) without prompting for user confirmation. The `optional` flag in extensions.yml is the user's feature flag to opt out.
- **FR-005**: When `gh` CLI is unavailable or `gh_integration` is `false`, the deliver command MUST display a suggestion block with the manual command and exit successfully (exit code 0).
- **FR-006**: Users MUST be able to override any deliver hook to `optional: true` in their local extension configuration to restore suggestion-only behavior.
- **FR-007**: The bundle MUST distribute a `pr-template.md` in its preset templates directory, resolved via `specify preset resolve pr-template`.
- **FR-008**: The deliver command MUST use the resolved `pr-template.md` to compose both PR title (from YAML frontmatter `title` field) and PR body (from markdown body), interpolating only `{{spec_title}}` and `{{spec_summary}}` placeholders. If the template cannot be resolved, it MUST fall back to a minimal hardcoded title and body.
- **FR-009**: When `gh pr create` or `gh pr ready` fails, the command MUST display the error message and continue the workflow without changing feature lifecycle status.
- **FR-010**: The bundle MUST distribute a `commit-template.md` in its preset templates directory, resolved via `specify preset resolve commit-template`.
- **FR-011**: The `trasgospec.commit` command MUST use the resolved `commit-template.md` to compose commit messages. The default template MUST produce the current format: one line per file (`<repo-relative-path> - <description>`), no tags, prefixes, or trailers. If the template cannot be resolved, it MUST fall back to the same hardcoded default format.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the fix, 100% of workflow milestones that trigger deliver hooks result in the deliver command being auto-executed (not displayed as a suggestion) when using the default bundle configuration.
- **SC-002**: Users without `gh` CLI installed experience no workflow interruptions — deliver degrades to a suggestion block without errors.
- **SC-003**: Users who override hooks to `optional: true` see suggestion blocks, confirming the override mechanism works.

## Assumptions

- The Spec Kit hook processor treats `optional: false` hooks as mandatory and auto-executes them, which is the documented behavior.
- The `gh` CLI graceful fallback is already implemented in the deliver script — it exits code 0 regardless of `gh` availability, so mandatory hook execution will not block workflow completion.
- Users can override extension hook settings in their local configuration without modifying the bundle source, per existing Spec Kit extension override conventions.
- The deliver command file (`.md`) needs updating to remove confirmation prompts and add template resolution — the script (`.sh`) gathers state only and needs no changes beyond renaming.
- The bundle can provide a preset by adding a `presets/` directory to the bundle structure and declaring it in `bundle.yml` under `provides.presets`. The template then installs via `specify bundle install`.
- The Spec Kit template resolution order is: project overrides → installed presets → installed extensions → core templates.
