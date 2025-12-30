# Prepress (`pps`) - Project Plan

Prepress is a modern, polyglot release management tool designed for Python, Rust, and Node.js projects. It prioritizes a "Single Source of Truth" (Changelog) and provides a guided, safe DX for shipping software.

## Core Philosophy
- **Changelog-Centric**: The `CHANGELOG.md` (Keep a Changelog format) is the source of truth for release notes.
- **Zero-Config**: Auto-detects project types and "just works."
- **Safety First**: Mandatory clean-git checks and robust previews.
- **Modern Standards**: Promotes `importlib.metadata` for Python and Trusted Publishing for CI/CD.

## Architecture: Driver-Based "Plan & Execute"
The tool is built with a decoupled architecture to ensure reliability across different ecosystems.

1. **Core Engine**: A state machine that calculates the "Release Plan" based on current state and user intent.
2. **Drivers**:
    - `PythonDriver`: Handles `pyproject.toml` and `__init__.py` (AST-based).
    - `RustDriver`: Handles `Cargo.toml`.
    - `NodeDriver`: Handles `package.json`.
    - `ChangelogDriver`: Specialized Markdown parser for versioned sections.
3. **Executioner**: Safely applies the plan, with validation at each step.

## CLI Commands & DX Flows

### 1. `pps init`
Initializes the project for Prepress.
- Creates `CHANGELOG.md` if missing.
- Offers to modernize `__init__.py` with `importlib.metadata`.
- **Trusted Publishing**: Generates `.github/workflows/publish.yml` tailored for the detected language (PyPI, npm, or crates.io) using OIDC.

### 2. `pps note "<message>"`
Quickly adds an entry to the `## [Unreleased]` section of the changelog.
- Defaults to the `### Added` subsection.
- Supports `--fixed`, `--changed`, `--removed` flags.

### 3. `pps bump [patch|minor|major]`
Prepares the project for a new version.
- Updates version strings in all detected manifests.
- Renames `## [Unreleased]` to `## [X.Y.Z] - YYYY-MM-DD`.
- Creates a `chore: bump version to X.Y.Z` commit.

### 4. `pps preview`
The "Sanity Check".
- Displays the detected version.
- Shows exactly what will be sent to the GitHub Release body.
- Validates consistency between manifests and changelog.

### 5. `pps release`
The final step.
- Runs pre-release hooks (e.g., tests).
- Tags the commit (e.g., `vX.Y.Z`).
- Pushes to origin.
- Uses `gh` CLI to create a GitHub Release with the extracted notes.

### 6. `pps status`
Shows the current release readiness of the project.

## Testing Strategy
- **Sandbox Testing**: Use `pytest` with `tmp_path` to simulate projects.
- **Polyglot Fixtures**: Pre-defined templates for Python, Rust, and Node.js projects.
- **Mocked Shell**: Intercept Git and GitHub CLI calls to verify behavior without side effects.
- **Snapshot Testing**: Ensure Markdown formatting remains consistent.

## Implementation Roadmap
1. [x] Scaffold package structure and CLI entry point.
2. [x] Implement `ChangelogDriver` (Parser/Writer).
3. [x] Implement `PythonDriver` (TOML + AST).
4. [x] Implement `pps init` with GitHub Action templates.
5. [x] Implement `pps bump` and `pps preview`.
6. [x] Implement `pps release` (Git + GitHub CLI).
7. [x] Implement `pps note` and `pps status`.
