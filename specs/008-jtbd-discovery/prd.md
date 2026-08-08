# PRD: JTBD in Discovery

**Created**: 2026-08-08
**Discovery Session**: 2026-08-08

## Problem Statement

**Pain Point**: The discovery command currently asks users to sketch user stories during problem exploration. User stories are solution-flavored artifacts — "As a [role], I want [capability]..." — that pull the conversation into solution space during what should be a pure problem-space activity. This breaks domain separation between discovery and specification. AI-assisted coding has brought many engineers and non-product people into product work; trasgospec-discovery is a teaching tool that should model good discovery practice, and modeling solution-space thinking at the discovery stage teaches the wrong habit.

**Who**: Two segments, one tool. (1) Experienced PMs who gain a structured approach to what they already do intuitively. (2) Engineers and non-product people who get a runbook for product discovery. Both may be working from their own ideas or synthesizing stakeholder conversations and transcripts — that's an input mode, not a separate persona.

**Current Alternatives**: The current discovery command covers six required sections: Pain Point, Who, Current Alternatives, Desired Outcome, User Stories Overview, and Assumptions. The "User Stories Overview" section asks users to sketch story-shaped statements during the discovery conversation. These sketches anchor on a solution shape before the problem space is fully explored.

**Desired Outcome**: Replace "User Stories Overview" with "Jobs to Be Done" in the discovery coverage map and PRD structure. Use the job story format — "When [situation], I want to [motivation], so I can [outcome]" — with the situation trigger as the anchor. This keeps the conversation in problem space. The translation from JTBD to user stories is delegated to `/speckit-specify` when the PRD is passed as feature context.

## Jobs to Be Done

- When I'm running a discovery session, I want the conversation to stay in problem space without drifting into solution sketches, so I can produce a PRD that captures the real need before any spec work begins.
- When I pass a PRD to `/speckit-specify`, I want the problem framing to be solution-agnostic, so specify can derive user stories that fit its own spec structure without inheriting premature design decisions from discovery.

## Assumptions

- `/speckit-specify` can consume JTBD job stories from a PRD and translate them into user stories for the spec without changes to the specify skill. To be validated by feeding this PRD to specify and reviewing the output.
