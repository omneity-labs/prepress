# Prepress (`pps`)

A modern, polyglot release management tool for Python, Rust, and Node.js projects.

[**View Website**](https://omneity-labs.github.io/prepress/)

## Features
- **Changelog-Centric**: Uses `CHANGELOG.md` as the source of truth.
- **Polyglot**: Supports `pyproject.toml`, `Cargo.toml`, and `package.json`.
- **Trusted Publishing**: Scaffolds GitHub Actions for secure OIDC-based publishing.
- **Safety**: AST-based version injection and robust dry-run previews.

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

