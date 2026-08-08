# Feature Specification: Conversational Discovery Command

**Feature Branch**: `007-conversational-discovery`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "A conversational discovery command (speckit-trasgospec-discovery) that guides users through interactive problem exploration before they commit to a spec. It asks targeted questions one at a time, challenges vague statements, and optionally uses web research to ground the conversation. The output is a structured PRD (prd.md) persisted in the specs directory following the existing numbering pattern. The PRD captures the problem statement, affected users, current alternatives, desired outcome, and user stories overview."

## Problem Statement *(mandatory)*

**Pain Point**: Users invoke `/speckit-specify` with a one-line feature description that often lacks sufficient problem context, audience clarity, and competitive landscape awareness. The specify skill does its best to infer missing context, but it cannot interrogate the user — it must work with whatever input it received. This results in specs that contain educated guesses, assumptions sections full of caveats, and NEEDS CLARIFICATION markers that require rework. The root cause is that problem discovery and spec generation are collapsed into a single step with no interactive exploration phase.

**Who**: Bundle authors and product thinkers who have a rough idea for a feature but have not yet articulated the problem space clearly enough to produce a high-quality spec on the first pass. These users benefit from guided questioning that helps them externalize tacit knowledge before committing to a formal specification.

**Current Alternatives**: Users currently either (a) write a longer, more detailed feature description upfront — which requires them to self-structure their thinking without guidance, (b) run `/speckit-specify` with a vague description and then manually edit the generated spec to fill gaps, or (c) use `/speckit-clarify` after spec generation to retroactively identify underspecified areas. None of these approaches provide the interactive, pre-spec discovery conversation that surfaces assumptions, challenges vagueness, and builds shared understanding before any artifact is generated.

**Desired Outcome**: Users can run a discovery command that walks them through structured problem exploration via one-question-at-a-time dialogue, challenges vague or hand-wavy statements, optionally enriches the conversation with web research, and produces a well-grounded PRD artifact that can be fed directly into `/speckit-specify` as high-quality input — reducing assumptions, NEEDS CLARIFICATION markers, and post-generation rework in the resulting spec.

## Clarifications

### Session 2026-08-08

- Q: Should the discovery session have a fixed max number of questions or user-driven termination? → A: Criteria-based — session concludes when the PRD satisfies all required sections; user is nudged but can continue refining indefinitely.
- Q: What structure should the prd.md follow? → A: Pain Point + Who + Current Alternatives + Desired Outcome + User Stories Overview + Assumptions + Research Findings (when web research used).
- Q: In what order should the discovery conversation explore topics? → A: Adaptive — the command explores whatever information is missing based on the conversation so far, following the natural flow rather than a fixed sequence. Assumes users have product sense.
- Q: How should the command handle persistence of the PRD? → A: Incremental — saves after each iteration or decision, asking the user if they want to persist as ground is covered.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Problem Exploration (Priority: P1)

A user invokes the discovery command with a rough idea (e.g., "I want to add caching to my API"). The command asks targeted questions one at a time — probing the pain point, who is affected, what alternatives exist, and what success looks like. The user answers each question conversationally. When the exploration is complete, the command generates a structured `prd.md` file in a new specs directory following the existing numbering pattern.

**Why this priority**: This is the core value loop — without interactive questioning and PRD output, the command delivers nothing. Everything else builds on this foundation.

**Independent Test**: Can be fully tested by invoking the discovery command with a brief feature idea and verifying that (a) the command asks at least one question before producing output, (b) the resulting `prd.md` exists in the correct specs directory, and (c) the PRD contains all five required sections: problem statement, affected users, current alternatives, desired outcome, and user stories overview.

**Acceptance Scenarios**:

1. **Given** a user invokes the discovery command with a brief feature idea, **When** the command begins, **Then** it asks a targeted question about the problem rather than immediately generating output.
2. **Given** the user has provided enough information to cover a discovery topic, **When** the command recognizes the topic is sufficiently explored, **Then** it offers to persist the current progress to `prd.md` before continuing.
3. **Given** the PRD satisfies all required sections (problem statement, affected users, current alternatives, desired outcome, user stories overview), **When** the completion criteria are met, **Then** the command nudges the user that the PRD is complete but allows them to continue refining.
4. **Given** a completed discovery session, **When** the `prd.md` is examined, **Then** it contains structured sections for problem statement (pain point, who, current alternatives, desired outcome), user stories overview, assumptions, and research findings (if web research was used) — all populated with content from the conversation.

---

### User Story 2 - Challenging Vague Statements (Priority: P2)

During the conversation, if the user provides a vague or hand-wavy answer (e.g., "it should be fast" or "everyone needs this"), the command pushes back with a follow-up question that asks for specifics rather than accepting the vague statement at face value.

**Why this priority**: Challenging vagueness is what differentiates this command from a simple questionnaire. Without it, the PRD would contain the same shallow content the user would have written on their own. However, the basic question-answer-persist loop (P1) must work first.

**Independent Test**: Can be tested by providing deliberately vague answers during a discovery session and verifying that the command responds with a follow-up that requests specifics rather than moving to the next topic.

**Acceptance Scenarios**:

1. **Given** the user responds to a question with a vague statement like "all users need this", **When** the command processes the answer, **Then** it asks a follow-up question requesting a specific user segment or persona.
2. **Given** the user responds with a non-measurable success criterion like "it should be better", **When** the command processes the answer, **Then** it asks what "better" means in observable or measurable terms.

---

### User Story 3 - Web Research Enrichment (Priority: P3)

The user opts into web research during the discovery session. The command uses web search to find information about the problem domain — existing solutions, market landscape, relevant prior art — and weaves findings into the conversation and the final PRD.

**Why this priority**: Web research adds depth and grounding to the PRD, but the core discovery loop and vagueness challenging must work without it. This is an enrichment layer.

**Independent Test**: Can be tested by invoking the discovery command with web research enabled, providing a problem description in a well-known domain, and verifying that the final PRD references external findings or alternatives discovered through research.

**Acceptance Scenarios**:

1. **Given** a user invokes the discovery command with web research enabled, **When** the conversation reaches the "current alternatives" topic, **Then** the command performs web research and presents relevant findings to the user for confirmation or correction.
2. **Given** web research is not explicitly enabled, **When** the discovery session runs, **Then** the command completes the full discovery flow without attempting web research.

---

### User Story 4 - PRD as Specify Input (Priority: P2)

After the discovery session produces a `prd.md`, the user can pass the PRD path to `/speckit-specify` as enriched input. The specify skill uses the PRD content to generate a higher-quality spec with fewer assumptions and NEEDS CLARIFICATION markers than it would from a raw one-line description.

**Why this priority**: This story closes the loop between discovery and specification. Without it, the PRD is a standalone document with no integration into the existing workflow. Ranked equal to P2 because it validates the end-to-end value proposition.

**Independent Test**: Can be tested by generating a PRD via the discovery command, then passing its path to `/speckit-specify`, and verifying the resulting spec has fewer NEEDS CLARIFICATION markers and assumptions than a spec generated from the same idea expressed as a one-line description.

**Acceptance Scenarios**:

1. **Given** a `prd.md` produced by the discovery command, **When** the user passes its path to `/speckit-specify`, **Then** the specify skill reads the PRD and uses its structured content as input for spec generation.
2. **Given** a PRD with a well-defined problem statement, **When** the specify skill generates a spec from it, **Then** the spec's Problem Statement section reflects the PRD content rather than making new inferences.

### Edge Cases

- What happens when the user wants to abort the discovery session midway? If no content has been persisted yet, the command should exit gracefully without creating any artifacts. If incremental saves have already been made, the command should warn the user that a partial prd.md exists on disk and offer to delete it or keep it as-is.
- What happens when the specs directory already has gaps in numbering (e.g., 001, 004, 005)? The command should use the next number after the highest existing spec, not fill gaps.
- What happens when the user provides contradictory answers during the session? The command should surface the contradiction and ask the user to resolve it before proceeding.
- What happens when web research returns no useful results? The command should note that no relevant external information was found and continue with the user's own knowledge.
- What happens when a user declines to persist mid-session? The command should continue the conversation but note that unpersisted content may be lost if the session is interrupted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The command MUST follow the trasgospec two-part extension pattern: a command file (`speckit.trasgospec.discovery.md`) containing AI agent instructions and a script file (`discovery.sh`) handling deterministic operations.
- **FR-002**: The command MUST ask questions one at a time, waiting for the user's response before proceeding to the next question.
- **FR-003**: The command MUST cover at minimum these discovery topics: problem statement, affected users, current alternatives, desired outcome, user stories overview, assumptions, and research findings (when web research is enabled).
- **FR-004**: The command MUST challenge vague or non-specific answers with targeted follow-up questions rather than accepting them verbatim.
- **FR-005**: The command MUST persist the discovery output as `prd.md` in a new specs directory following the existing sequential numbering pattern (`specs/<NNN-slug>/`).
- **FR-012**: The command MUST use criteria-based session completion: when the PRD satisfies all required sections (problem statement, affected users, current alternatives, desired outcome, user stories overview, assumptions), the command MUST nudge the user that the PRD is complete but allow them to continue refining.
- **FR-013**: The command MUST explore topics adaptively based on what information is already present or missing from the conversation, rather than following a fixed question sequence. The command assumes users have product sense and can navigate the exploration naturally.
- **FR-014**: The `prd.md` MUST contain structured sections for: problem statement (pain point, who, current alternatives, desired outcome), user stories overview, assumptions, and research findings (when web research was used).
- **FR-015**: The command MUST offer to persist progress to `prd.md` incrementally as topics are covered, rather than only saving at session completion. The user may accept or decline persistence at each checkpoint.
- **FR-007**: The command MUST support an optional web research mode that enriches the conversation with external findings.
- **FR-008**: When web research is not enabled, the command MUST complete the full discovery flow without attempting any web calls.
- **FR-009**: The script file MUST determine the next sequential spec number and create the output directory. The command file MUST NOT perform this deterministic work itself.
- **FR-010**: The `prd.md` path MUST be usable as input to `/speckit-specify` for enriched spec generation.
- **FR-011**: The command MUST register with the alias `trasgospec.discovery` in addition to the full `speckit.trasgospec.discovery` ID, following existing naming conventions.

### Key Entities

- **Discovery Session**: The interactive conversation between the command and the user, covering structured discovery topics. Not persisted as a raw transcript; its content is distilled into the PRD.
- **PRD (Product Requirements Document)**: The structured output artifact (`prd.md`) capturing the problem space exploration results. Serves as enriched input for downstream spec generation.
- **Spec Directory**: The numbered directory under `specs/` where the PRD is persisted, following the same sequential pattern used by specs themselves.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: PRDs generated through the discovery command produce specs (via `/speckit-specify`) with at least 50% fewer NEEDS CLARIFICATION markers compared to specs generated from equivalent one-line descriptions.
- **SC-002**: The discovery session covers all required topics (problem statement, affected users, current alternatives, desired outcome, user stories overview, assumptions) before generating the PRD.
- **SC-003**: At least one vague statement per session is challenged with a follow-up question requesting specifics (when the user provides vague input).
- **SC-004**: The `prd.md` is valid markdown that can be parsed by downstream tools without errors.
- **SC-005**: The spec directory numbering is correct and consistent with existing specs in the project.

## Assumptions

- The discovery command is a trasgospec bundle extension command, not a core Spec Kit skill — it follows the same two-part pattern (command file + script file) as `hello` and `roadmap`.
- The command file handles all conversational AI logic (questioning, challenging, research) while the script handles deterministic operations (directory creation, numbering, file structure scaffolding).
- How the PRD path is passed to `/speckit-specify` is not a risk — the handoff mechanism (file path argument, paste, or other) is a planning-phase detail that does not affect the discovery command's design.
- Web research uses the existing Perplexity-based `/research` skill infrastructure rather than introducing a new research mechanism.
- The PRD format is distinct from `spec.md` — a PRD is a pre-specification artifact focused on problem exploration, not a full feature specification. Both can coexist in the same specs directory.
