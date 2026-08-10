# Feature Specification: Fix Flow-Nudge Default Execution

**Feature Branch**: `012-fix-flow-nudge-default`

**Created**: 2026-08-10

**Status**: Planning

**Input**: User description: "Bugfix — continuation of 009-spec-lifecycle-management. Flow-nudge hooks are registered as optional: true, which means the skill hook processor only displays a suggestion block instead of auto-executing the command. PRs are never created automatically."

## Problem Statement *(mandatory)*

**Pain Point**: The flow-nudge hooks (`after_plan`, `after_implement`, `after_analyze`, `after_discovery`) are registered with `optional: true` in the extension manifest. The Spec Kit hook processing logic only auto-executes mandatory hooks (`optional: false`) — optional hooks are rendered as passive suggestion blocks ("To execute: /command"). This means flow-nudge never actually runs during the workflow, so PRs are never created, marked ready, or flagged for final review automatically.

**Who**: Any user running the trasgospec workflow who expects PR lifecycle actions (draft creation, mark-ready, final-review nudge) to happen automatically at workflow milestones.

**Current Alternatives**: Users must manually notice the suggestion block in the output and then run `/speckit-trasgospec-flow-nudge` themselves. Most users miss this entirely.

**Desired Outcome**: Flow-nudge hooks execute automatically by default at each workflow milestone. When `gh` CLI is unavailable or when a user explicitly overrides the hook to `optional: true` in their local configuration, the command falls back to displaying a suggestion block instead.

**Continuation**: This is a bugfix continuation of [009-spec-lifecycle-management](../009-spec-lifecycle-management/spec.md), which introduced the lifecycle status system and hook-driven transitions. The flow-nudge hooks were configured as optional during that feature's implementation, but the intended behavior was automatic execution.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Flow-Nudge Runs Automatically at Workflow Milestones (Priority: P1)

When a user completes a workflow phase (plan, implement, analyze, discovery), the flow-nudge hook executes automatically as a mandatory post-hook, suggesting or performing the appropriate PR action without user intervention.

**Why this priority**: This is the core bug — the hook never runs. Fixing the default is the entire purpose of this feature.

**Independent Test**: Can be tested by running a skill (e.g., `/speckit-plan`) on a feature branch and verifying that flow-nudge executes automatically during the post-hook phase rather than displaying as a passive suggestion.

**Acceptance Scenarios**:

1. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.flow-nudge` under `after_plan` with `optional: false`, **When** a user completes `/speckit-plan`, **Then** the flow-nudge command is auto-executed by the hook processor (not merely displayed as a suggestion).
2. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.flow-nudge` under `after_implement` with `optional: false`, **When** a user completes `/speckit-implement`, **Then** the flow-nudge command is auto-executed.
3. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.flow-nudge` under `after_analyze` with `optional: false`, **When** a user completes `/speckit-analyze`, **Then** the flow-nudge command is auto-executed.
4. **Given** the bundle's `extension.yml` registers `speckit.trasgospec.flow-nudge` under `after_discovery` with `optional: false`, **When** a user completes `/speckit-trasgospec-discovery`, **Then** the flow-nudge command is auto-executed.

---

### User Story 2 - Graceful Fallback When gh Is Unavailable (Priority: P2)

When flow-nudge runs automatically but the `gh` CLI is not installed, the command displays a suggestion block with the manual command instead of failing.

**Why this priority**: Not all users have `gh` installed. The command must degrade gracefully rather than error out when running as a mandatory hook.

**Independent Test**: Can be tested by removing `gh` from PATH and running a workflow phase, verifying the nudge displays a suggestion block with the manual command.

**Acceptance Scenarios**:

1. **Given** `gh` is not available on the system, **When** flow-nudge runs as a mandatory hook after `/speckit-plan`, **Then** it displays a suggestion block with the `gh pr create` command the user can run manually, and exits successfully (does not block the workflow).
2. **Given** `gh` is available but `gh_integration` is set to `false` in the extension config, **When** flow-nudge runs, **Then** it displays the suggestion block instead of executing `gh` commands.

---

### User Story 3 - User Override to Optional (Priority: P3)

A user who prefers not to receive automatic PR nudges can override the hook to `optional: true` in their local extension configuration, restoring the suggestion-only behavior.

**Why this priority**: Users should retain control over their workflow. The override mechanism is an existing Spec Kit capability that just needs to work correctly with the new default.

**Independent Test**: Can be tested by setting `optional: true` on a flow-nudge hook in the local extension config and verifying the hook is displayed as a suggestion rather than auto-executed.

**Acceptance Scenarios**:

1. **Given** a user has overridden `after_plan.flow-nudge` to `optional: true` in their local configuration, **When** the user completes `/speckit-plan`, **Then** the flow-nudge is displayed as an optional suggestion block ("To execute: /speckit-trasgospec-flow-nudge") and is not auto-executed.

---

### Edge Cases

- What happens if the flow-nudge script exits with a non-zero code during a mandatory hook? The hook processor should display the error but not block the overall workflow completion, since PR nudges are advisory.
- What happens if a PR already exists and is up to date? The flow-nudge script returns `suggested_action: none`, and the command displays nothing or a brief confirmation.
- What happens if the user is on the main branch when flow-nudge runs? The flow-nudge script detects no feature branch context and returns an appropriate no-action response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All `speckit.trasgospec.flow-nudge` hook registrations in the bundle's `extension.yml` MUST use `optional: false` as the default.
- **FR-002**: The installed copy of the extension manifest (`.specify/extensions/trasgospec/extension.yml`) MUST reflect the same `optional: false` default after bundle installation.
- **FR-003**: When `gh` CLI is unavailable or `gh_integration` is `false`, the flow-nudge command MUST display a suggestion block with the manual command and exit successfully (exit code 0).
- **FR-004**: Users MUST be able to override any flow-nudge hook to `optional: true` in their local extension configuration to restore suggestion-only behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the fix, 100% of workflow milestones that trigger flow-nudge hooks result in the flow-nudge command being auto-executed (not displayed as a suggestion) when using the default bundle configuration.
- **SC-002**: Users without `gh` CLI installed experience no workflow interruptions — flow-nudge degrades to a suggestion block without errors.
- **SC-003**: Users who override hooks to `optional: true` see suggestion blocks, confirming the override mechanism works.

## Assumptions

- The Spec Kit hook processor treats `optional: false` hooks as mandatory and auto-executes them, which is the documented behavior.
- The `gh` CLI graceful fallback is already implemented in the flow-nudge command and script — no changes needed to the command logic itself, only to the hook registration defaults.
- Users can override extension hook settings in their local configuration without modifying the bundle source, per existing Spec Kit extension override conventions.
- The flow-nudge script already exits with code 0 regardless of `gh` availability, so mandatory hook execution will not block workflow completion.
