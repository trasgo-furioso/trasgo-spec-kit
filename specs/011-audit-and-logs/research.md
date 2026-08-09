# Research: Audit and Logs

## R1: Script responsibility — what does commit.sh do vs the command file?

**Decision**: The script (`commit.sh`) gathers deterministic git state: runs `git status --porcelain` repo-wide, extracts file paths and statuses, checks branch state, and emits JSON. The command file (AI) receives this JSON, inspects diffs/content to generate descriptions, decides what to include (asking the user when unsure), then runs `git add`, `git commit`, and `git push`.

**Rationale**: Follows the two-part pattern — the script does no AI work, the command does no deterministic filesystem work. The script's JSON gives the AI enough context to make decisions. The AI performs `git add`/`commit`/`push` directly since it needs to construct the commit message dynamically.

**Alternatives considered**:
- Script does staging + commit: Would require the script to generate descriptions, violating the no-AI rule
- Script provides diffs in JSON: Diffs can be large and contain characters that break JSON encoding; better for the command to run `git diff` itself when needed

## R2: How the AI generates file descriptions

**Decision**: For each changed file, the command inspects the diff (via `git diff` for modified files) or file content (for new files). It produces a brief one-liner description focusing on what changed and why. Descriptions should be concise (under 80 chars) and meaningful.

**Rationale**: The AI already has full session context from the preceding skill invocation. Combined with diff inspection, it can produce meaningful descriptions without any inter-hook communication mechanism.

**Alternatives considered**:
- Generic descriptions ("updated", "created"): Too uninformative to serve as an audit trail
- Skill passes context via environment/file: Invasive, requires modifying every skill

## R3: How the AI decides what to include

**Decision**: The command includes all changed/new files by default. It asks the user before including files that are:
- Potential secrets (.env, credentials, tokens, keys)
- Binary files or large generated artifacts
- Files that appear unrelated to the current feature/skill context

The AI uses its judgment — no hardcoded rules in the script.

**Rationale**: The AI already understands the context of the preceding skill. Hardcoding rules in the script would be brittle and incomplete. The AI's judgment handles edge cases naturally.

**Alternatives considered**:
- Hardcoded exclude patterns in the script: Inflexible, can't adapt to context
- Always include everything: Risks committing secrets or unrelated changes

## R4: Push behavior and failure handling

**Decision**: After a successful commit, the command runs `git push`. If push fails, it displays the error and warns the user, but leaves the commit in place. The command never blocks the preceding skill's completion.

**Rationale**: Push failures are usually infrastructure issues (network, permissions, branch protection) that the user needs to resolve manually. Rolling back the commit would defeat the purpose of preserving work.

**Alternatives considered**:
- Retry push: Network issues are usually transient but retrying adds complexity and delay
- Ask user what to do: The user already has the commit; they can push manually

## R5: .specify/ gitignore strategy

**Decision**: Add `.specify/` to the project's `.gitignore`. This directory contains user-environment state (feature.json, extensions.yml, installed extensions) that is managed by Spec Kit per-user, not project source code.

**Rationale**: Without this, the commit command would pick up `.specify/` changes on every invocation, creating noise and merge conflicts between developers. The `.specify/` directory is analogous to `.vscode/` or `.idea/` — per-user tool configuration.

**Alternatives considered**:
- Hardcode `.specify/` exclusion in the commit script: Would work but doesn't solve the broader problem of `.specify/` being tracked
- Add to global gitignore: Per-user setting, not enforceable across team

## R6: Hook registration — which skills get after_* hooks

**Decision**: Register `after_*` hooks for 8 artifact-producing skills: discovery, specify, clarify, checklist, plan, tasks, implement, converge. All use `priority: 20` and `optional: false`.

**Rationale**: Priority 20 ensures the commit hook runs after all existing hooks (status at 5, flow-nudge at 10). This means the commit captures all changes, including those made by other hooks. All 8 skills can produce artifacts that should be committed.

**Alternatives considered**:
- Include `analyze` and `roadmap`: These are read-only commands; no artifacts to commit
- Make the hook optional: Defeats the purpose — audit trail must be automatic
