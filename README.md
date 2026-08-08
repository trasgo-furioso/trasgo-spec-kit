# Trasgo Spec Kit

Journey-first product specification for spec-driven development.

A curated bundle of [GitHub Spec Kit](https://github.com/github/spec-kit).

## Philosophy

**Design experiences, not components.** System architecture emerges from delivering user experiences — not the other way around. Every piece of work is a journey: an experience someone wants to deliver.

**The process is fractal.** The same specify → plan → tasks → implement cycle applies at every level. A stakeholder specifying a product vision and a developer implementing a checkout flow are doing the same thing at different zoom levels.

**One entity type, infinite depth.** There are no tasks, stories, or epics. There are only journeys. A product vision is a journey. A feature is a journey. A bug fix is a journey. When a journey is too big to implement directly, you decompose it into smaller journeys and run the process again.

## Install

```bash
# Add both the bundle catalog and extension catalog
specify bundle catalog add https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/refs/heads/main/catalog.json --policy install-allowed
specify extension catalog add https://raw.githubusercontent.com/trasgo-furioso/trasgo-spec-kit/refs/heads/main/extension-catalog.json --name trasgospec --install-allowed

# Install the bundle
specify bundle install trasgospec
```

## Development

### Setup

After cloning, activate the git hooks:

```bash
./scripts/setup.sh
```

This configures `git core.hooksPath` to use the tracked `.githooks/` directory, enabling the automated bundle build on push.

### Bundle Build Automation

A pre-push hook automatically validates and builds the bundle when you push changes to `bundle/` on main. The flow requires two pushes:

1. **First `git push`**: The hook validates, builds, updates `catalog.json`, creates a `chore: build bundle vX.Y.Z` commit, and **blocks the push** (the new commit can't be added to an in-flight push).
2. **Second `git push`**: The hook detects the build commit is already at HEAD and lets the push through, including all artifacts.

Pushes that don't touch `bundle/` pass through silently. Validation failures block the push.

### Tests

```bash
pytest tests/unit/ -v
```

## Components

- `/speckit-trasgospec-hello` — Verify bundle installation
- `/speckit-trasgospec-roadmap` — View project roadmap as a markdown table
