# Data Model: Conversational Discovery Command

## Entities

### PRD Document (`prd.md`)

The primary output artifact. A markdown file with structured sections.

| Section | Required | Content Source |
|---------|----------|---------------|
| Title (H1) | Yes | Derived from conversation — slug-friendly feature name |
| Created date | Yes | Script generates timestamp at directory creation |
| Discovery Session date | Yes | Same as created date |
| Problem Statement > Pain Point | Yes | Conversation extraction |
| Problem Statement > Who | Yes | Conversation extraction |
| Problem Statement > Current Alternatives | Yes | Conversation extraction |
| Problem Statement > Desired Outcome | Yes | Conversation extraction |
| User Stories Overview | Yes | Conversation extraction — bullet list of story sketches |
| Assumptions | Yes | Conversation extraction — reasonable defaults noted |
| Research Findings | Conditional | Only when web research mode was enabled; omitted otherwise |

### Spec Directory (`specs/<NNN-slug>/`)

| Attribute | Type | Source |
|-----------|------|--------|
| Number (NNN) | 3-digit zero-padded integer | Script computes: max existing + 1 |
| Slug | Kebab-case string | Script derives from user's initial input or conversation title |
| Directory path | Filesystem path | `specs/<NNN>-<slug>/` |

### Discovery Session (transient — not persisted)

The conversational state tracked by the command file during the session. Not saved as a raw transcript.

| Attribute | Type | Description |
|-----------|------|-------------|
| Topic coverage map | Map<Topic, Status> | Tracks which PRD sections have sufficient content (empty/partial/complete) |
| Current topic | Topic enum | Which discovery topic is being explored |
| Persistence state | Boolean | Whether the current PRD state has been saved to disk |
| Web research enabled | Boolean | Whether the user opted into web research |

**Topic enum**: `pain_point`, `who`, `current_alternatives`, `desired_outcome`, `user_stories`, `assumptions`

**Status enum**: `empty` (not discussed), `partial` (discussed but vague/incomplete), `complete` (sufficient content)

### Completion Criteria

The PRD is considered complete when all required sections reach `complete` status:

| Section | Completion Rule |
|---------|----------------|
| Pain Point | Contains a concrete, specific problem statement (not vague) |
| Who | Identifies a specific audience or persona (not "everyone") |
| Current Alternatives | Names at least one existing approach and why it falls short |
| Desired Outcome | States a measurable or observable goal |
| User Stories | Contains at least one story sketch with actor + action + value |
| Assumptions | Contains at least one documented assumption |

## Relationships

```
Spec Directory (1) ── contains ──> (1) PRD Document
Spec Directory (1) ── may later contain ──> (1) spec.md (created by /speckit-specify)
Discovery Session (1) ── produces ──> (1) PRD Document
Discovery Session (1) ── uses ──> (0..1) Web Research (via /research skill)
```

## State Transitions

```
Discovery Session States:
  STARTED → EXPLORING → COMPLETE → FINALIZED

  STARTED: Script created directory, command file begins conversation
  EXPLORING: One or more topics being discussed, topic coverage map updating
  COMPLETE: All required sections reach "complete" status; user is nudged
  FINALIZED: User confirms done; final PRD written to disk

  At any point: user says "abort" → no artifacts created (or partial artifacts deleted)
  At any point: user says "done" before COMPLETE → PRD saved as-is with warning about missing sections
```
