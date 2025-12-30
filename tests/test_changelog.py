import pytest
from pathlib import Path
from prepress.core.drivers.changelog import ChangelogDriver

def test_changelog_exists(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    driver = ChangelogDriver(path)
    assert not driver.exists()
    path.write_text("# Changelog")
    assert driver.exists()

def test_get_latest_version(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text("""# Changelog
## [1.2.3] - 2023-01-01
### Added
- Feature A
""")
    driver = ChangelogDriver(path)
    assert driver.get_latest_version() == "1.2.3"

def test_get_unreleased_notes(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text("""# Changelog
## [Unreleased]
### Added
- New feature
- Another one

## [1.2.3] - 2023-01-01
""")
    driver = ChangelogDriver(path)
    notes = driver.get_unreleased_notes()
    assert "### Added" in notes
    assert "- New feature" in notes
    assert "## [1.2.3]" not in notes

def test_add_note(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text("# Changelog\n\n## [Unreleased]\n")
    driver = ChangelogDriver(path)
    driver.add_note("Test note", "Fixed")
    
    content = path.read_text()
    assert "### Fixed" in content
    assert "- Test note" in content

def test_bump(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text("""# Changelog
## [Unreleased]
### Added
- Feature X

## [1.0.0] - 2023-01-01
""")
    driver = ChangelogDriver(path)
    driver.bump("1.1.0")
    
    content = path.read_text()
    assert "## [Unreleased]" in content
    assert "## [1.1.0] -" in content
    assert "### Added" in content
    assert "- Feature X" in content
    # Check order: Unreleased should be at top
    assert content.find("## [Unreleased]") < content.find("## [1.1.0]")
