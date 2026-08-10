# Feature Specification: GitHub Flow Enforcement

**Feature Branch**: `005-github-flow-enforcement`

**Created**: 2026-08-08

**Status**: Delivered

**Input**: User description: "Enforce GitHub Flow branching discipline as a built-in part of trasgospec's core skills. Every spec-kit skill (specify, clarify, checklist, plan, tasks, implement, converge, analyze) gets flow-aware behavior: block execution on main branch (offer to create a feature branch derived from spec dir name like feat/NNN-slug), nudge PR creation at plan phase (draft) and implement phase (mark ready). A shared flow_context.sh script provides deterministic git state (current branch, is_main, branch age, commits behind main, PR status) as a JSON blob merged into each skill script's output. gh CLI integration is configurable via extension input gh_integration (boolean, default true) with three effective modes: gh available+enabled does full PR ops, gh missing falls back to output-only with warning, gh disabled outputs PR title/description/suggested-command only. Read-only commands (roadmap, hello) are not flow-aware."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Branch Gate via Hook (Priority: P1)

A developer using trasgospec runs any spec-kit skill (clarify, checklist, plan, tasks, implement, converge, analyze). Before the skill executes, a mandatory `before_*` hook fires automatically. The hook checks the current git branch. If the developer is on `main`, the hook blocks execution and offers to create a feature branch. The branch name is read from the `**Feature Branch**:` field in the active spec's `spec.md` file — it is used as-is with no prefix added. If the developer is already on a feature branch, the hook passes and the skill proceeds normally.

The specify skill is exempt from `before_*` gating because it creates the spec directory and `feature.json` that the gate depends on. Instead, specify has a mandatory `after_specify` hook that reads the newly created spec's `**Feature Branch**` field and creates/switches to that branch if the developer is not already on it.

This is implemented as a single extension command (`speckit.trasgospec.flow-gate`) registered as a mandatory hook: `after_specify` (create/switch branch) and `before_*` on the remaining seven phases (block on `main`). The hook follows the two-part extension pattern: a deterministic script gathers git state, and the command file interprets the result to gate or proceed.

**Why this priority**: This is the foundational behavior. Without branch gating, no other flow enforcement is possible. It ensures every piece of spec-driven work happens on a dedicated branch, which is the core GitHub Flow discipline.

**Independent Test**: Can be fully tested by running specify on `main` and verifying the `after_specify` hook creates and switches to the branch, then running another skill on `main` and verifying the `before_*` hook blocks. Delivers the core value of preventing undisciplined commits to `main`.

**Acceptance Scenarios**:

1. **Given** a developer runs `/speckit-specify` on `main`, **When** the specify skill completes and the `after_specify` hook fires, **Then** the hook reads the `**Feature Branch**` field from the new spec.md and creates/switches to that branch
2. **Given** the branch from `**Feature Branch**` already exists, **When** the `after_specify` hook fires, **Then** it switches to the existing branch without creating a new one
3. **Given** a developer is on the `main` branch, **When** they invoke any flow-aware skill other than specify, **Then** the mandatory `before_*` hook blocks execution and offers to create the branch named in spec.md
4. **Given** a developer is on the correct feature branch, **When** they invoke any flow-aware skill, **Then** the hook passes and the skill proceeds normally
5. **Given** a developer is on a branch that does not match the spec's `**Feature Branch**` value, **When** the hook fires, **Then** it warns about the mismatch but does not block execution
6. **Given** a developer is on a detached HEAD, **When** the hook fires, **Then** it blocks execution and explains that a named feature branch is required

---

### User Story 2 - PR Lifecycle Nudges via Hook (Priority: P2)

As a developer progresses through the spec-kit workflow, optional `after_*` hooks fire at key milestones to suggest PR actions. After completing the plan phase, the hook suggests opening a draft PR. After completing the implement phase, the hook suggests marking the PR as ready for review. After completing the analyze phase, the hook suggests the PR is ready for final review. Because these hooks are optional (`optional: true`), the developer can skip them.

This is implemented as a single extension command (`speckit.trasgospec.flow-nudge`) registered as an optional hook on `after_plan`, `after_implement`, and `after_analyze`. The command adapts its suggestion based on which phase triggered it and the current PR state.

**Why this priority**: PR lifecycle management turns the branch into a reviewable artifact. It is the second half of GitHub Flow after branch creation. Without it, branches exist but lack the collaboration structure.

**Independent Test**: Can be tested by running the plan, implement, and analyze skills on a feature branch and verifying the appropriate PR nudge appears at each phase.

**Acceptance Scenarios**:

1. **Given** a developer completes `/speckit-plan` on a feature branch with no open PR, **When** the optional `after_plan` hook fires, **Then** it suggests opening a draft PR with a proposed title and description
2. **Given** a developer completes `/speckit-implement` on a feature branch with a draft PR, **When** the optional `after_implement` hook fires, **Then** it suggests marking the PR as ready for review
3. **Given** a developer completes `/speckit-analyze` on a feature branch with a PR, **When** the optional `after_analyze` hook fires, **Then** it suggests the PR is ready for final review
4. **Given** a developer has already opened a non-draft PR at the plan phase, **When** `after_implement` fires, **Then** it recognizes the PR is already ready and skips the nudge
5. **Given** a developer declines the optional hook, **When** the skill completes, **Then** no PR action is taken and the skill reports success normally

---

### User Story 3 - Configurable gh CLI Integration (Priority: P2)

A developer configures whether trasgospec uses the `gh` CLI for automated PR operations. When enabled (default), the flow-nudge hook creates and updates PRs automatically. When disabled or when `gh` is not installed, the hook outputs the PR title, description, and suggested `gh` command so the developer can act manually.

**Why this priority**: Same priority as PR nudges because it determines how those nudges are delivered. The configurability ensures the feature works in environments without `gh` and respects developer preferences.

**Independent Test**: Can be tested by toggling `gh_integration` and verifying the hook either executes PR operations or outputs manual instructions.

**Acceptance Scenarios**:

1. **Given** `gh_integration` is `true` and `gh` is installed, **When** the flow-nudge hook suggests opening a draft PR, **Then** it creates the PR automatically using `gh pr create --draft`
2. **Given** `gh_integration` is `true` but `gh` is not installed, **When** the flow-nudge hook fires, **Then** it warns once that `gh` is not available and outputs the PR title, description, and copy-paste `gh` command
3. **Given** `gh_integration` is `false`, **When** the flow-nudge hook fires, **Then** it outputs the PR title, description, and copy-paste `gh` command without attempting to run `gh`
4. **Given** `gh_integration` is `true` and `gh` is installed, **When** the flow-nudge hook suggests marking a PR ready, **Then** it runs `gh pr ready` automatically

---

### User Story 4 - Flow Context Script (Priority: P1)

Both hook commands (`flow-gate` and `flow-nudge`) rely on a shared `flow_context.sh` script that gathers deterministic git state. The script reads the branch name from the `**Feature Branch**:` field in the active spec's `spec.md` (located via `feature.json`). It emits a JSON object containing: current branch name, whether it is `main`, the expected branch name from spec.md, whether the current branch matches it, branch age in days, number of commits behind `main`, and whether there are uncommitted changes. Each hook command sources this script and acts on the resulting context.

**Why this priority**: This is the data layer that enables both the gate and nudge hooks. Without a consistent flow context, each hook would need to independently query git state, leading to duplication and inconsistency.

**Independent Test**: Can be tested by running the flow context script directly and verifying its JSON output against known git state.

**Acceptance Scenarios**:

1. **Given** a repository on branch `005-github-flow-enforcement` that is 3 days old and 0 commits behind main, **When** the flow context script runs, **Then** it outputs valid JSON with `current_branch: "005-github-flow-enforcement"`, `is_main: false`, `branch_age_days: 3`, `commits_behind_main: 0`
2. **Given** a spec.md with `**Feature Branch**: \`005-github-flow-enforcement\``, **When** the flow context script runs on that branch, **Then** `spec_branch_match` is `true` and `expected_branch` is `"005-github-flow-enforcement"`
3. **Given** the current branch does not match the spec's `**Feature Branch**` value, **When** the flow context script runs, **Then** `spec_branch_match` is `false`
4. **Given** no `.specify/feature.json` exists, **When** the flow context script runs, **Then** it outputs flow context with `spec_branch_match` as `null`, `expected_branch` as `null`, and does not error
5. **Given** `feature.json` exists but spec.md has no `**Feature Branch**` field, **When** the flow context script runs, **Then** `expected_branch` is `null` and `spec_branch_match` is `null`

---

### User Story 5 - Read-Only Commands Excluded (Priority: P3)

Read-only trasgospec commands (`roadmap`, `hello`) are not flow-aware. No hooks are registered for these commands. They execute on any branch without gating, warnings, or flow context. This prevents unnecessary friction for informational commands.

**Why this priority**: Lowest priority because it is a constraint (what NOT to do) rather than a feature to build. It is important for usability but requires no new code — only the absence of hook registrations for these commands.

**Independent Test**: Can be tested by running `/speckit-trasgospec-roadmap` and `/speckit-trasgospec-hello` on `main` and verifying they execute without flow-related output.

**Acceptance Scenarios**:

1. **Given** a developer is on the `main` branch, **When** they run `/speckit-trasgospec-roadmap`, **Then** the command executes normally without branch warnings or blocks
2. **Given** a developer is on the `main` branch, **When** they run `/speckit-trasgospec-hello`, **Then** the command executes normally without branch warnings or blocks

---

### User Story 6 - Hook Registration on Bundle Install (Priority: P1)

When the trasgospec bundle is installed into a project, the bundle installation process registers the flow-gate and flow-nudge hooks in `.specify/extensions.yml`. The gate hook is registered as mandatory (`optional: false`) on `after_specify` and seven `before_*` phases (clarify, checklist, plan, tasks, implement, converge, analyze). The nudge hook is registered as optional (`optional: true`) on `after_plan`, `after_implement`, and `after_analyze`. This ensures flow enforcement is active immediately after installation with no additional configuration.

**Why this priority**: Without hook registration, the commands exist but never fire. This story is what makes enforcement automatic and built-in rather than opt-in.

**Independent Test**: Can be tested by installing the bundle into a clean project and verifying `extensions.yml` contains the expected hook entries.

**Acceptance Scenarios**:

1. **Given** a clean project with no hooks registered, **When** the trasgospec bundle is installed, **Then** `.specify/extensions.yml` contains a mandatory `after_specify` hook for `flow-gate`
2. **Given** a clean project with no hooks registered, **When** the trasgospec bundle is installed, **Then** `.specify/extensions.yml` contains mandatory `before_*` hooks for `flow-gate` on the seven remaining phases (clarify, checklist, plan, tasks, implement, converge, analyze)
3. **Given** a clean project with no hooks registered, **When** the trasgospec bundle is installed, **Then** `.specify/extensions.yml` contains optional `after_*` hooks for `flow-nudge` on plan, implement, and analyze phases
4. **Given** a project with existing hooks from other extensions, **When** trasgospec is installed, **Then** the flow hooks are added without overwriting existing hook entries

---

### Edge Cases

- What happens when the developer is on a detached HEAD (no branch)?
- What happens when the spec directory does not exist yet (first run of specify, before `feature.json` is written)?
- What happens when multiple spec directories exist and the active one is ambiguous?
- What happens when the feature branch already exists but points to a different spec?
- What happens when `gh` authentication has expired?
- What happens when the repository has no remote configured?
- What happens when the developer is on a branch that follows GitHub Flow conventions but was not created by trasgospec?
- What happens when a developer uninstalls the bundle — are hooks cleaned up?

## Requirements *(mandatory)*

### Functional Requirements

**Hook Architecture**

- **FR-001**: System MUST implement flow enforcement using the existing spec-kit hook mechanism (`before_*` and `after_*` hooks in `.specify/extensions.yml`), not by modifying individual skill scripts
- **FR-002**: System MUST provide a `speckit.trasgospec.flow-gate` extension command registered as a mandatory hook (`optional: false`) on `after_specify` (create/switch branch) and `before_clarify`, `before_checklist`, `before_plan`, `before_tasks`, `before_implement`, `before_converge`, `before_analyze` (block on `main`)
- **FR-003**: System MUST provide a `speckit.trasgospec.flow-nudge` extension command registered as an optional hook (`optional: true`) on `after_plan`, `after_implement`, and `after_analyze`
- **FR-004**: Both hook commands MUST follow the extension two-part pattern: a deterministic bash script (JSON on stdout, diagnostics on stderr, bash 3.2+ compatible) and a command markdown file with AI agent instructions

**Branch Gating (flow-gate)**

- **FR-005**: The flow-gate hook MUST block skill execution when the current branch is `main` and offer to create a feature branch
- **FR-006**: Feature branch names MUST be read from the `**Feature Branch**:` field in the active spec's `spec.md` and used as-is with no prefix added
- **FR-007**: On `after_specify`, the flow-gate hook MUST create and switch to the branch named in spec.md if the developer is not already on it; if the branch already exists, it MUST switch to it without creating a new one
- **FR-008**: The flow-gate hook MUST warn (but not block) when the current branch does not match the spec's `**Feature Branch**` value
- **FR-009**: The flow-gate hook MUST handle the case where no spec directory is active (e.g., `feature.json` does not exist) by skipping the branch-match check gracefully

**PR Nudges (flow-nudge)**

- **FR-010**: The flow-nudge hook MUST suggest opening a draft PR after the plan phase when no PR exists for the current branch
- **FR-011**: The flow-nudge hook MUST suggest marking a PR as ready for review after the implement phase when a draft PR exists
- **FR-012**: The flow-nudge hook MUST suggest the PR is ready for final review after the analyze phase
- **FR-013**: The flow-nudge hook MUST adapt its behavior based on which phase triggered it and the current PR state

**gh CLI Integration**

- **FR-014**: System MUST support a configurable `gh_integration` input (boolean, default `true`) that controls whether `gh` CLI is used for PR operations
- **FR-015**: When `gh_integration` is enabled and `gh` is installed, the flow-nudge hook MUST execute PR operations automatically
- **FR-016**: When `gh_integration` is enabled but `gh` is not installed, the system MUST warn once and fall back to output-only mode
- **FR-017**: When `gh_integration` is disabled, the system MUST output PR title, description, and suggested `gh` command without attempting to execute `gh`

**Flow Context**

- **FR-018**: System MUST provide a shared `flow_context.sh` script that emits a JSON object containing: `current_branch`, `is_main`, `expected_branch`, `spec_branch_match`, `branch_age_days`, `commits_behind_main`, `uncommitted_changes`
- **FR-019**: The `expected_branch` field MUST be read from the `**Feature Branch**:` field in the active spec's `spec.md`, extracted by pattern matching (same approach as `scan-specs.sh` uses for title and status)
- **FR-020**: The flow context script MUST be sourceable by both hook command scripts to avoid duplication of git state logic

**Scope Boundaries**

- **FR-021**: Read-only commands (`roadmap`, `hello`) MUST NOT have flow hooks registered
- **FR-022**: Hook registration MUST occur during bundle installation and MUST be idempotent

### Key Entities

- **Flow Context**: The deterministic git state snapshot produced by `flow_context.sh` — represents the branch, PR, and divergence state at the moment a hook fires
- **Flow-Gate Hook**: A mandatory `before_*` hook that checks branch state and blocks execution on `main`
- **Flow-Nudge Hook**: An optional `after_*` hook that suggests PR actions at workflow milestones
- **Hook Registration**: The entries in `.specify/extensions.yml` that bind hook commands to skill lifecycle phases

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of flow-aware skills trigger the mandatory gate hook before execution, blocking on `main` and allowing on feature branches
- **SC-002**: Developers receive PR lifecycle nudges at the correct phases (plan, implement, analyze) with zero false positives
- **SC-003**: The flow context script produces valid JSON output within 2 seconds on repositories with up to 10,000 commits
- **SC-004**: When `gh` is unavailable, the system provides a complete copy-paste command that the developer can use without modification
- **SC-005**: Read-only commands execute with no additional latency or output from flow enforcement
- **SC-006**: All flow context fields are accurate when compared against direct `git` command output
- **SC-007**: Bundle installation registers all hook entries idempotently — installing twice produces the same `extensions.yml` state

## Assumptions

- The project uses git as its version control system
- The `main` branch is the primary integration branch (not `master` or another name)
- The `.specify/feature.json` file is the authoritative source for the active spec directory
- Developers have git available in their PATH
- The `gh` CLI, when installed, is authenticated and has sufficient permissions for PR operations
- Branch age is calculated from the first commit on the branch, not the branch creation date (git does not track branch creation time)
- The branch name is whatever the developer writes in the `**Feature Branch**:` field of spec.md — no prefix is added or enforced
- The `**Feature Branch**:` field uses backtick-wrapped format: `**Feature Branch**: \`branch-name\``
- The existing spec-kit hook mechanism supports mandatory (`optional: false`) and optional (`optional: true`) hooks as documented in the skill templates
- The flow-nudge command infers its triggering phase from spec directory artifacts, not from hook mechanism context
