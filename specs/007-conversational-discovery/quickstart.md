# Quickstart: Conversational Discovery Command

## Prerequisites

- Trasgo Spec Kit bundle installed (`trasgospec`)
- Project initialized with `.specify/` directory
- At least one existing spec in `specs/` (to verify sequential numbering)

## Validation Scenarios

### Scenario 1: Script creates directory and scaffold

```bash
# Run the discovery script directly to verify deterministic operations
cd /path/to/project
bundle/extensions/trasgospec/scripts/bash/discovery.sh --json "test-feature"
```

**Expected output** (stdout):
```json
{"spec_dir":"specs/008-test-feature","spec_number":"008","slug":"test-feature","prd_path":"specs/008-test-feature/prd.md","feature_json_updated":true}
```

**Verify**:
- Directory `specs/008-test-feature/` exists
- `specs/008-test-feature/prd.md` exists with section headers
- `.specify/feature.json` points to `specs/008-test-feature`

### Scenario 2: Discovery command — basic conversational loop

```
/speckit-trasgospec-discovery I want to add caching to my API
```

**Expected behavior**:
1. Script runs, creates directory and scaffold
2. Command analyzes the input "I want to add caching to my API"
3. Command identifies gaps (e.g., "Who experiences the caching problem?")
4. Command asks the first question about the least-covered topic
5. User answers; command evaluates coverage and asks next question
6. When all criteria met, command nudges: "The PRD covers all required topics..."
7. User says "done"; final `prd.md` is written

**Verify**:
- `prd.md` has all sections populated (Pain Point, Who, Current Alternatives, Desired Outcome, User Stories, Assumptions)
- No section contains placeholder text

### Scenario 3: Vagueness challenge

During Scenario 2, provide a vague answer:
- User: "Everyone needs caching"
- **Expected**: Command pushes back — "Who specifically experiences slow responses? Backend developers, end users, or API consumers?"

### Scenario 4: Incremental persistence

During the conversation:
- After discussing the Pain Point topic sufficiently
- **Expected**: Command asks "Want me to save this progress to prd.md?"
- User: "yes"
- **Verify**: `prd.md` now has Pain Point section populated; other sections still have headers only

### Scenario 5: Web research enrichment

```
/speckit-trasgospec-discovery --research I want to add real-time collaboration to my document editor
```

**Expected behavior**:
- Command uses `/research` skill to find existing solutions (Google Docs, Notion, etc.)
- Research findings woven into conversation and persisted in Research Findings section

### Scenario 6: PRD as specify input

```
/speckit-specify specs/008-test-feature/prd.md
```

**Expected behavior**:
- Specify skill reads the PRD content
- Generated `spec.md` reflects PRD content in Problem Statement section
- Fewer NEEDS CLARIFICATION markers than a spec from a one-liner

### Scenario 7: Sequential numbering with gaps

Given existing specs: `001-*`, `004-*`, `005-*`, `007-*`

```bash
bundle/extensions/trasgospec/scripts/bash/discovery.sh --json "new-feature"
```

**Expected**: `spec_number` is `008` (max + 1), not `002` (gap fill)

## Test Commands

```bash
# Unit tests for the discovery script
.venv/bin/pytest tests/unit/test_discovery.py -v

# Integration tests for end-to-end flow
.venv/bin/pytest tests/integration/test_discovery_integration.py -v
```
