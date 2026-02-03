# Prepress (`pps`)

A modern, polyglot release management tool for Python, Rust, Node.js, and Go projects.

*prepress is dogfooding its own release management!*

[**View Website**](https://omneity-labs.github.io/prepress/)

## Features
- **Changelog-Centric**: Uses `CHANGELOG.md` as the source of truth.
- **Polyglot**: Supports `pyproject.toml`, `Cargo.toml`, `package.json`, and `go.mod`.
- **Trusted Publishing**: Scaffolds GitHub Actions for secure OIDC-based publishing (PyPI/npm/crates.io).
- **Safety**: AST-based version injection and robust dry-run previews.

### Go projects
Go modules don't have a standard version field in `go.mod`, so Prepress uses git tags (e.g. `v1.2.3`) as is [standard practice](https://go.dev/blog/publishing-go-modules) in the Go ecosystem.
Run `pps init` to scaffold a minimal Go CI workflow (along with `CHANGELOG.md`).

## Installation
```bash
pip install prepress
# or
uv tool install prepress
```

## Usage
```bash
pps # Show current project status
pps status # same as above

pps init     # Setup project
pps note     # Add changelog entry
pps bump     # Increment version
pps preview  # Check release notes
pps release  # Tag and ship
```

## Documentation
For detailed workflows and command references, see the [User Guide](GUIDE.md).

## License
This project is licensed under the MIT License.

Copyright **Omar Kamali** ([omarkamali.com](https://omarkamali.com))

A project by **Omneity Labs** ([omneitylabs.com](https://omneitylabs.com))

