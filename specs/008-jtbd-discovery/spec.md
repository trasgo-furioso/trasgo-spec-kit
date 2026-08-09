# Feature Specification: JTBD in Discovery

**Feature Branch**: `008-jtbd-discovery`

**Created**: 2026-08-08

**Status**: Delivered

**Input**: PRD from `specs/008-jtbd-discovery/prd.md` — Replace "User Stories Overview" with "Jobs to Be Done" in the trasgospec-discovery command. The discovery conversation should stay in problem space using the job story format ("When [situation], I want to [motivation], so I can [outcome]"). Translation from JTBD to user stories is delegated to `/speckit-specify` when the PRD is passed as feature context.

## Problem Statement *(mandatory)*

**Pain Point**: The discovery command currently includes "User Stories Overview" as a required section in both its coverage map and PRD output structure. User stories follow the "As a [role], I want [capability]..." format, which is inherently solution-flavored — it asks the user to describe a product capability during what should be a pure problem-space exploration. This breaks domain separation between discovery and specification. For engineers and non-product people who rely on trasgospec-discovery as a runbook for product discovery, modeling solution-space thinking at the discovery stage teaches the wrong habit.

**Who**: Two user segments served by one tool. (1) Experienced PMs who gain a structured approach to problem discovery they already practice intuitively. (2) Engineers and non-product people entering product work through AI-assisted coding, who use trasgospec-discovery as a runbook. Both may work from their own ideas or synthesize stakeholder conversations and transcripts — an input mode difference, not a persona difference.

**Current Alternatives**: The current discovery command covers six required sections: Pain Point, Who, Current Alternatives, Desired Outcome, User Stories Overview, and Assumptions. The "User Stories Overview" section asks users to sketch story-shaped statements during the discovery conversation. These sketches anchor on a solution shape before the problem space is fully explored. There is no way to stay in problem space throughout the entire discovery session.

**Desired Outcome**: The discovery command stays entirely in problem space by replacing the "User Stories Overview" section with "Jobs to Be Done" using the job story format. The situation trigger ("When [situation]...") anchors the conversation on when problems occur rather than what capabilities to build. The downstream `/speckit-specify` skill handles the translation from JTBD to user stories when consuming the PRD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discovery Conversation Uses Job Stories (Priority: P1)

A user runs `/speckit-trasgospec-discovery` with a feature idea. During the conversation, when the coverage map reaches the "Jobs to Be Done" section, the command guides the user to articulate job stories using the "When [situation], I want to [motivation], so I can [outcome]" format. The situation trigger is emphasized as the anchor — the command asks about when the problem occurs before asking about motivation or outcome.

**Why this priority**: This is the core behavioral change. Without it, the discovery command still asks for user stories and the domain contamination persists.

**Independent Test**: Run a discovery session and verify that (a) the coverage map tracks "Jobs to Be Done" instead of "User Stories Overview", (b) the command prompts for situation triggers, and (c) the resulting PRD contains a "Jobs to Be Done" section with properly formatted job stories.

**Acceptance Scenarios**:

1. **Given** a user starts a discovery session, **When** the coverage map is displayed or tracked internally, **Then** it lists "Jobs to Be Done" instead of "User Stories Overview".
2. **Given** the conversation reaches the JTBD topic, **When** the command prompts the user, **Then** it asks about the situation or trigger ("When does this problem occur?") before asking about motivation or desired outcome.
3. **Given** the user provides a job story, **When** the command evaluates coverage, **Then** it accepts the "When [situation], I want to [motivation], so I can [outcome]" format as complete coverage for the JTBD section.

---

### User Story 2 - PRD Output Structure Uses JTBD (Priority: P1)

When the discovery session completes, the generated `prd.md` contains a "Jobs to Be Done" section with the job stories collected during the conversation, replacing the former "User Stories Overview" section.

**Why this priority**: Equal to P1 because the PRD is the output artifact — if the output still says "User Stories Overview", the behavioral change in the conversation is not reflected in the deliverable.

**Independent Test**: Complete a discovery session and examine the resulting `prd.md` to verify it contains a "## Jobs to Be Done" heading with job stories in the correct format, and does not contain a "## User Stories Overview" heading.

**Acceptance Scenarios**:

1. **Given** a completed discovery session, **When** the `prd.md` is generated, **Then** it contains a "## Jobs to Be Done" section with at least one job story.
2. **Given** a completed discovery session, **When** the `prd.md` is generated, **Then** it does not contain a "## User Stories Overview" section.
3. **Given** a job story was captured during the session, **When** it appears in the PRD, **Then** it follows the "When [situation], I want to [motivation], so I can [outcome]" format.

---

### User Story 3 - Specify Consumes JTBD from PRD (Priority: P2)

A user passes a PRD containing JTBD job stories to `/speckit-specify`. The specify skill reads the job stories, understands them as problem-space framing, and derives appropriate user stories for the spec's "User Scenarios & Testing" section without requiring changes to the specify skill itself.

**Why this priority**: This validates the end-to-end handoff and the assumption that specify can handle the new PRD format. Ranked P2 because it depends on P1 being complete and tests the integration rather than discovery itself.

**Independent Test**: Generate a PRD with JTBD job stories via discovery, pass it to `/speckit-specify`, and verify the resulting spec contains user stories derived from the job stories — not copied verbatim as job stories.

**Acceptance Scenarios**:

1. **Given** a PRD with a "Jobs to Be Done" section, **When** passed to `/speckit-specify`, **Then** the spec's "User Scenarios & Testing" section contains user stories (not raw job stories).
2. **Given** a PRD with situation-triggered job stories, **When** the specify skill generates acceptance scenarios, **Then** the scenarios reflect the situations described in the job stories.

---

### Edge Cases

- What happens when the user provides a statement in user story format during the JTBD section? The command should recognize the format mismatch and guide the user to reframe it as a job story, focusing on the situation trigger.
- What happens when the user can only articulate one job story? The command should accept one job story as sufficient for the JTBD section — there is no minimum count beyond one.
- What happens when existing PRDs (from before this change) with "User Stories Overview" are passed to specify? Specify should handle both formats gracefully — this is not a discovery concern, but a compatibility note.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The discovery command's coverage map MUST track "Jobs to Be Done" instead of "User Stories Overview".
- **FR-002**: The discovery command MUST prompt users for job stories using the "When [situation], I want to [motivation], so I can [outcome]" format.
- **FR-003**: The discovery command MUST emphasize the situation trigger as the primary anchor when exploring JTBD — asking "when does this happen?" before "what do you want?" or "why?".
- **FR-004**: The `prd.md` output MUST contain a "## Jobs to Be Done" section instead of "## User Stories Overview".
- **FR-005**: The `prd.md` MUST list each job story as a bullet point in the JTBD section.
- **FR-006**: The command file (`speckit.trasgospec.discovery.md`) MUST be updated to reflect the new coverage map and PRD structure.
- **FR-007**: The skill file (`.claude/skills/speckit-trasgospec-discovery/SKILL.md`) MUST be updated to match the command file changes.
- **FR-008**: The discovery script (`discovery.sh`) MUST scaffold `prd.md` with "## Jobs to Be Done" instead of "## User Stories Overview" in the initial template.
- **FR-009**: The command MUST guide users away from solution-flavored statements if they drift into "As a [role], I want [capability]..." format during the JTBD section.

### Key Entities

- **Job Story**: A problem-space statement in the format "When [situation], I want to [motivation], so I can [outcome]". The situation trigger describes when the need arises; the motivation describes what progress the user seeks; the outcome describes the desired result.
- **Coverage Map**: The internal tracker of required PRD sections. "Jobs to Be Done" replaces "User Stories Overview" in the six required sections.
- **PRD**: The discovery output artifact. Its structure changes from containing "User Stories Overview" to "Jobs to Be Done".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Discovery sessions produce PRDs with a "Jobs to Be Done" section containing at least one properly formatted job story in 100% of completed sessions.
- **SC-002**: No discovery session produces a PRD containing a "User Stories Overview" section.
- **SC-003**: When a PRD with JTBD is passed to `/speckit-specify`, the resulting spec contains user stories derived from the job stories — not verbatim copies of the job story format.
- **SC-004**: The discovery conversation does not prompt for or accept solution-flavored "As a [role], I want [capability]..." statements in the JTBD section.

## Assumptions

- `/speckit-specify` can consume JTBD job stories from a PRD and translate them into user stories for the spec without changes to the specify skill. This PRD-to-spec conversion is being validated by this very spec generation.
- Existing PRDs with "User Stories Overview" will continue to work with `/speckit-specify` — backward compatibility is not broken, it is simply not a concern of the discovery command.
- The discovery script's PRD scaffolding template is the only place in the script that references the section name — the change is a string replacement, not a structural change to the script's logic.
- The command file and skill file are mirrors of each other — changes to one must be reflected in the other.
