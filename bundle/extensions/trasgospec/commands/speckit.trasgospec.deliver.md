---
description: Deliver PR lifecycle actions at workflow milestones.
scripts:
  sh: scripts/bash/deliver.sh
---

## User Input

```text
$ARGUMENTS
```

## Goal

Execute pull request actions at workflow milestones. This command runs as a mandatory `after_*` hook at the plan, implement, analyze, and discovery phases. It creates draft PRs, marks them ready for review, or flags final review — all without prompting for confirmation.

## Outline

1. Run `{SCRIPT}` from the repo root and parse the JSON output.

2. Resolve the `pr-template` via the Spec Kit preset resolution stack:
   - Attempt to read `.specify/templates/overrides/pr-template.md` first
   - Then `.specify/presets/trasgospec/templates/pr-template.md`
   - If neither exists, use hardcoded defaults:
     - Title: `feat(<spec_dir_basename>): <spec_title>`
     - Body: `## Summary\n\n<spec_summary>`

3. If the template is found:
   - Parse YAML frontmatter for `title` pattern
   - Read markdown body for PR body pattern
   - Read the feature's `spec.md` to extract:
     - `{{spec_title}}` — from the `# Feature Specification: <title>` heading
     - `{{spec_summary}}` — from the Problem Statement section (first paragraph after `**Pain Point**:`)
   - Replace `{{spec_title}}` and `{{spec_summary}}` placeholders in both title and body
   - Also replace `{{spec_dir}}` in the title with the spec directory basename

4. Check `suggested_action` to determine what to do:

   - **`none`**: No action needed. Display "PR is up to date." or nothing.

   - **`create_draft`**: Create a draft PR.

     If `gh_integration` is `true` and `gh_available` is `true`:
     - Run `gh pr create --draft --title "<interpolated_title>" --body "<interpolated_body>"`
     - If successful: Display the resulting PR URL
     - If `gh pr create` fails: Display the error message and continue (do NOT block the workflow or change feature status)

     If `gh_integration` is `false` OR `gh_available` is `false`:
     - Display the suggested PR details:
       ```
       PR Action Suggested: Open Draft PR

         Title:  <interpolated_title>
         Branch: <current_branch> → main
         Body:   <first line of interpolated body>

         Run: gh pr create --draft --title "..." --body "..."
       ```

   - **`mark_ready`**: Mark the PR as ready for review.

     If `gh_integration` is `true` and `gh_available` is `true`:
     - Run `gh pr ready`
     - If successful: Display confirmation with PR number
     - If `gh pr ready` fails: Display the error message and continue

     If `gh_integration` is `false` OR `gh_available` is `false`:
     - Display:
       ```
       PR Action Suggested: Mark Ready for Review

         PR: #<pr_number> (<pr_url>)

         Run: gh pr ready
       ```

   - **`final_review`**: Flag the PR as ready for final review.

     Display:
     ```
     PR Status: Ready for Final Review

       PR: #<pr_number> (<pr_url>)

       The implementation and analysis phases are complete.
       This PR is ready for team review and merge.
     ```

5. If `gh_available` is `false` and `gh_integration` is `true`:
   - Display once: "Note: `gh` CLI not found. Install it for automated PR management, or set `gh_integration: false` in `.specify/extensions.yml`."
