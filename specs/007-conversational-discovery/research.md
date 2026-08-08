# Research: Conversational Discovery Command

## R1: Script Responsibilities — What deterministic work does discovery.sh need to do?

**Decision**: The script handles three operations: (1) determine the next sequential spec number by scanning existing `specs/` directories, (2) create the output directory `specs/<NNN-slug>/`, and (3) scaffold an empty `prd.md` with section headers. It also updates `.specify/feature.json`.

**Rationale**: This mirrors how `scan-specs.sh` already scans `specs/` directories and how `flow-context.sh` reads `feature.json`. The script does the filesystem setup; the command file does the conversational AI work and fills in the PRD content.

**Alternatives considered**:
- Having the command file do directory creation directly — rejected, violates constitution Principle I (deterministic work in scripts)
- Having the script also scaffold `spec.md` — rejected, the discovery command only produces `prd.md`; `spec.md` is created later by `/speckit-specify`

## R2: PRD Template Structure

**Decision**: The `prd.md` uses this structure:

```markdown
# PRD: [Feature Title]

**Created**: [DATE]
**Discovery Session**: [DATE]

## Problem Statement

**Pain Point**: [extracted from conversation]

**Who**: [extracted from conversation]

**Current Alternatives**: [extracted from conversation]

**Desired Outcome**: [extracted from conversation]

## User Stories Overview

- [Story sketch 1]
- [Story sketch 2]
- ...

## Assumptions

- [Assumption 1]
- ...

## Research Findings

- [Finding 1 — only when web research was used]
- ...
```

**Rationale**: Mirrors the spec template's Problem Statement section for direct 1:1 mapping. Adds Assumptions and Research Findings sections per clarification decisions. Keeps it lightweight — this is a pre-spec artifact, not a full specification.

**Alternatives considered**:
- Free-form narrative — rejected, loses the structured handoff benefit
- Full spec template copy — rejected, too heavy for a problem exploration artifact

## R3: Criteria-Based Completion Logic

**Decision**: The command file maintains an internal checklist of required PRD sections. After each user response, it evaluates which sections have sufficient content. When all required sections are populated, it nudges the user: "The PRD covers all required topics. You can continue refining or say 'done' to finalize." The user can always continue adding detail.

**Rationale**: This is purely AI agent logic (evaluating conversation completeness) — it belongs in the command file, not the script. The criteria are: (1) Pain Point has a concrete statement, (2) Who identifies a specific audience, (3) Current Alternatives names at least one, (4) Desired Outcome has a measurable goal, (5) User Stories has at least one sketch.

**Alternatives considered**:
- Fixed question count (5 or 10) — rejected per clarification; criteria-based is more adaptive
- Script-side completeness check — rejected; requires AI judgment to assess quality

## R4: Adaptive Topic Exploration

**Decision**: The command file starts by analyzing the user's initial input to identify which PRD sections already have partial coverage. It then asks about the least-covered topic first, following the natural conversation flow. It does not follow a fixed question sequence.

**Rationale**: Per clarification, users have product sense and can navigate the exploration naturally. The command acts as a gap-filler, not a rigid interviewer. This requires AI judgment (command file responsibility).

**Alternatives considered**:
- Fixed sequence (problem → users → alternatives → outcome → stories) — rejected per clarification
- Fully user-driven with no guidance — rejected; the command still needs to ensure all topics are covered

## R5: Incremental Persistence

**Decision**: After each significant exchange (when a topic reaches sufficient coverage), the command asks: "Want me to save this progress to prd.md?" If yes, it writes the current state. If no, it continues but warns that unpersisted content may be lost. The script creates the initial empty scaffold; the command file handles all subsequent writes.

**Rationale**: Per clarification, incremental saves reduce risk of losing work in long sessions. The ask-before-save pattern respects user control.

**Alternatives considered**:
- Auto-save after every response — rejected; too noisy, user wants control
- Save only at end — rejected per clarification; risks losing work

## R6: Web Research Integration

**Decision**: The command file uses the existing `/research` skill (Perplexity-based) when web research is enabled. It invokes research at natural conversation points — primarily when discussing current alternatives and desired outcomes. Research findings are woven into the conversation and persisted in the Research Findings section.

**Rationale**: Reuses existing infrastructure (Principle II — Spec Kit Native). No new research mechanism needed.

**Alternatives considered**:
- Custom web search integration — rejected; duplicates existing `/research` capability
- Always-on research — rejected per FR-008; must be opt-in

## R7: Vagueness Detection

**Decision**: The command file uses AI judgment to detect vague statements. Indicators include: non-specific audiences ("everyone", "all users"), unmeasurable outcomes ("better", "faster", "more intuitive"), undefined scope ("and more", "etc."), and missing specifics ("some kind of"). When detected, the command asks a targeted follow-up before accepting the answer.

**Rationale**: This is the core differentiator (User Story 2). It's purely AI judgment — command file responsibility. The vagueness patterns are guidelines, not rigid rules.

**Alternatives considered**:
- Keyword-based detection in script — rejected; requires AI judgment for context
- Always challenge every answer — rejected; would be annoying for already-specific answers
