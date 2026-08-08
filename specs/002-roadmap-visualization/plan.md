# Implementation Plan: Roadmap Visualization

**Branch**: `002-roadmap-visualization` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-roadmap-visualization/spec.md`

## Summary

Add a `/speckit-trasgospec-roadmap` command to the Trasgo Spec Kit bundle
using the Spec Kit extension development pattern. The feature comprises
two components:

1. **A shell script** (`bundle/scripts/bash/scan-specs.sh`) that
   deterministically scans the `specs/` directory, extracts metadata
   (title, status, creation date) from each `spec.md`, and emits a
   stable JSON contract on stdout.
2. **A command file** (`bundle/commands/speckit.trasgospec.roadmap.md`)
   with YAML frontmatter pointing to the script and markdown
   instructions that direct the AI agent to run the script, parse
   its JSON output, and render the results as a markdown table.

This follows the Spec Kit extension pattern: deterministic work in
scripts, judgment and presentation in the command's AI instructions.
The constitution (v1.1.0) now permits runtime behavior via this
pattern.

## Technical Context

**Language/Version**: Bash 3.2+ (script, macOS-compatible), Markdown
(command definition), YAML (frontmatter + bundle manifest), Python
3.11+ (dev-only testing)

**Primary Dependencies**:
- `specify` CLI (command invocation and bundle management)
- Core `.specify/scripts/bash/common.sh` (sourced for `json_escape`,
  `find_specify_root` helpers — no hard dependency, fallback provided)
- `pytest` (dev-only, integration tests)

**Storage**: N/A (reads existing `spec.md` files from filesystem)

**Testing**: pytest (TDD) — tests are written FIRST and must FAIL
before implementation. Two test layers:
- **Unit tests** (`tests/unit/test_scan_specs.py`): test
  `scan-specs.sh` directly via `subprocess.run`, using `tmp_path`
  fixtures to create controlled spec directory structures. Validate
  JSON contract output (Arrange/Act/Assert).
- **Integration tests** (`tests/integration/test_us1_roadmap.py`):
  end-to-end acceptance scenarios from spec user stories, using
  the existing `conftest.py` fixtures and `run_specify` helper.
All testing is done through pytest — never run bash commands
manually to try things out; encapsulate them in tests.

**Target Platform**: Spec Kit projects using the `claude` integration

**Project Type**: Spec Kit bundle extension (command + script)

**Performance Goals**: Script completes in under 5 seconds for up to
50 specs (SC-001). JSON output is single-line for reliable parsing.

**Constraints**:
- Script is deterministic only — no judgment, no markdown rendering,
  no AI calls. It resolves paths and extracts text patterns.
- Command file contains the AI instructions for presentation.
- Bash 3.2+ compatibility (macOS default): no `mapfile`, no
  `readarray`, no process substitution for core paths.
- Script MUST source core `common.sh` opportunistically (fallback
  `json_escape` if unavailable).

**Scale/Scope**: 1 new command + 1 new script added to existing
bundle. Bundle version bump from 0.1.0 to 0.2.0.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Composition Over Creation | PASS | New runtime behavior follows SK extension pattern (command + script). Script uses documented extension points (scripts frontmatter, core common.sh). No bypass of SK mechanism. |
| II. Spec Kit Native | PASS | Uses SK command format (YAML frontmatter + markdown), SK script conventions, `bundle.yml` provides section, core helpers |
| III. Documentation-Driven | PASS | Researched SK extension pattern from user-provided examples; script follows `load-config.sh` conventions (repo root resolution, json_escape, common.sh sourcing) |
| IV. Idempotent & Traceable | PASS | Read-only command; does not modify any files. Bundle install remains idempotent via SK machinery |
| V. Version-Pinned Distribution | PASS | New command version-pinned in `bundle.yml` provides section |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-roadmap-visualization/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── scan-specs-output.md  # JSON contract for script output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/
├── bundle.yml                              # Updated: add command + script
├── commands/
│   └── speckit.trasgospec.roadmap.md       # NEW: command (YAML frontmatter + AI instructions)
├── scripts/
│   └── bash/
│       └── scan-specs.sh                   # NEW: deterministic spec scanner
└── skills/
    ├── trasgospec/
    │   └── SKILL.md                        # Existing hello command (unchanged)
    └── trasgospec-roadmap/
        └── SKILL.md                        # NEW: skill trigger that delegates to command

tests/
├── unit/
│   ├── __init__.py                         # NEW
│   └── test_scan_specs.py                  # NEW: script unit tests (JSON contract)
└── integration/
    ├── __init__.py                          # Existing
    ├── conftest.py                          # Shared fixtures (reuse from 001)
    ├── test_us1_install.py                  # Existing (unchanged)
    ├── test_edge_cases.py                   # Existing (unchanged)
    └── test_us1_roadmap.py                  # NEW: e2e acceptance tests
```

**Structure Decision**: Extension pattern separates deterministic
logic (script) from AI presentation (command). The script lives in
`bundle/scripts/bash/` following the convention from the roadmap
extension example (`load-config.sh`). The command lives in
`bundle/commands/` with dot-namespaced ID `speckit.trasgospec.roadmap`
(invoked as `/speckit-trasgospec-roadmap`). A thin skill in
`bundle/skills/trasgospec-roadmap/` triggers the command.
