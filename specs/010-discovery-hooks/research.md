# Research: Discovery Command Hooks

**Feature**: 010-discovery-hooks | **Date**: 2026-08-09

## Research Questions & Decisions

### R1: Which command handles the after_discovery status transition?

**Decision**: Reuse `speckit.trasgospec.status`

**Rationale**: The status command already handles all lifecycle transitions (Discovery, Planning, In Progress, Ready to Dev, In Review, Complete, Delivered). It reads the current status from the spec/PRD file and applies the appropriate transition. No new command needed.

**Alternatives considered**: A dedicated discovery-specific transition script was considered but rejected — it would duplicate status management logic already in `status-change.sh`.

### R2: Does the quality gate for Discovery-to-Opportunity need implementation here?

**Decision**: No — out of scope

**Rationale**: Per spec Assumptions: "The quality gate for Discovery to Opportunity transition will be implemented as part of the lifecycle management feature (spec 009), not in this spec. This spec only provides the hook infrastructure that makes it possible."

**Alternatives considered**: None — the spec is explicit about this boundary.

### R3: Should SKILL.md be modified despite being auto-generated?

**Decision**: Yes — modify both command file and SKILL.md

**Rationale**: Per FR-007: "The hook infrastructure MUST be added to both the bundle command file and the skill file to keep them in sync." The SKILL.md won't be regenerated until the next `specify bundle install`, so manual update is required for immediate functionality.

**Alternatives considered**: Modifying only the command file and relying on bundle reinstall — rejected because users would not get hook support until they reinstall the bundle.

### R4: What priority values should the new hooks use?

**Decision**: flow-gate: 10, status: 5, flow-nudge: 10

**Rationale**: Matches the existing pattern from `before_tasks` and `after_plan` where status hooks (priority 5) run before flow hooks (priority 10). Lower priority number = runs first.

**Alternatives considered**: None — consistency with existing hooks is non-negotiable.

### R5: Does before_discovery need a status hook?

**Decision**: No — only flow-gate

**Rationale**: Discovery is the initial lifecycle phase. There is no prior status to advance FROM. The status hook only makes sense as `after_discovery` (Discovery to Opportunity). Other `before_*` hooks (e.g., `before_tasks`) have status hooks because they advance from an intermediate status.

**Alternatives considered**: Adding a status hook to `before_discovery` for symmetry — rejected because there's no valid transition to make before discovery begins.

### R6: Hook dispatch pattern source

**Decision**: Copy verbatim from `speckit-plan/SKILL.md` and `speckit-specify/SKILL.md`

**Rationale**: These are the canonical implementations. The pattern is identical across both, differing only in the hook key name (`before_plan` vs `before_specify`). The discovery command will substitute `before_discovery` and `after_discovery`.

**Alternatives considered**: None — consistency is the primary requirement (SC-002).
