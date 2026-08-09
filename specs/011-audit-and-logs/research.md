# Research: Audit and Logs

## R1: How to detect changed/new files in the spec directory

**Decision**: Use `git status --porcelain` scoped to the spec directory path to detect both untracked (new) and modified files.

**Rationale**: `git status --porcelain` provides a stable, machine-parseable output format across git versions. By scoping to the spec directory path (e.g., `git status --porcelain -- specs/011-audit-and-logs/`), we get exactly the files we need without touching anything outside. The porcelain format uses status codes (`??` for untracked, `M` for modified, `A` for added) that are easy to parse in bash 3.2.

**Alternatives considered**:
- `git diff --name-only`: Only detects modified tracked files, misses new untracked files
- `find` + timestamp comparison: Requires storing a baseline timestamp, fragile across platforms
- `git diff --name-only HEAD` + `git ls-files --others`: Two commands, more complex parsing but would work. Rejected because `git status --porcelain` provides both in one call.

## R2: How to generate meaningful descriptions from the AI command

**Decision**: The command file (AI agent) runs the script to get the list of changed files, then for each file inspects the diff (via `git diff` for modified files) or file content (for new files) to generate a brief one-liner description. The descriptions are assembled into the commit message.

**Rationale**: The two-part pattern requires the script to be deterministic (no AI). The script outputs the list of changed files as JSON. The command file (AI agent) then uses its judgment to write descriptions — this is the same pattern as flow-nudge where the script gathers state and the command decides what to present.

**Alternatives considered**:
- Script generates generic descriptions ("updated", "created"): Too uninformative, doesn't meet FR-003 for meaningful descriptions
- Pass descriptions via environment variable from the calling skill: Would require modifying every existing skill command — invasive and fragile

## R3: Commit message format and git invocation

**Decision**: Use a multi-line commit message via heredoc:
```
<file1> - <description1>
<file2> - <description2>
[speckit:audit]
```

The command stages files with `git add -- <spec_dir>/` and commits with the formatted message.

**Rationale**: Matches the format decided during discovery. The `[speckit:audit]` tag on its own line enables `git log --grep='[speckit:audit]'` filtering. Using `git add -- <spec_dir>/` is safe because it only stages files within the spec directory.

**Alternatives considered**:
- `[speckit:audit]` as a prefix on the first line: Would appear in `git log --oneline` but the multi-file format doesn't have a natural single-line summary
- Separate tag line (e.g., `Tags: speckit:audit`): Non-standard, harder to grep

## R4: Hook registration pattern for multiple after_* hooks

**Decision**: Register the audit-commit command as an `after_*` hook in `extension.yml` for each artifact-producing skill phase: `after_discovery`, `after_specify`, `after_clarify`, `after_checklist`, `after_plan`, `after_tasks`, `after_implement`, `after_converge`. All registrations use `priority: 20` and `optional: false`.

**Rationale**: Priority 20 ensures the audit hook runs after all existing hooks (status advancement at priority 5, flow-nudge at priority 10). This means the commit captures all artifact changes including those made by other hooks.

The `extensions.yml` installed at `.specify/extensions.yml` is the runtime hook registry (populated during `specify bundle install`). The `extension.yml` in the bundle source declares hooks that the installer merges into the project's `extensions.yml`.

**Alternatives considered**:
- Single generic `after_all` hook: Spec Kit doesn't support a wildcard hook — each phase must be registered individually
- Higher priority (e.g., 50): Would work but 20 is sufficient given current max is 10

## R5: Script JSON contract design

**Decision**: The script outputs:
```json
{
  "spec_dir": "specs/011-audit-and-logs",
  "changed_files": ["spec.md", "plan.md"],
  "new_files": ["research.md"],
  "has_changes": true,
  "on_branch": true,
  "branch": "011-audit-and-logs",
  "error": null
}
```

**Rationale**: Follows the existing pattern (flow-context.sh, flow-nudge.sh) of emitting a single-line JSON object on stdout. The `has_changes` boolean lets the command quickly decide whether to proceed. Separating `changed_files` and `new_files` lets the command tailor descriptions (e.g., "created" vs "updated"). The `on_branch` flag handles the detached HEAD edge case.

**Alternatives considered**:
- Include file diffs in the JSON: Too large, and diffs may contain characters that break JSON encoding. Better for the command to run `git diff` itself.
- Flat file list without new/changed distinction: Less information for description generation.

## R6: Error handling strategy

**Decision**: The script exits 0 with `"error"` field set when recoverable (e.g., no spec directory, detached HEAD). The command reads the error and displays it as a warning. The script exits non-zero only for truly fatal errors (not a git repo). The command never blocks the preceding skill's completion — errors in the audit hook are warnings only.

**Rationale**: The audit hook is a convenience feature. A failure to commit should never prevent a user from completing their workflow. This matches the spec's FR-007.

**Alternatives considered**:
- Exit non-zero for all errors: Would make the hook appear to "fail", potentially confusing users or triggering retry logic
- Silent skip on all errors: Users would not know their artifacts weren't committed
