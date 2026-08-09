# PRD: Spec Lifecycle Management

**Created**: 2026-08-09
**Discovery Session**: 2026-08-09
**Status**: Discovery

## Problem Statement

**Pain Point**: Trasgospec provides roadmap visualization and a full specify → plan → tasks → implement workflow, but there is no structured lifecycle tracking for specs. The status field exists in spec.md but has no defined values, no transitions, and never changes as work progresses through phases. This makes it impossible to see at a glance where each feature stands or identify bottlenecks across the portfolio.

**Who**: Teams and solo practitioners using trasgospec for spec-driven development. Two personas — product (creates ideas and PRDs) and engineering (drives specs through implementation) — may be the same person, but the lifecycle enforces a collaboration contract between product thinking and engineering execution regardless of team size.

**Current Alternatives**: No status tracking exists today. The `**Status**` field in spec.md is freeform and never updated during the project. Spec Kit leaves it open to users. Users track phase informally by knowing which artifacts exist.

**Desired Outcome**: A structured lifecycle with defined phases, automated transitions via pre/post hooks on skills, and a dedicated tool for manual status management. PRDs appear on the roadmap alongside specs, giving full portfolio visibility. The roadmap becomes the single view where teams orchestrate their work, spot bottlenecks (blocked items), and decide what to do next.

## Lifecycle Phases

| Phase | Meaning | Entered When |
|-------|---------|--------------|
| `discovery` | PRD in progress, problem being explored | PRD created via discovery skill |
| `opportunity` | PRD complete, validated, ready for engineering | PRD passes quality gate (requirements list, assumptions validated) |
| `planning` | Spec and plan being written | Spec or plan work begins |
| `ready-to-dev` | Spec and plan complete | Spec + plan finalized |
| `in-progress` | Tasks and implementation underway | Tasks generated, implementation started |
| `in-review` | PR open, team reviewing | PR opened for the feature branch |
| `delivered` | Branch merged to main | Feature branch merged |

**Lateral state**: `blocked` — human decision needed. Can apply at any phase. Agents set this when they encounter a decision point requiring user input. Surfaces as a bottleneck on the roadmap.

**Abandoned**: deleted, not tracked. No zombie specs.

## Status Field Design

- Both `prd.md` and `spec.md` carry an identical `**Status**` field
- `scan-specs.sh` reads `**Status**` from whichever artifact it finds (prd.md when no spec.md exists; spec.md takes precedence when both exist)
- No artifact-inference logic — status is always explicit
- This means the roadmap command works identically for PRD-only features and fully-specced features

## Automation Model

- Pre/post hooks on skills trigger automatic status transitions (e.g., running `/speckit-plan` advances status from `opportunity` to `planning`)
- A dedicated tool (command) allows humans and agents to manage statuses manually — advance, set blocked, revert
- Agents set `blocked` mid-workflow when they need a human decision, making bottlenecks visible on the roadmap

## Jobs to Be Done

- When I look at the roadmap, I want to see every feature's lifecycle stage so I can orchestrate what to work on next — even as a solo team
- When an agent hits a decision point during a workflow, I want it to flag the feature as blocked so I can easily find and resolve bottlenecks from the roadmap
- When I create a PRD during discovery, I want it to appear on the roadmap immediately so all planned work is visible from ideation onward

## Assumptions

- PRDs can exist on the roadmap independently of specs (discovery/opportunity phases)
- A quality gate (requirements checklist) distinguishes discovery from opportunity
- The roadmap script needs to scan both prd.md and spec.md to build the full picture
- Hooks infrastructure (pre/post on skills) exists or will be built to automate transitions
- The same `**Status**` field pattern in prd.md and spec.md allows uniform parsing with no special-case logic
