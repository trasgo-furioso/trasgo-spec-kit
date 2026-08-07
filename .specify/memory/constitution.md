<!--
Sync Impact Report
===================
Version change: (new) -> 1.0.0
Modified principles: N/A (initial ratification)
Added sections:
  - Core Principles (5 principles)
  - Bundle Architecture Constraints
  - Development Workflow
  - Governance
Removed sections: None
Deferred TODOs: None
-->

# Trasgo Spec Kit Constitution

## Core Principles

### I. Composition Over Creation

Bundles compose existing Spec Kit components (extensions, presets,
workflows, steps) into a single, versioned, installable unit. A bundle
MUST NOT introduce new runtime behavior. It is a distribution and
composition layer over Spec Kit primitives — nothing more.

**Rationale**: Bundles that add runtime behavior blur the boundary
between distribution and implementation, making upgrades unpredictable
and debugging harder.

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

**Version**: 1.0.0 | **Ratified**: 2026-08-07 | **Last Amended**: 2026-08-07
