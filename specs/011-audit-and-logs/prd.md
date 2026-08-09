# PRD: Audit and Logs

**Created**: 2026-08-09
**Discovery Session**: 2026-08-09
**Status**: Discovery

## Problem Statement

**Pain Point**: Spec artifacts (prd.md, spec.md, plan.md, tasks.md) are created and modified during workflow sessions but not automatically committed. Untracked files are lost when switching branches, as experienced during the 009/010 branch setup where spec files had to be recreated multiple times. There is no structured commit trail that records who changed what, when, and why for each artifact — making it impossible to audit the evolution of a feature's documentation.

**Who**: Developers and agents using trasgospec for spec-driven development. Both human users who switch branches mid-session and autonomous agents that modify artifacts as part of workflow execution.

**Current Alternatives**: Manual git commits after each artifact change. This is easily forgotten, especially during interactive sessions where multiple artifacts are created or updated in rapid succession. When forgotten, untracked files are lost on branch switches.

**Desired Outcome**: Every artifact change triggers an automatic git commit with a structured, grep-filterable message. The commit history becomes the audit log — showing the complete document lifecycle: who changed what file, when, and why (which skill or manual action produced the change). Users can run `git log --grep` to reconstruct the full history of any artifact.

## Jobs to Be Done

- When a skill creates or updates a spec artifact, I want an automatic commit so that my work is never lost to branch switches or session interruptions
- When I need to understand how a spec evolved, I want to filter git history by artifact path and structured commit tags so I can trace every change back to the skill or action that produced it
- When an agent modifies artifacts during autonomous workflow execution, I want each change committed with context so I can audit what the agent did and why

## Assumptions

- Git is always available in trasgospec projects (the bundle requires a git repository)
- Automatic commits use a structured message format with a filterable prefix (e.g., `[speckit:audit]`) so they can be distinguished from manual commits and filtered with `git log --grep`
- Commit messages include: the artifact path, the skill/action that triggered the change, and a brief description of what changed
- Automatic commits are granular (one per artifact change) rather than batched, to preserve precise audit trails
- The commit author reflects who or what made the change (human user's git config or agent identity)
