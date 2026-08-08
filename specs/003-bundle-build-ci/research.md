# Research: Bundle Build CI

## R1: Git Pre-Push Hook Mechanics

**Decision**: Use git's pre-push hook with stdin parsing for ref detection.

**Rationale**: The pre-push hook receives the remote name and URL as arguments, and ref information via stdin in the format `<local ref> <local sha> <remote ref> <remote sha>`. This allows detecting which branch is being pushed and which commits are new, enabling targeted bundle change detection via `git diff --name-only <remote-sha>..<local-sha> -- bundle/`.

**Alternatives considered**:
- Pre-commit hook: Too frequent, runs on every commit during iterative development
- CI pipeline: Requires environment setup, not leveraging local tooling
- Post-commit hook: Cannot block the push on validation failure

## R2: Hook Distribution via core.hooksPath

**Decision**: Store hooks in `.githooks/` directory tracked by git, activate via `git config core.hooksPath .githooks`.

**Rationale**: `core.hooksPath` is supported in git 2.9+ (2016), widely available. It allows the hook to be version-controlled and shared. A setup script sets this config once per clone.

**Alternatives considered**:
- Symlink from `.git/hooks/`: Requires per-hook symlinking, fragile
- Copy scripts into `.git/hooks/`: Copies drift from source, not auto-updated
- Tool-managed (husky, pre-commit): Adds external dependency, overkill for a single hook

## R3: Bundle Change Detection

**Decision**: Use `git diff --name-only` between the remote SHA and local SHA to check for files under `bundle/`.

**Rationale**: The pre-push hook receives the remote and local SHAs via stdin. Comparing them with `git diff --name-only` is efficient and only detects changes in the commits being pushed, not the entire history. Filtering with `-- bundle/` limits the check to the relevant directory.

**Alternatives considered**:
- Checking staged files: Not applicable in pre-push context (commits are already made)
- Using `git log --name-only`: More complex parsing, same result

## R4: YAML Parsing in Bash

**Decision**: Use simple grep/sed patterns to extract fields from `bundle/bundle.yml`.

**Rationale**: The bundle manifest has a flat, predictable structure. Fields like `version`, `id`, `name`, `description`, and `role` are top-level under `bundle:` with simple key-value syntax. Complex YAML parsing is unnecessary. For the multiline `description` (using `>-`), we read the indented continuation line.

**Alternatives considered**:
- Requiring yq: Adds external dependency
- Python helper: Available but overkill for flat YAML
- Sourcing a separate parser: Over-engineering for known structure

## R5: catalog.json Update Strategy

**Decision**: Use sed for in-place JSON field updates in `catalog.json`.

**Rationale**: The catalog JSON structure is well-known, flat, and stable (`schema_version: 1.0`). The fields to update are `version`, `description`, and `download_url` — all simple string replacements within a known structure. No nested objects or arrays need manipulation.

**Alternatives considered**:
- jq: Most robust, but adds external dependency not present in project
- Python one-liner: Available via venv but adds complexity to a bash script
- Full JSON rewrite: Brittle if structure changes

## R6: .gitignore Conflict with *.zip

**Decision**: Add a negation pattern to `.gitignore` for the bundle zip artifact.

**Rationale**: The `.gitignore` currently contains `*.zip` which would prevent the bundle artifact from being committed. Adding `!trasgospec-*.zip` (or the specific filename pattern produced by `specify bundle build`) allows the bundle artifact through while keeping other zip files ignored.

**Alternatives considered**:
- Using `git add -f`: Works but requires remembering the force flag; fragile in automated scripts
- Removing `*.zip` entirely: Would allow all zip files, losing protection against accidental commits
- Moving the artifact to a non-ignored directory: Changes the build output path, conflicts with `specify bundle build --output .`

## R7: GitHub Raw URL Inference from SSH Remote

**Decision**: Parse the git remote URL (SSH or HTTPS) to extract owner/repo for constructing the raw.githubusercontent.com download URL.

**Rationale**: The remote URL is `git@github.com:trasgo-furioso/trasgo-spec-kit.git`. This can be parsed with sed to extract `trasgo-furioso` (owner) and `trasgo-spec-kit` (repo), then construct `https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/refs/heads/main/<filename>`.

**Parsing patterns**:
- SSH: `git@github.com:<owner>/<repo>.git` → extract via `sed 's/.*github.com[:/]\(.*\)\/\(.*\)\.git/\1 \2/'`
- HTTPS: `https://github.com/<owner>/<repo>.git` → same sed pattern works

## R8: Auto-Commit Strategy in Pre-Push Hook

**Decision**: After building artifacts, create a new commit with `git add` + `git commit` before allowing the push to proceed.

**Rationale**: The pre-push hook runs after commits are made but before they are sent. Creating a new commit at this point adds it to the push. The hook must handle the case where the working tree has unstaged changes by stashing them, creating the build commit, then restoring.

**Key steps**:
1. Stash any uncommitted changes (if present)
2. Run validate + build
3. Update catalog.json
4. `git add <zip-file> catalog.json`
5. `git commit -m "chore: build bundle vX.Y.Z"`
6. Restore stash (if applied)
7. Exit 0 to allow push (which now includes the new commit)

**Alternatives considered**:
- Amending the last commit: Changes commit hash, confusing if already referenced
- Blocking push and asking developer to commit manually: Adds friction, defeats automation purpose

## R9: Testing Strategy for Pre-Push Hook

**Decision**: Test the hook logic as a standalone bash script via pytest + subprocess, following the existing `test_scan_specs.py` pattern.

**Rationale**: The project already tests bash scripts via `subprocess.run()` in pytest, creating isolated temporary project directories. The pre-push hook can be tested the same way — create a temp git repo, make bundle changes, invoke the hook script, and verify the output (zip created, catalog.json updated, commit created).

**Key test considerations**:
- Need a temp git repo with a remote (can use `git init --bare` for a local remote)
- Need `specify` CLI available in test environment
- Test both the hook script directly and the setup script
