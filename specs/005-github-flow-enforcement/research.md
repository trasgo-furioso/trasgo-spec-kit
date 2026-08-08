# Research: GitHub Flow Enforcement

## R1: How do hook commands know which phase triggered them?

**Decision**: The flow-gate command has two modes: `after_specify` (create/switch branch) and `before_*` (block on main). It distinguishes them by checking whether `feature.json` was just created (specify just ran) vs. already existed. The flow-nudge command infers the phase by examining which spec artifacts exist in the feature directory.

**Rationale**: The spec-kit hook mechanism invokes commands by name without passing the hook point identifier. Rather than requiring separate commands per phase, state-based inference is deterministic and aligns with the two-part pattern (script does deterministic work).

**Inference logic**:
- `plan.md` exists but no `tasks.md` → plan phase completed → suggest draft PR
- `tasks.md` exists → implement/converge phase → suggest mark PR ready
- After analyze runs, the flow-nudge checks if PR is already ready; if not, suggests final review

**Alternative considered**: Register three separate commands (`flow-nudge-plan`, `flow-nudge-implement`, `flow-nudge-analyze`). Rejected because it triples the command surface area for identical logic with minor variations.

## R2: How does flow-context.sh calculate branch age?

**Decision**: Branch age is calculated as the number of days since the first commit on the branch that is not reachable from `main`. If no such commit exists (branch just created with no commits), age is 0.

**Rationale**: Git does not track branch creation time. The first divergent commit is the most reliable proxy.

**Implementation approach**:
```bash
first_commit=$(git log main..HEAD --format="%ai" --reverse | head -1)
```
If empty, age is 0. Otherwise, compute day difference from current date.

**Alternative considered**: Using reflog timestamps. Rejected because reflogs expire and are not reliable across clones.

## R3: How should flow-gate handle the specify phase (chicken-and-egg)?

**Decision**: Specify is exempt from `before_*` gating. Instead, flow-gate runs as a mandatory `after_specify` hook. After specify creates `feature.json` and `spec.md`, the hook reads the `**Feature Branch**:` field from spec.md, and if the developer is not already on that branch, creates and switches to it — but only if the branch doesn't already exist. If the branch already exists, it switches to it.

**Rationale**: The specify skill creates the spec directory, `feature.json`, and `spec.md` (which contains the `**Feature Branch**` field). The gate cannot run before specify because the branch name source (spec.md) doesn't exist yet. Running after specify means the spec is created on `main` but immediately moved to a feature branch before any further work happens. This matches natural GitHub Flow: you decide to start a feature, then branch.

**Alternative considered**: Block `before_specify` and ask the user to name a branch manually. Rejected because the branch name comes from spec.md, which specify creates — asking the user to pre-name it duplicates what specify already does.

## R4: Where does the branch name come from?

**Decision**: The branch name is read from the `**Feature Branch**: \`<name>\`` field in the active spec's `spec.md`. It is used as-is — no prefix (`feat/`, `feature/`, etc.) is added. The extraction uses the same grep-based pattern matching that `scan-specs.sh` uses for title and status.

**Rationale**: The spec file is the source of truth for the feature. The developer controls the branch name when they write the spec. Using it verbatim avoids convention conflicts and lets teams use whatever naming scheme they prefer.

**Extraction pattern**:
```bash
branch_line=$(grep -m1 '^\*\*Feature Branch\*\*:' "$spec_file" 2>/dev/null || true)
# Strip prefix, backticks, and whitespace
```

**Alternative considered**: Derive branch name from the spec directory name (e.g., `specs/005-foo/` → `feat/005-foo`). Rejected because it imposes a `feat/` convention and couples the branch name to the directory structure. The `**Feature Branch**` field gives the developer explicit control.

## R5: How should gh_integration be configured?

**Decision**: The `gh_integration` setting is read from `.specify/extensions.yml` under `settings.gh_integration`. Default is `true` when not present.

**Rationale**: The extensions.yml file already has a `settings` section and is the natural place for extension-level configuration. This avoids creating a new configuration file. The setting applies to the trasgospec extension as a whole since both hook commands may need it.

**Configuration location**: `.specify/extensions.yml`
```yaml
settings:
  gh_integration: true  # default
```

**Alternative considered**: Command-level `inputs` in frontmatter. Rejected because the setting should be project-wide, not per-invocation.

## R6: Script architecture — one script or two?

**Decision**: Two scripts: `flow-context.sh` (git-local state only) and `flow-nudge.sh` (PR state and phase inference). The flow-gate command file invokes `flow-context.sh` directly. The flow-nudge command file invokes `flow-nudge.sh`, which sources `flow-context.sh` and adds PR-specific fields.

**Rationale**: Separation of concerns. `flow-context.sh` is fast and offline (pure git). `flow-nudge.sh` may call `gh` (network-dependent). The gate should never be slow or fail due to network issues.

**Alternative considered**: Single `flow-context.sh` that does everything. Rejected because the gate hook must be fast and reliable — it fires on every skill invocation. Network calls belong only in the nudge path.

## R7: What happens on detached HEAD?

**Decision**: The flow-gate blocks execution and reports `current_branch: null`, `is_main: false`. The command file explains that a named feature branch is required and offers to create one.

**Rationale**: Detached HEAD is not a valid state for GitHub Flow. The developer needs to be on a named branch for PRs and traceability.

## R8: Hook registration during bundle install — mechanism

**Decision**: The bundle installation process (which already handles extension.yml deployment) will also update `.specify/extensions.yml` to add hook entries. This is part of the bundle's install contract.

**Rationale**: Spec-kit bundles already modify `.specify/extensions.yml` during installation (adding to the `installed` list). Adding hook entries follows the same pattern.

**Idempotency**: Before adding a hook entry, check if an entry with the same `extension` and `command` already exists at that hook point. If so, skip. This ensures `install` can be run multiple times safely.

**Note**: The exact mechanism for hook registration during install needs to be investigated during implementation. The current bundle install flow updates `extensions.yml` for the `installed` list, but hook registration may require additional logic. This could be a manual step documented in the bundle README until an automated hook registration mechanism is available.
