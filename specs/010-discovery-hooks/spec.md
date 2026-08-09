# Feature Specification: Discovery Command Hooks

**Feature Branch**: `010-discovery-hooks`

**Created**: 2026-08-09

**Status**: In Progress

**Input**: User description: "Add before_discovery/after_discovery hook support to the discovery command, matching the pattern used by speckit-specify and speckit-plan. Enable other extensions to hook into discovery lifecycle. Use after_discovery to automate the Discovery → Opportunity transition."

## Problem Statement *(mandatory)*

**Pain Point**: The discovery command (`/speckit-trasgospec-discovery`) lacks the pre/post hook infrastructure that all other Spec Kit skills (specify, plan, tasks, implement, etc.) provide. This means extensions cannot hook into the discovery lifecycle — no branch enforcement before discovery, no automated status transitions after discovery, and no extensibility point for third-party extensions.

**Who**: Bundle developers who want to hook into the discovery lifecycle (e.g., trasgospec itself for status transitions and branch gating), and end users who expect consistent behavior across all Spec Kit skills.

**Current Alternatives**: The discovery command runs without any hook dispatch. Extensions that register hooks for other skills (e.g., flow-gate for branch enforcement) have no equivalent entry point for discovery. Users must manually manage any pre/post-discovery actions.

**Desired Outcome**: The discovery command dispatches `before_discovery` and `after_discovery` hooks using the same pattern as all other Spec Kit skills. Extensions can register hooks in `.specify/extensions.yml` under these keys and they execute identically to hooks on specify, plan, or any other skill. The `after_discovery` hook enables automating the Discovery → Opportunity status transition when the PRD passes a quality gate.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hook Dispatch in Discovery Command (Priority: P1)

When a user runs `/speckit-trasgospec-discovery`, the command checks `.specify/extensions.yml` for `before_discovery` and `after_discovery` hooks and dispatches them using the same protocol as other Spec Kit skills.

**Why this priority**: Without hook dispatch, no other functionality (status transitions, branch gating) can be automated around discovery. This is the enabling infrastructure.

**Independent Test**: Can be tested by registering a test hook under `before_discovery` in extensions.yml, running the discovery command, and verifying the hook was dispatched.

**Acceptance Scenarios**:

1. **Given** `.specify/extensions.yml` has a mandatory hook registered under `before_discovery`, **When** the user runs `/speckit-trasgospec-discovery`, **Then** the hook executes before the discovery conversation begins and the command waits for it to complete.
2. **Given** `.specify/extensions.yml` has an optional hook registered under `after_discovery`, **When** the discovery session completes and prd.md is written, **Then** the optional hook is presented to the user with its description and prompt.
3. **Given** `.specify/extensions.yml` has no hooks registered under `before_discovery` or `after_discovery`, **When** the user runs `/speckit-trasgospec-discovery`, **Then** hook checking is skipped silently and the command proceeds normally.
4. **Given** a hook with `enabled: false` registered under `before_discovery`, **When** the user runs `/speckit-trasgospec-discovery`, **Then** the disabled hook is filtered out and not dispatched.

---

### User Story 2 - Discovery to Opportunity Transition via After Hook (Priority: P2)

After a discovery session completes and the PRD is finalized, the `after_discovery` hook triggers a status transition command that evaluates the PRD against a quality gate and advances the status from Discovery to Opportunity if the gate passes.

**Why this priority**: This automates the first lifecycle transition, closing the gap between the discovery skill and the lifecycle management feature. Without it, users must manually set the status after every discovery session.

**Independent Test**: Can be tested by completing a discovery session that produces a PRD with all required sections, and verifying the status field advances to "Opportunity".

**Acceptance Scenarios**:

1. **Given** a completed discovery session producing a PRD with all required sections (Pain Point, Who, Current Alternatives, Desired Outcome, Jobs to Be Done, Assumptions), **When** the `after_discovery` hook fires and the quality gate passes, **Then** the PRD's `**Status**` field updates from "Discovery" to "Opportunity".
2. **Given** a completed discovery session producing a PRD missing required sections, **When** the `after_discovery` hook fires and the quality gate fails, **Then** the PRD's `**Status**` field remains "Discovery" and the user is informed which sections are incomplete.

---

### User Story 3 - Branch Gating Before Discovery (Priority: P2)

The existing flow-gate hook can be registered under `before_discovery` to enforce GitHub Flow branch discipline before starting a discovery session, consistent with how it gates all other skills.

**Why this priority**: Consistency. Every other skill enforces branch gating. Discovery should not be an exception.

**Independent Test**: Can be tested by registering the flow-gate hook under `before_discovery`, running discovery from the main branch, and verifying the hook blocks or creates a feature branch.

**Acceptance Scenarios**:

1. **Given** flow-gate is registered as a mandatory hook under `before_discovery` and the user is on `main`, **When** the user runs `/speckit-trasgospec-discovery`, **Then** the flow-gate hook fires and handles branch creation/switching before discovery begins.
2. **Given** flow-gate is registered under `before_discovery` and the user is on the correct feature branch, **When** the user runs `/speckit-trasgospec-discovery`, **Then** the flow-gate hook passes silently and discovery proceeds.

---

### Edge Cases

- What happens when the discovery session is aborted before prd.md is written? The `after_discovery` hooks are not dispatched since the command did not complete successfully.
- What happens when a mandatory `before_discovery` hook fails? The discovery command does not proceed, matching the behavior of all other Spec Kit skills.
- What happens when `.specify/extensions.yml` is malformed? Hook checking is skipped silently and discovery proceeds normally.
- What happens when a hook has a non-empty `condition` field? The hook is skipped — condition evaluation is deferred to the HookExecutor implementation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The discovery command MUST check `.specify/extensions.yml` for hooks registered under the `hooks.before_discovery` key before starting the discovery conversation.
- **FR-002**: The discovery command MUST check `.specify/extensions.yml` for hooks registered under the `hooks.after_discovery` key after the PRD is finalized and written to disk.
- **FR-003**: Hook dispatch MUST follow the identical protocol used by speckit-specify and speckit-plan: filter disabled hooks, skip conditional hooks, classify as mandatory or optional, and execute/present accordingly.
- **FR-004**: Mandatory hooks MUST block command execution until they complete. Optional hooks MUST be presented to the user without blocking.
- **FR-005**: The `after_discovery` hooks MUST only fire when the discovery session completes successfully (prd.md written). Aborted sessions MUST NOT trigger after hooks.
- **FR-006**: Hook command names MUST use the dot-to-hyphen mapping convention (e.g., `speckit.trasgospec.flow-gate` → `/speckit-trasgospec-flow-gate`).
- **FR-007**: The hook infrastructure MUST be added to both the bundle command file (`speckit.trasgospec.discovery.md`) and the skill file (`SKILL.md`) to keep them in sync.

### Key Entities

- **Hook Registration**: An entry in `.specify/extensions.yml` under `hooks.before_discovery` or `hooks.after_discovery`, following the same schema as all other hook registrations (extension, command, enabled, optional, priority, prompt, description, condition).
- **Discovery Lifecycle**: The execution phases of the discovery command: pre-hooks → discovery conversation → prd.md write → post-hooks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of hooks registered under `before_discovery` and `after_discovery` in extensions.yml are dispatched correctly when the discovery command runs.
- **SC-002**: The discovery command's hook behavior is indistinguishable from other Spec Kit skills — a developer registering a hook for discovery follows the exact same process as registering one for specify or plan.
- **SC-003**: The flow-gate hook can be registered under `before_discovery` and functions identically to its registration under other `before_*` keys.
- **SC-004**: After a successful discovery session, the `after_discovery` hook fires and can trigger downstream actions (e.g., status transition).

## Assumptions

- The `.specify/extensions.yml` schema already supports arbitrary hook keys — adding `before_discovery` and `after_discovery` requires no schema changes.
- The hook dispatch protocol is consistent across all Spec Kit skills and can be replicated by copying the established pattern from speckit-plan.
- The discovery command's bundle command file and skill file are kept in sync — changes to hook support must be applied to both.
- The quality gate for Discovery → Opportunity transition will be implemented as part of the lifecycle management feature (spec 009), not in this spec. This spec only provides the hook infrastructure that makes it possible.
