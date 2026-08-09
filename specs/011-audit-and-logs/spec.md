# Feature Specification: Audit and Logs

**Feature Branch**: `011-audit-and-logs`

**Created**: 2026-08-09

**Status**: Ready to Dev

**Input**: User description: "specs/011-audit-and-logs/prd.md"

## Problem Statement

**Pain Point**: Spec artifacts (prd.md, spec.md, plan.md, tasks.md) are created and modified during workflow sessions but never automatically committed. Untracked files are silently lost when switching branches — as experienced during the 009/010 branch setup where spec files had to be recreated multiple times. There is no structured commit trail that records who changed what, when, and why for each artifact, making it impossible to audit the evolution of a feature's documentation.

**Who**: Developers and AI agents using trasgospec for spec-driven development. Both human users who switch branches mid-session and autonomous agents that modify artifacts as part of workflow execution.

**Current Alternatives**: Manual `git commit` after each artifact change. This is easily forgotten during interactive sessions where multiple artifacts are created or updated in rapid succession. When forgotten, untracked files are lost on branch switches with no recovery path.

**Desired Outcome**: Every skill invocation that modifies spec artifacts triggers an automatic git commit with a structured, grep-filterable message. The commit history becomes the audit log — users can run `git log --grep='[speckit:audit]'` to reconstruct the full lifecycle of any artifact.

## Clarifications

### Session 2026-08-09

- Q: Should the audit hook commit all new/modified files in the spec directory, or only files changed during the current skill invocation? → A: Commit all new/modified files in the spec directory (no baseline tracking needed)
- Q: How should the audit hook generate the one-liner description for each changed file in the commit message? → A: The hook command (AI) inspects the diff or file content to generate a brief meaningful description
- Q: What priority should the audit hook have relative to existing after_* hooks? → A: Run last (priority 20) — commit after all other hooks finish modifying artifacts

## User Scenarios & Testing

### User Story 1 - Automatic Commit After Skill Execution (Priority: P1)

A developer runs a spec-driven skill (e.g., `/speckit-specify`, `/speckit-plan`, `/speckit-discovery`) that creates or modifies artifacts in the feature's spec directory. After the skill completes, an `after_*` hook automatically detects all new and modified files in the spec directory, stages them, and commits them with a structured message. The developer sees a brief confirmation showing which files were committed.

**Why this priority**: This is the core value proposition — preventing artifact loss and creating an audit trail. Without this, all other stories are moot.

**Independent Test**: Run `/speckit-specify` on a test feature, verify that a git commit is automatically created containing the spec artifacts, with the correct message format.

**Acceptance Scenarios**:

1. **Given** a skill has just finished and modified `spec.md` in the spec directory, **When** the `after_specify` hook fires, **Then** the hook stages `spec.md`, commits with a message listing `spec.md - <description>` followed by `[speckit:audit]`, and displays `Committed: spec.md - <description> [speckit:audit]`
2. **Given** a skill has just finished and created two new files (`research.md`, `data-model.md`), **When** the `after_plan` hook fires, **Then** both files are staged and committed in a single commit with each file listed on its own line, followed by `[speckit:audit]`
3. **Given** a skill has just finished but made no changes to any artifacts in the spec directory, **When** the `after_*` hook fires, **Then** no commit is created and the hook displays `No artifact changes to commit.`

---

### User Story 2 - Grep-Filterable Audit Trail (Priority: P2)

A developer needs to understand how a feature's spec evolved over time. They run `git log --grep='[speckit:audit]'` and see a chronological list of all automatic commits, each showing which files changed and which skill produced the change. They can further narrow by file path with `git log --grep='[speckit:audit]' -- specs/011-audit-and-logs/`.

**Why this priority**: The audit trail is the primary user-facing output of this feature. If commits exist but aren't filterable or readable, the feature fails its stated goal.

**Independent Test**: After several skill invocations, run `git log --grep='[speckit:audit]'` and verify all automatic commits appear with correct, parseable message format.

**Acceptance Scenarios**:

1. **Given** multiple skills have run and produced automatic commits, **When** the user runs `git log --grep='[speckit:audit]'`, **Then** all audit commits appear and no non-audit commits are included
2. **Given** a commit message with the format `spec.md - created feature specification\n[speckit:audit]`, **When** the user reads the log, **Then** each line before `[speckit:audit]` identifies a file and a human-readable description of the change

---

### User Story 3 - Hook Registration in extensions.yml (Priority: P3)

A developer installs the trasgospec bundle, which registers `after_*` hooks in `.specify/extensions.yml` for all artifact-producing skills. The hooks point to the audit commit command with priority 20 (runs after all other hooks). The developer does not need to manually configure anything — the hooks are part of the bundle's extension manifest.

**Why this priority**: Without hook registration, the automatic commit mechanism has no trigger. This is infrastructure that enables P1, but is lower priority because it's a one-time setup concern.

**Independent Test**: Install the bundle and verify that `extensions.yml` contains `after_*` entries for discovery, specify, clarify, plan, tasks, implement, and converge hooks pointing to the audit commit command.

**Acceptance Scenarios**:

1. **Given** the trasgospec bundle is installed, **When** the user inspects `.specify/extensions.yml`, **Then** `after_*` hook entries exist for each artifact-producing skill, each pointing to the audit commit command with `optional: false` and `priority: 20`
2. **Given** an `after_*` hook is registered for a skill that does not modify artifacts (e.g., `analyze`), **When** that skill runs, **Then** the hook fires but correctly reports `No artifact changes to commit.`

---

### Edge Cases

- What happens when the spec directory has uncommitted changes from outside a skill (e.g., manual edits)? The hook commits all new/modified files in the spec directory — it does not distinguish between skill-produced and pre-existing changes.
- What happens when `git commit` fails (e.g., due to a pre-commit hook failure or lock file)? The hook should display the git error and warn the user that artifacts were not committed, without blocking the skill's completion.
- What happens when the user is on a detached HEAD? The hook should warn that no commit was created because no branch is checked out.
- What happens when the spec directory does not exist (e.g., skill invoked without a feature context)? The hook should skip silently.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide an `after_*` hook command that detects new and modified files in the current feature's spec directory after a skill completes
- **FR-002**: System MUST stage all detected new and modified files within the spec directory and create a single git commit per skill invocation
- **FR-003**: Commit messages MUST follow the format: one line per changed file (`<filename> - <description>`), ending with `[speckit:audit]` on its own line. The description is generated by the hook command (AI) by inspecting the diff or file content.
- **FR-004**: System MUST display a brief confirmation after a successful commit listing the committed files
- **FR-005**: System MUST display `No artifact changes to commit.` when no files in the spec directory changed
- **FR-006**: System MUST register `after_*` hooks in `extensions.yml` for all artifact-producing skills: discovery, specify, clarify, checklist, plan, tasks, implement, and converge, with `priority: 20` (runs after all other hooks)
- **FR-007**: System MUST gracefully handle git errors (commit failures, detached HEAD, missing spec directory) without blocking the preceding skill's completion
- **FR-008**: System MUST use the commit author from the user's git configuration (no override)

### Key Entities

- **Audit Commit**: A git commit created by the hook, containing one or more artifact changes from a single skill invocation, with a structured `[speckit:audit]`-tagged message
- **Spec Directory**: The feature's directory under `specs/` containing all artifacts (prd.md, spec.md, plan.md, tasks.md, checklists/, etc.)
- **Hook Registration**: An entry in `.specify/extensions.yml` under `after_*` keys that triggers the audit commit command with `priority: 20`

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of artifact-producing skill invocations result in an automatic commit or a `No artifact changes to commit.` message — no silent failures
- **SC-002**: Users can retrieve the complete change history of any spec artifact using `git log --grep='[speckit:audit]' -- <artifact-path>`
- **SC-003**: Zero manual git commits are required to preserve spec artifacts during normal workflow usage
- **SC-004**: Each audit commit message is parseable — every line before `[speckit:audit]` matches the pattern `<filename> - <description>`

## Assumptions

- Git is always available and initialized in trasgospec projects (the bundle requires a git repository)
- The hook follows the two-part extension pattern: a command file with AI instructions and a script file with deterministic logic
- The script detects changes by listing all new and modified files in the spec directory at hook execution time (no baseline snapshot needed)
- The hook command (AI) generates meaningful one-liner descriptions by inspecting the diff or file content for each changed file
- Pre-existing uncommitted changes outside the spec directory are not touched by the hook
- The audit hook runs with priority 20, ensuring it executes after all other `after_*` hooks (status advancement, flow-nudge, etc.) have finished
