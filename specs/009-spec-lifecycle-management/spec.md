# Feature Specification: Spec Lifecycle Management

**Feature Branch**: `009-spec-lifecycle-management`

**Created**: 2026-08-09

**Status**: Draft

**Input**: User description: "specs/009-spec-lifecycle-management/prd.md"

## Problem Statement *(mandatory)*

**Pain Point**: Trasgospec provides roadmap visualization and a full specify → plan → tasks → implement workflow, but there is no structured lifecycle tracking for specs. The status field exists in spec.md but has no defined values, no transitions, and never changes as work progresses through phases. This makes it impossible to see at a glance where each feature stands or identify bottlenecks across the portfolio.

**Who**: Teams and solo practitioners using trasgospec for spec-driven development. Two personas — product (creates ideas and PRDs) and engineering (drives specs through implementation) — may be the same person, but the lifecycle enforces a collaboration contract between product thinking and engineering execution regardless of team size.

**Current Alternatives**: No status tracking exists today. The `**Status**` field in spec.md is freeform and never updated during the project. Spec Kit leaves it open to users. Users track phase informally by knowing which artifacts exist.

**Desired Outcome**: Every feature on the roadmap displays a well-defined lifecycle phase. Users can see which features are in discovery, which are ready to develop, which are blocked, and which are delivered — all from a single roadmap view. Agents automatically advance status as they complete workflow phases, and flag features as blocked when human decisions are needed.

## Clarifications

### Session 2026-08-09

- Q: How should the system preserve the previous phase when blocked? → A: Git history is the source of truth. The status command writes "Blocked" directly; to unblock, it reads the prior `**Status**` value from git log. No extra fields or sidecar files.
- Q: How should scan-specs.sh extract the feature title from PRD-only features? → A: Match both `# Feature Specification:` and `# PRD:` heading patterns for title extraction.
- Q: What is the canonical casing for lifecycle phase values? → A: Title case. Canonical values: Discovery, Opportunity, Planning, Ready to Dev, In Progress, In Review, Delivered, Blocked.
- Q: What should the status management command be named? → A: `trasgospec.roadmap.status.change`, invoked as `/trasgospec-roadmap-status-change`.
- Q: Which hooks trigger which phase transitions? → A: `before_specify` → Planning, `after_plan` → Ready to Dev, `before_tasks` → In Progress, `after_implement` → In Review. Remaining transitions (Discovery, Opportunity, Delivered, Blocked) are manual via `/trasgospec-roadmap-status-change`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Roadmap Shows Lifecycle Status for All Features (Priority: P1)

A user runs the roadmap command and sees every feature — including PRD-only ideas still in discovery — with its current lifecycle phase displayed. This gives them a single portfolio view to orchestrate their work.

**Why this priority**: Without visibility, the entire feature is moot. The roadmap is the primary surface where lifecycle data is consumed.

**Independent Test**: Can be tested by creating features with different artifacts (prd-only, spec+plan, spec+plan+tasks) and verifying the roadmap displays the correct status for each.

**Acceptance Scenarios**:

1. **Given** a project with three features: one with only prd.md (status: discovery), one with spec.md+plan.md (status: planning), and one with all artifacts (status: in-progress), **When** the user runs the roadmap command, **Then** all three features appear with their respective lifecycle status.
2. **Given** a feature directory contains both prd.md and spec.md, **When** the roadmap script scans for status, **Then** it reads `**Status**` from spec.md (spec takes precedence over prd).
3. **Given** a feature directory contains only prd.md with `**Status**: Discovery`, **When** the roadmap script scans, **Then** the feature appears on the roadmap with status "Discovery".

---

### User Story 2 - Automated Status Transitions via Hooks (Priority: P2)

When a user runs a Spec Kit skill (e.g., `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`), the feature's status automatically advances to the corresponding lifecycle phase via pre/post hooks.

**Why this priority**: Manual status updates create friction and are easily forgotten. Automation ensures status is always current without user effort.

**Independent Test**: Can be tested by running a skill on a feature and verifying the status field in spec.md has been updated to the expected phase.

**Acceptance Scenarios**:

1. **Given** a feature with status "Opportunity", **When** the user runs `/speckit-specify` (triggering `before_specify` hook), **Then** the status advances to "Planning".
2. **Given** a feature with status "Planning", **When** the user runs `/speckit-plan` and it completes (triggering `after_plan` hook), **Then** the status advances to "Ready to Dev".
3. **Given** a feature with status "Ready to Dev", **When** the user runs `/speckit-tasks` (triggering `before_tasks` hook), **Then** the status advances to "In Progress".
4. **Given** a feature with status "In Progress", **When** the user runs `/speckit-implement` and it completes (triggering `after_implement` hook), **Then** the status advances to "In Review".

---

### User Story 3 - Manual Status Management Command (Priority: P2)

A user or agent can manually set a feature's status using a dedicated command, enabling transitions that aren't tied to artifact creation — such as marking a feature as blocked or delivered.

**Why this priority**: Not all transitions are artifact-driven. Blocked requires human judgment, and delivered depends on merge state. A manual command covers these gaps and provides override capability.

**Independent Test**: Can be tested by running the status command with different arguments and verifying the status field updates correctly in the target artifact.

**Acceptance Scenarios**:

1. **Given** a feature in any phase, **When** the user runs `/trasgospec-roadmap-status-change blocked`, **Then** the `**Status**` field updates to "Blocked".
2. **Given** a blocked feature, **When** the user runs `/trasgospec-roadmap-status-change unblock`, **Then** the status reverts to the phase it was in before being blocked (retrieved from git history).
3. **Given** a feature in "In Review", **When** the user runs `/trasgospec-roadmap-status-change delivered`, **Then** the status updates to "Delivered".
4. **Given** a feature, **When** the user runs `/trasgospec-roadmap-status-change` with an invalid phase name, **Then** the system rejects the input and displays the valid phase options.

---

### User Story 4 - Agents Flag Blocked Status (Priority: P3)

When an agent running a workflow encounters a decision point that requires human input, it sets the feature status to "blocked". The human sees blocked features highlighted on the roadmap and can act on them.

**Why this priority**: This closes the feedback loop between autonomous agent execution and human oversight. Without it, agents stall silently.

**Independent Test**: Can be tested by simulating an agent workflow that encounters a decision point and verifying the status changes to blocked and appears as such on the roadmap.

**Acceptance Scenarios**:

1. **Given** an agent running `/speckit-implement` on a feature, **When** the agent encounters a decision requiring human input, **Then** it sets the feature status to "Blocked" with context about what decision is needed.
2. **Given** a blocked feature on the roadmap, **When** the user views the roadmap, **Then** the blocked feature is clearly identifiable among other features.

---

### User Story 5 - PRD Quality Gate for Opportunity Status (Priority: P3)

A PRD in discovery status can advance to opportunity status only when it passes a quality gate — specifically, it has a complete requirements list and validated assumptions.

**Why this priority**: The gate ensures only well-formed PRDs advance to engineering, maintaining the collaboration contract between product thinking and engineering execution.

**Independent Test**: Can be tested by creating PRDs with varying completeness and verifying only those meeting the quality criteria can advance to opportunity.

**Acceptance Scenarios**:

1. **Given** a PRD with all required sections populated (Pain Point, Who, Current Alternatives, Desired Outcome, Jobs to Be Done, Assumptions), **When** the quality gate is evaluated, **Then** the PRD is eligible to advance to "Opportunity".
2. **Given** a PRD missing the Assumptions section, **When** the quality gate is evaluated, **Then** the PRD remains in "Discovery" and the user is informed which sections are incomplete.

---

### Edge Cases

- What happens when a feature directory contains neither prd.md nor spec.md? The feature is excluded from the roadmap.
- What happens when a status field contains an unrecognized value? The roadmap displays it as-is with a warning indicator.
- What happens when a user tries to advance status backward (e.g., from "in-progress" to "planning")? The system allows it — status is not a one-way ratchet. Users may need to revisit earlier phases.
- What happens when multiple features are blocked? All blocked features appear on the roadmap, allowing the user to prioritize which bottlenecks to resolve first.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `scan-specs.sh` script MUST read the `**Status**` field from both prd.md and spec.md files, with spec.md taking precedence when both exist in a feature directory.
- **FR-002**: The `scan-specs.sh` script MUST include features that have only a prd.md (no spec.md) in the scan results, extracting the title from the `# PRD:` heading pattern.
- **FR-003**: The system MUST define exactly 7 forward lifecycle phases in title case: Discovery, Opportunity, Planning, Ready to Dev, In Progress, In Review, Delivered.
- **FR-004**: The system MUST support a lateral "Blocked" state that can be applied at any lifecycle phase.
- **FR-005**: When "Blocked" is set, the previous phase is recoverable from git history. To unblock, the status command reads the prior `**Status**` value from git log. No additional metadata fields are required.
- **FR-006**: The status management command `trasgospec.roadmap.status.change` (invoked as `/trasgospec-roadmap-status-change`) MUST allow users and agents to set, advance, and revert lifecycle status.
- **FR-007**: The status management command MUST validate input against the defined lifecycle phases and reject invalid values.
- **FR-008**: The following hooks MUST automatically advance feature status: `before_specify` → Planning, `after_plan` → Ready to Dev, `before_tasks` → In Progress, `after_implement` → In Review. Remaining transitions (Discovery, Opportunity, Delivered, Blocked) are manual via `/trasgospec-roadmap-status-change`.
- **FR-009**: The `**Status**` field in prd.md MUST follow the same format as the `**Status**` field in spec.md, enabling uniform parsing.
- **FR-010**: The roadmap command MUST display features from all lifecycle phases, including PRD-only features in discovery and opportunity.
- **FR-011**: Agents MUST be able to set a feature's status to "blocked" with contextual information about the decision needed.
- **FR-012**: A PRD quality gate MUST evaluate completeness of required sections (Pain Point, Who, Current Alternatives, Desired Outcome, Jobs to Be Done, Assumptions) before allowing advancement from discovery to opportunity.

### Key Entities

- **Lifecycle Phase**: One of the 7 defined forward phases (Discovery, Opportunity, Planning, Ready to Dev, In Progress, In Review, Delivered) plus the lateral "Blocked" state. All values use title case. Persisted as the value of the `**Status**` field in prd.md or spec.md.
- **Feature**: A unit of work represented by a directory under `specs/`, containing at minimum a prd.md or spec.md with a `**Status**` field. Features progress through lifecycle phases.
- **Quality Gate**: A set of completeness criteria applied to a PRD to determine eligibility for advancement from discovery to opportunity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of features on the roadmap display a valid lifecycle phase — no features appear with a missing or undefined status.
- **SC-002**: Users can identify all blocked features from the roadmap in a single glance, without opening individual spec files.
- **SC-003**: Status transitions triggered by Spec Kit skills complete without requiring any manual status updates from the user.
- **SC-004**: PRD-only features (pre-spec) are visible on the roadmap with the same fidelity as fully-specced features.
- **SC-005**: A user can determine what action to take next on any feature by reading its lifecycle status on the roadmap.

## Assumptions

- The existing `scan-specs.sh` script can be extended to scan prd.md files without breaking backward compatibility with existing spec-only features.
- The `**Status**` field in prd.md will use the same markdown pattern (`**Status**: <value>`) as spec.md, requiring no parser changes beyond scanning an additional file.
- The hooks infrastructure in `.specify/extensions.yml` supports adding new pre/post hooks for status transitions without modifying Spec Kit core.
- The status management command follows the extension two-part pattern (command file + script file) per the project constitution.
- Backward status transitions (e.g., from in-progress back to planning) are valid and intentional — the lifecycle is not a strict forward-only state machine.
- Features with unrecognized status values are displayed as-is on the roadmap rather than being hidden, to avoid data loss.
