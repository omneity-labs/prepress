# Prepress (`pps`) User Guide

Prepress is a release management tool designed to make shipping software boring and predictable. It automates the tedious parts of versioning and changelog management so you can focus on writing code.

## Core Commands

### `pps init`
**The Onboarding.** Run this once per project.
- Creates a `CHANGELOG.md` if you don't have one.
- Offers to modernize your Python `__init__.py` to use `importlib.metadata`.
- Scaffolds `.github/workflows/publish.yml` for Trusted Publishing (OIDC).

### `pps note "<message>"`
**The Developer's Diary.** Use this as you work.
- Adds a bullet point to the `## [Unreleased]` section of your changelog.
- Use `-s Fixed` or `-s Changed` to categorize your notes.
- *Tip: Run this right after you merge a PR.*

### `pps status`
**The Reality Check.**
- Compares your manifest version (`pyproject.toml`, `Cargo.toml`, etc.) with your changelog.
- Tells you if you have unreleased notes waiting to be shipped.

### `pps bump [patch|minor|major|<version>]`
**The Preparation.**
- Updates your version strings across all manifests.
- Moves your `[Unreleased]` notes into a new versioned section with today's date.
- Commits the changes with a clean message.

### `pps preview`
**The Final Look.**
- Shows you exactly what the GitHub Release body will look like.
- Ensures your regexes and parsers are seeing what you expect.

### `pps release`
**The Ship It Button.**
- Verifies your git state is clean.
- Creates a git tag (e.g., `v1.2.3`).
- Pushes the branch and the tag to origin.
- Creates a GitHub Release using the notes extracted from your changelog.

---

## Proposed Workflows

### 1. The "Continuous Documenter" (Recommended)
*Best for: Teams who want a perfect changelog without the end-of-sprint stress.*

1. **Work**: Implement a feature.
2. **Note**: `pps note "Added support for dark mode"`
3. **Repeat**: Do this for every meaningful change.
4. **Ship**: When ready, run `pps bump minor` then `pps release`.
5. **Result**: Your users get a beautiful, human-written changelog every time.

### 2. The "One-Shot" Release
*Best for: Small fixes or solo projects where you just want to get it out.*

1. **Fix**: Squash that bug.
2. **Bump**: `pps bump patch`
3. **Note**: `pps note "Fixed the login timeout bug" -s Fixed`
4. **Release**: `pps release`
5. **Result**: Version updated and shipped in 30 seconds.

### 3. The "Safety First" Flow
*Best for: Critical infrastructure or large projects.*

1. **Prepare**: `pps bump minor`
2. **Verify**: `pps preview`
3. **Test**: Run your CI/CD or local test suite.
4. **Release**: `pps release`
5. **Result**: Zero-surprise releases.

---

## Why Prepress?
Most tools either auto-generate "garbage" changelogs from messy commit messages or require complex configuration. Prepress assumes you care about your users enough to write a one-sentence note about your changes, and it handles the rest of the plumbing for you.
