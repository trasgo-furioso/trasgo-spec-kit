# PRD: Audit and Logs

**Created**: 2026-08-09
**Discovery Session**: 2026-08-09 (revised)
**Status**: Discovery

## Problem Statement

**Pain Point**: Files created or modified during workflow sessions — spec artifacts, implementation code, tests, documentation — are not automatically committed. Untracked files are lost when switching branches, as experienced during the 009/010 branch setup where spec files had to be recreated multiple times. There is no structured commit trail that records who changed what, when, and why — making it impossible to audit the evolution of a project's artifacts.

**Who**: Developers and AI agents using trasgospec for spec-driven development. Both human users who switch branches mid-session and autonomous agents that modify files as part of workflow execution.

**Current Alternatives**: Manual `git commit` after each change. This is easily forgotten during interactive sessions where multiple files are created or updated in rapid succession. When forgotten, untracked files are lost on branch switches with no recovery path.

**Desired Outcome**: A reusable commit command (`speckit.trasgospec.commit`) that follows the two-part extension pattern. It performs the full git cycle — detect changes, decide what to include (AI judgment), stage, commit with a structured message, and push. Hooked on `after_*` for every artifact-producing skill, the commit history becomes the audit log. Users can audit who did what and why by running `git log`.

## Jobs to Be Done

- When a skill creates or updates files, I want an automatic commit and push so that my work is never lost to branch switches or session interruptions
- When I need to understand how a project evolved, I want to read `git log` and see structured `file - description` entries so I can trace every change back to the action that produced it
- When an agent modifies files during autonomous workflow execution, I want each change committed with context so I can audit what the agent did and why

## Assumptions

- Git is always available in trasgospec projects (the bundle requires a git repository)
- `.specify/` directory is gitignored — it is user-environment state managed by Spec Kit, not project source
- The command follows the two-part extension pattern: a command file (AI instructions) and a script file (deterministic git status/diff gathering)
- Commits are batched per skill invocation (one commit per skill run)
- Commit message format is a flat list of changed files with one-liner descriptions, no tags or headers. File paths are relative to the repo root:
  ```
  specs/011-audit-and-logs/prd.md - populated problem statement and JTBD from discovery session
  specs/011-audit-and-logs/spec.md - created feature specification from PRD
  ```
- The command is repo-wide — it considers all changed/new files, not just the spec directory
- The AI decides what to include in the commit based on judgment; when unsure (unrelated changes, binaries, secrets), it asks the user
- The command performs the full git cycle: detect → decide → stage → commit → push
- If push fails (remote rejection, conflicts), the command warns and leaves the commit in place for the user to resolve manually
- The commit author reflects who or what made the change (human user's git config or agent identity)
- The mechanism is hook-based: an `after_*` hook registered for each artifact-producing skill triggers the commit command
