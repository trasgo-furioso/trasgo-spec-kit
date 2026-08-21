# Contract: Command File — speckit.trasgospec.acceptance-tests

## Overview

Defines the structure of the extension command file that implements the acceptance test generation agent.

## File Location

```
bundle/extensions/trasgospec/commands/speckit.trasgospec.acceptance-tests.md
```

## YAML Frontmatter

```yaml
---
description: Generate Playwright E2E tests from spec.md acceptance scenarios.
---
```

No `scripts` key — this is an AI-agent-only command (precedent: `speckit.trasgospec.hello`).

## Extension Manifest Entry

Added to `bundle/extensions/trasgospec/extension.yml` under `provides.commands`:

```yaml
- name: "speckit.trasgospec.acceptance-tests"
  file: "commands/speckit.trasgospec.acceptance-tests.md"
  description: "Generate Playwright E2E tests from spec.md acceptance scenarios."
  aliases: ["trasgospec.acceptance-tests"]
```

## Markdown Body Structure

The command file body contains AI agent instructions organized as:

1. **User Input** — `$ARGUMENTS` block for optional arguments
2. **Goal** — one-paragraph summary of what the command does
3. **Outline** — numbered execution steps:
   - Step 1: Read `.specify/feature.json` to locate the active spec
   - Step 2: Parse spec.md for acceptance scenarios (GWT format)
   - Step 3: Check for `contracts/testing-surface-*.md` files
   - Step 4: Detect project context (framework, playwright.config, existing POs)
   - Step 5: Resolve `acceptance-test-template` via template resolution stack
   - Step 6: Generate test files (one per user story) with page objects and fixtures
   - Step 7: If contracts exist, generate provider-verification tests
   - Step 8: Display summary of generated files
4. **Output Format** — defines the traceability header, test naming convention, and file structure
5. **Incremental Update Rules** — how to handle re-runs (detect existing files by header marker, add/modify/skip)
6. **Done When** — checklist of completion criteria

## Consumers

- Spec Kit command runner (invokes the command file)
- `/speckit-implement` (invokes the command during task execution)
- Developers (manual invocation via `/speckit-trasgospec-acceptance-tests`)

## Validation Rules

- File MUST have `description` in YAML frontmatter
- File MUST NOT have `scripts` key in YAML frontmatter
- File MUST reference `$ARGUMENTS` for user input
- File MUST include template resolution via `specify preset resolve acceptance-test-template`
