<!--
Sync Impact Report
===================
Version change: 1.2.0 -> 1.3.0
Modified principles: None
Added sections:
  - Principle VI: Test-Driven Development (new core principle)
  - Task Organization subsection in Development Workflow
  - Testing Constraints subsection in Development Workflow
Removed sections: None
Deferred TODOs: None
-->

# Trasgo Spec Kit Constitution

## Core Principles

### I. Composition Over Creation

Bundles compose existing Spec Kit components (extensions, presets,
workflows, steps) into a single, versioned, installable unit.
Composition of existing primitives is the default and preferred
approach.

When a bundle needs runtime behavior that cannot be achieved through
composition alone, it MAY introduce new behavior provided it follows
the Spec Kit extension development pattern. Extensions MUST use
documented Spec Kit extension points, hooks, and lifecycle contracts.
Custom runtime behavior that bypasses Spec Kit's extension mechanism
is prohibited.

**Rationale**: Pure composition keeps bundles predictable and
upgradeable, but some features genuinely require new behavior.
Channeling that behavior through Spec Kit's extension pattern
ensures discoverability, testability, and compatibility with the
platform's lifecycle.

### II. Spec Kit Native

All components MUST follow Spec Kit development guides and leverage
existing Spec Kit features. The bundle MUST NOT duplicate or
re-implement functionality already provided by Spec Kit primitives.
When a Spec Kit capability exists, it MUST be used instead of building
a custom alternative.

**Rationale**: Duplication creates drift. Leveraging the platform
ensures compatibility across Spec Kit versions and reduces maintenance
burden.

### III. Documentation-Driven Development

Spec Kit documentation MUST be consulted during planning before
selecting components or designing workflows. Tooling choices
(extensions, presets, workflows, steps) MUST be deliberate and
justified against available Spec Kit capabilities. We are Spec Kit
specialists — every decision MUST be informed by the official
documentation.

**Rationale**: Uninformed choices lead to reinventing solved problems.
Consulting documentation first ensures optimal use of the platform.

### IV. Idempotent & Traceable

Every component installation MUST be idempotent — running install
twice produces the same result with no side effects. Full provenance
tracking MUST be maintained so that any component can be cleanly
removed or refreshed. Failed installs MUST NOT leave orphaned
provenance records.

**Rationale**: Idempotency and traceability are prerequisites for
reliable automation and clean uninstallation across teams.

### V. Version-Pinned Distribution

Bundle manifests MUST pin component versions explicitly. Version pins
are the distribution contract — consumers MUST be able to rely on
deterministic installs. Pin enforcement is applied at install and
update time through the bundle's own machinery.

**Rationale**: Unpinned versions produce non-reproducible environments.
Explicit pins guarantee that every consumer gets the same stack.

### VI. Test-Driven Development

All feature work MUST follow a strict TDD cycle: tests are written
FIRST and MUST fail (red) before any implementation code is written.
Only after the failing test is confirmed does implementation proceed
to make the test pass (green), followed by refactoring if needed.

- Tests MUST be written and executed exclusively via **pytest**. No
  other test runner is permitted.
- Test execution MUST occur through the pytest tool integration —
  developers MUST NOT run test commands manually via bash/shell.
- Each implementation task MUST begin with a failing test that
  validates the expected behavior before the production code exists.
- The red-green-refactor cycle is non-negotiable and MUST be
  verifiable in commit history (test commits preceding or
  accompanying implementation commits).

**Rationale**: Writing tests first forces precise specification of
behavior before implementation, catches design flaws early, and
produces a comprehensive regression suite as a natural byproduct.
Standardizing on pytest ensures consistent tooling and reporting
across the project.

## Bundle Architecture Constraints

- The `bundle.yml` manifest is the single source of truth for a
  bundle's component set, version pins, and metadata.
- Components resolve through the catalog stack in priority order:
  project, user, built-in.
- The only cross-bundle conflict point is the active integration;
  bundles targeting a different integration than the project's MUST
  abort installation with no changes.
- Integration-agnostic bundles inherit the project's active
  integration.
- On installation failure, no provenance record is written and
  partially installed components are removed on a best-effort basis.

## Extension Development Pattern

When a bundle introduces new runtime behavior (per Principle I), it
MUST follow this two-component pattern:

### Command File

Location: `bundle/commands/<dot.namespaced.id>.md`

- MUST include YAML frontmatter with `description` and `scripts`
  keys.
- The `scripts` key MUST declare platform-specific script paths
  (`sh` for bash, `ps` for PowerShell).
- The markdown body contains AI agent instructions: it MUST invoke
  the declared script, parse its JSON output, and handle
  presentation and edge-case messaging.
- The command MUST NOT perform deterministic calculations itself;
  all deterministic work MUST be delegated to the script.

### Script File

Location: `bundle/scripts/bash/<script-name>.sh` (and/or
`bundle/scripts/powershell/<script-name>.ps1`)

- MUST be deterministic only — no AI calls, no judgment, no
  presentation logic.
- MUST emit a stable JSON contract on stdout (single line).
  Diagnostics go to stderr.
- MUST target bash 3.2+ for macOS compatibility (no `mapfile`,
  no `readarray`, no process substitution for core paths).
- MUST source core `.specify/scripts/bash/common.sh`
  opportunistically with an inline fallback for `json_escape`
  when the core helper is unavailable.
- MUST locate the repo root via `find_specify_root` (or
  equivalent walk-up) rather than assuming CWD.
- MUST use `set -euo pipefail`.
- Exit code 0 on success, non-zero on error.

### Naming Convention

- Command IDs use dot namespacing: `speckit.<bundle-id>.<name>`
  (e.g., `speckit.trasgospec.roadmap`).
- Dots map to hyphens at invocation: `/speckit-trasgospec-roadmap`.

### Separation of Concerns

- **Script**: deterministic filesystem operations, data extraction,
  configuration resolution, JSON output. Testable in isolation.
- **Command**: AI agent instructions for running the script, parsing
  JSON, rendering user-facing output, handling empty/error states.
- This separation ensures reproducibility (scripts produce the same
  output for the same input) and testability (scripts can be tested
  without an AI agent).

## Development Workflow

- Consult Spec Kit documentation before choosing or composing
  components for inclusion in the bundle.
- Use the Spec Kit workflow (specify, plan, implement) for all
  feature work on this bundle.
- Validate bundles (`specify bundle validate`) before publishing.
- Test install paths from clean projects to verify end-to-end
  resolution and integration compatibility.
- Reference non-default catalog URLs in documentation when the
  bundle depends on components from those catalogs.

### Task Organization

Tasks MUST be grouped by user story. Each user story represents a
cohesive unit of user-facing value, and its tasks MUST be listed
together in dependency order beneath it. This grouping applies to
`tasks.md` generation and any task tracking artifacts.

### Testing Constraints

- All tests MUST use **pytest** as the sole test framework.
- Test execution MUST occur through pytest tool integration, never
  via manual bash/shell commands.
- Every implementation task MUST begin with writing a failing test
  before any production code.

## Governance

This constitution supersedes all other development practices for
Trasgo Spec Kit. Compliance with these principles MUST be verified
during spec and plan reviews.

- **Amendments**: Any change to this constitution MUST be documented
  with a version bump, rationale, and migration plan if the change
  affects existing workflows.
- **Versioning**: Constitution versions follow semantic versioning:
  MAJOR for principle removals or incompatible redefinitions, MINOR
  for new principles or materially expanded guidance, PATCH for
  clarifications and wording fixes.
- **Compliance review**: Every spec and plan review MUST include a
  constitution compliance check. Non-compliance MUST be resolved
  before implementation proceeds.

**Version**: 1.3.0 | **Ratified**: 2026-08-07 | **Last Amended**: 2026-08-08
