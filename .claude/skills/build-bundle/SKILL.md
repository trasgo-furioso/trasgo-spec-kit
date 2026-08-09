---
name: build-bundle
description: "Build the trasgospec bundle: bump version, build ZIPs, update catalogs, place all artifacts."
argument-hint: "<version> e.g. 0.7.0"
user-invocable: true
---

## User Input

```text
$ARGUMENTS
```

## Goal

Build and package the trasgospec bundle with all artifacts in the correct locations, ready to commit and push.

## Outline

1. **Parse version** from `$ARGUMENTS`. If empty, determine the current version by fetching the live catalog from main: `curl -s https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/refs/heads/main/catalog.json` and extracting `bundles.trasgospec.version`. Display the current version and auto-increment the minor version (e.g., `0.7.0` → `0.8.0`). Ask the user to confirm or provide a different version.

2. **Detect branch** by running `git branch --show-current`.

3. **Count commands** by reading `bundle/extensions/trasgospec/extension.yml` and counting entries under `provides.commands`.

4. **Validate** the bundle before building: `specify bundle validate --path bundle --offline`. Stop if validation fails.

5. **Bump version** in these files (replace ALL occurrences of the old version string with the new one):
   - `bundle/bundle.yml` — both `bundle.version` and `provides.extensions[0].version`
   - `bundle/extensions/trasgospec/extension.yml` — `extension.version`

6. **Build bundle ZIP** via `specify bundle build --path bundle`. This creates `bundle/trasgospec-<version>.zip`.

7. **Copy bundle ZIP** to repo root: `cp bundle/trasgospec-<version>.zip trasgospec-<version>.zip`

8. **Build extension ZIP** from `bundle/extensions/trasgospec/`:
   ```bash
   cd bundle/extensions/trasgospec && zip -r ../../../trasgospec-extension-<version>.zip extension.yml scripts/ commands/
   ```

9. **Update `catalog.json`** with:
   - `version`: new version
   - `download_url`: `https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/<branch>/trasgospec-<version>.zip`

10. **Update `extension-catalog.json`** with:
    - `version`: new version
    - `catalog_url`: `https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/<branch>/extension-catalog.json`
    - `download_url`: `https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/<branch>/trasgospec-extension-<version>.zip`
    - `provides.commands`: actual command count from step 3
    - `updated_at`: current ISO 8601 timestamp

11. **Re-validate** after build: `specify bundle validate --path bundle --offline`

12. **Report** all artifacts created/updated:
    - `bundle/bundle.yml` (version bumped)
    - `bundle/extensions/trasgospec/extension.yml` (version bumped)
    - `trasgospec-<version>.zip` (bundle ZIP at root)
    - `trasgospec-extension-<version>.zip` (extension ZIP at root)
    - `catalog.json` (updated)
    - `extension-catalog.json` (updated)

13. **Do NOT commit or push.** Just report what was done and suggest:
    ```
    Ready to commit. Suggested command:
    git add bundle/bundle.yml bundle/extensions/trasgospec/extension.yml \
           catalog.json extension-catalog.json \
           trasgospec-<version>.zip trasgospec-extension-<version>.zip \
    && git commit -m "chore: build bundle v<version>"
    ```

## Done When

- [ ] Version bumped in bundle.yml and extension.yml
- [ ] Bundle ZIP built and placed at repo root
- [ ] Extension ZIP built and placed at repo root
- [ ] catalog.json updated with correct version and download URL
- [ ] extension-catalog.json updated with correct version, download URL, and command count
- [ ] Bundle validates after build
- [ ] Artifacts reported to user
