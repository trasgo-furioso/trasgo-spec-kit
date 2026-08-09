# PRD: Audit and Logs

**Created**: 2026-08-09
**Discovery Session**: 2026-08-09
**Status**: Planning

## Problem Statement

**Pain Point**: Spec artifacts (prd.md, spec.md, plan.md, tasks.md) are created and modified during workflow sessions but not automatically committed. Untracked files are lost when switching branches, as experienced during the 009/010 branch setup where spec files had to be recreated multiple times. There is no structured commit trail that records who changed what, when, and why for each artifact — making it impossible to audit the evolution of a feature's documentation.

**Who**: Developers and agents using trasgospec for spec-driven development. Both human users who switch branches mid-session and autonomous agents that modify artifacts as part of workflow execution.

**Current Alternatives**: Manual git commits after each artifact change. This is easily forgotten, especially during interactive sessions where multiple artifacts are created or updated in rapid succession. When forgotten, untracked files are lost on branch switches.

**Desired Outcome**: Every artifact change triggers an automatic git commit with a structured, grep-filterable message. The commit history becomes the audit log — showing the complete document lifecycle: who changed what file, when, and why (which skill or manual action produced the change). Users can run `git log --grep='[speckit:audit]'` to reconstruct the full history of any artifact.

## Jobs to Be Done

- When a skill creates or updates a spec artifact, I want an automatic commit so that my work is never lost to branch switches or session interruptions
- When I need to understand how a spec evolved, I want to filter git history by artifact path and structured commit tags so I can trace every change back to the skill or action that produced it
- When an agent modifies artifacts during autonomous workflow execution, I want each change committed with context so I can audit what the agent did and why

## Assumptions

- Git is always available in trasgospec projects (the bundle requires a git repository)
- Commits are batched per skill invocation (one commit per skill run), not per individual artifact change — balances auditability with commit noise
- Commit message format is a flat list of changed files with one-liner descriptions, ending with `[speckit:audit]` tag on its own line:
  ```
  prd.md - populated problem statement and JTBD from discovery session
  spec.md - created feature specification from PRD
  [speckit:audit]
  ```
- The mechanism is hook-based: an `after_*` hook registered for each skill detects changed/new artifacts in the spec directory and commits them
- The hook stages both new (untracked) and modified files within the spec directory
- On successful commit, the hook displays a brief confirmation: `Committed: <file> - <description> [speckit:audit]`
- When no artifacts changed, the hook displays: `No artifact changes to commit.`
- The commit author reflects who or what made the change (human user's git config or agent identity)
