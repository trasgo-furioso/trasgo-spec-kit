# Feature Specification: Audit and Logs

**Feature Branch**: `011-audit-and-logs`

**Created**: 2026-08-09

**Status**: Planning

**Input**: User description: "specs/011-audit-and-logs/prd.md" (revised)

## Problem Statement

**Pain Point**: Files created or modified during workflow sessions — spec artifacts, implementation code, tests, documentation — are not automatically committed. Untracked files are lost when switching branches, as experienced during the 009/010 branch setup where spec files had to be recreated multiple times. There is no structured commit trail that records who changed what, when, and why — making it impossible to audit the evolution of a project's artifacts.

**Who**: Developers and AI agents using trasgospec for spec-driven development. Both human users who switch branches mid-session and autonomous agents that modify files as part of workflow execution.

**Current Alternatives**: Manual `git commit` after each change. This is easily forgotten during interactive sessions where multiple files are created or updated in rapid succession. When forgotten, untracked files are lost on branch switches with no recovery path.

**Desired Outcome**: A reusable commit command (`speckit.trasgospec.commit`) that performs the full git cycle — detect changes, decide what to include, stage, commit with a structured message, and push. Hooked on `after_*` for every artifact-producing skill, the commit history becomes the audit log. Users can audit who did what and why by reading `git log`.

## User Scenarios & Testing

### User Story 1 - Automatic Commit and Push After Skill Execution (Priority: P1)

A developer runs a spec-driven skill (e.g., `/speckit-specify`, `/speckit-plan`) that creates or modifies files anywhere in the repository. After the skill completes, an `after_*` hook triggers the commit command. The command gathers all changed and new files repo-wide, uses AI judgment to decide what to include, stages appropriate files, commits with a structured message, and pushes to the remote. The developer sees a brief confirmation showing which files were committed.

**Why this priority**: This is the core value proposition — preventing file loss, creating an audit trail, and keeping the remote in sync. Without this, all other stories are moot.

**Independent Test**: Run `/speckit-specify` on a test feature, verify that a git commit is automatically created containing the changed files with the correct message format, and that the commit is pushed.

**Acceptance Scenarios**:

1. **Given** a skill has just finished and modified files in the repository, **When** the commit command fires, **Then** the command detects all changed/new files, stages them, commits with a message listing each file with its repo-relative path and a one-liner description, and pushes to the remote
2. **Given** a skill has just finished and created multiple new files across different directories, **When** the commit command fires, **Then** all new files are included in a single commit with each listed on its own line
3. **Given** a skill has just finished but made no changes to any files, **When** the commit command fires, **Then** no commit is created and the command displays `No changes to commit.`
4. **Given** the command detects files it is unsure about (unrelated changes, binaries, potential secrets), **When** deciding what to include, **Then** the command asks the user before including those files

---

### User Story 2 - Readable Audit Trail via git log (Priority: P2)

A developer needs to understand how a project evolved. They run `git log` and see structured commit messages where each line identifies a file (by full repo-relative path) and a brief description of the change. The format is distinctive enough to identify automated commits without needing a special tag.

**Why this priority**: The audit trail is the primary user-facing output. If commits exist but aren't readable or parseable, the feature fails its stated goal.

**Independent Test**: After several skill invocations, run `git log` and verify all automated commits follow the `<path> - <description>` format.

**Acceptance Scenarios**:

1. **Given** multiple skills have run and produced automated commits, **When** the user reads `git log`, **Then** each automated commit message contains one or more lines matching `<repo-relative-path> - <description>`
2. **Given** a commit message with multiple file entries, **When** the user reads the log, **Then** each line identifies the file's full path from the repo root and a human-readable description of what changed

---

### User Story 3 - Hook Registration (Priority: P3)

The trasgospec bundle registers `after_*` hooks for all artifact-producing skills, each pointing to the commit command. The developer does not need to manually configure anything — the hooks are part of the bundle's extension manifest.

**Why this priority**: Without hook registration, the commit command has no automatic trigger. This is infrastructure that enables P1, but is lower priority because it's a one-time setup concern.

**Independent Test**: Install the bundle and verify that the extension manifest contains `after_*` entries for discovery, specify, clarify, plan, tasks, implement, and converge hooks.

**Acceptance Scenarios**:

1. **Given** the trasgospec bundle is installed, **When** the user inspects the extension manifest, **Then** `after_*` hook entries exist for each artifact-producing skill, each pointing to the commit command with `optional: false` and `priority: 20`
2. **Given** an `after_*` hook fires for a skill that did not modify any files, **When** the commit command runs, **Then** it reports `No changes to commit.` without error

---

### User Story 4 - Gitignore .specify Directory (Priority: P1)

The `.specify/` directory is user-environment state managed by Spec Kit. It should be gitignored so that per-user configuration (feature.json, extensions.yml, installed extensions) does not pollute the repository or cause merge conflicts.

**Why this priority**: This is a prerequisite for the commit command to work correctly — without it, every commit would include `.specify/` changes, creating noise and merge conflicts.

**Independent Test**: Create a project with `.specify/` directory and verify it is excluded from `git status` output.

**Acceptance Scenarios**:

1. **Given** a project with a `.gitignore` that includes `.specify/`, **When** files inside `.specify/` are modified, **Then** `git status` does not list them as changed or untracked
2. **Given** an existing project without `.specify/` in `.gitignore`, **When** the bundle is installed or updated, **Then** the documentation instructs the user to add `.specify/` to `.gitignore`

---

### Edge Cases

- What happens when the repository has uncommitted changes from outside a skill (e.g., manual edits)? The command includes all repo-wide changes — it does not distinguish between skill-produced and pre-existing changes. The AI uses judgment and asks the user when unsure.
- What happens when `git commit` fails (e.g., due to a pre-commit hook failure or lock file)? The command displays the git error and warns the user, without blocking the preceding skill's completion.
- What happens when the user is on a detached HEAD? The command warns that no commit was created because no branch is checked out.
- What happens when `git push` fails (e.g., remote rejection, branch protection, conflicts)? The command warns and leaves the commit in place for the user to resolve manually.
- What happens when changed files include potential secrets (.env, credentials)? The command flags them and asks the user before including.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a commit command (`speckit.trasgospec.commit`) that detects all new and modified files in the repository
- **FR-002**: System MUST use AI judgment to decide which files to include in the commit, asking the user when unsure about unrelated changes, binaries, or potential secrets
- **FR-003**: System MUST stage selected files, commit with a structured message, and push to the remote in a single invocation
- **FR-004**: Commit messages MUST follow the format: one line per file with `<repo-relative-path> - <description>`. No tags, headers, or footers.
- **FR-005**: System MUST display a brief confirmation after a successful commit and push
- **FR-006**: System MUST display `No changes to commit.` when no files have changed
- **FR-007**: System MUST register `after_*` hooks for all artifact-producing skills: discovery, specify, clarify, checklist, plan, tasks, implement, and converge, with `priority: 20`
- **FR-008**: System MUST gracefully handle git errors (commit failures, detached HEAD, push failures) without blocking the preceding skill's completion
- **FR-009**: System MUST use the commit author from the user's git configuration
- **FR-010**: The `.specify/` directory MUST be documented as gitignored — it is user-environment state, not project source

### Key Entities

- **Commit Command**: The `speckit.trasgospec.commit` extension command following the two-part pattern (command file + script file)
- **Commit Message**: A structured multi-line message where each line is `<repo-relative-path> - <description>`
- **Hook Registration**: An entry in the extension manifest under `after_*` keys that triggers the commit command with `priority: 20`

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of artifact-producing skill invocations result in an automatic commit or a `No changes to commit.` message — no silent failures
- **SC-002**: Users can reconstruct the full change history of any file by reading `git log -- <file-path>`
- **SC-003**: Zero manual git commits are required to preserve work during normal workflow usage
- **SC-004**: Each automated commit message is human-readable — every line matches `<path> - <description>`
- **SC-005**: All automated commits are pushed to the remote within the same command invocation (unless push fails, in which case a warning is shown)

## Assumptions

- Git is always available and initialized in trasgospec projects (the bundle requires a git repository)
- `.specify/` directory is gitignored — it is user-environment state managed by Spec Kit, not project source
- The command follows the two-part extension pattern: a command file (AI instructions) and a script file (deterministic git status/diff gathering)
- Commits are batched per skill invocation (one commit per skill run)
- The command is repo-wide — it considers all changed/new files, not scoped to the spec directory
- The AI decides what to include based on judgment; when unsure, it asks the user
- The full git cycle is: detect → decide → stage → commit → push
- If push fails, the command warns and leaves the commit in place
- The commit author reflects who or what made the change (human user's git config or agent identity)
- The hook runs with priority 20, ensuring it executes after all other `after_*` hooks
