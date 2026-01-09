# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

## [0.1.2] - 2026-01-09

### Added
- Anchor missing `Unreleased` section above the most recent version when adding notes (changelog driver).
- Detect current git branch and remote when pushing tags; push to the branch's configured remote instead of assuming `origin/main`.
- Add global `--yes/-y` flag to auto-approve confirmations while still displaying approved steps.
- Improve push behavior to run `git push` without capturing output so SSH prompts and `~/.ssh/config` hosts are honored.

### Changed
- Update `pps release`, `pps bump`, and `pps init` to confirm detailed actions (e.g. "pushing commit X to branch Y") and respect the `--yes` flag.
- Add tests covering changelog anchoring, branch/remote detection, and auto-approve flows.

## [0.1.1] - 2026-01-03

### Added
- Allow skipping tag creation in `pps release` if the tag already exists.
- Improved error handling for existing git tags.

## [0.1.0] - 2025-12-30

### Added
- AST-based version modernization for Python __init__.py
- GitHub Trusted Publishing (OIDC) scaffolding
- Automated changelog management (Keep a Changelog format)
- Support for Python, Rust, and Node.js manifests
- Initial release of Prepress
- Initial project setup.
