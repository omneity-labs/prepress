import pytest
from typer.testing import CliRunner
from prepress.cli import app
from pathlib import Path
import subprocess
from unittest.mock import patch, MagicMock

runner = CliRunner()

@pytest.fixture
def mock_repo(tmp_path):
    # Create a fake python project
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-pkg"\nversion = "0.1.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n\n### Added\n- Initial\n")
    return tmp_path

def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Prepress v" in result.output

def test_cli_status(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    # Mock subprocess.run for git check
    with patch("prepress.cli.run_cmd") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
        assert "Clean" in result.output

def test_cli_note(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    result = runner.invoke(app, ["note", "New feature"])
    assert result.exit_code == 0
    assert "Added note" in result.output
    assert "- New feature" in (mock_repo / "CHANGELOG.md").read_text()

def test_cli_bump(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    # Mock Confirm.ask to return True
    with patch("rich.prompt.Confirm.ask", return_value=True):
        result = runner.invoke(app, ["bump", "minor"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
        assert "0.2.0" in result.output
        assert 'version = "0.2.0"' in (mock_repo / "pyproject.toml").read_text()
        assert "## [0.2.0]" in (mock_repo / "CHANGELOG.md").read_text()

def test_cli_preview(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    result = runner.invoke(app, ["preview"])
    assert result.exit_code == 0
    assert "Version: 0.1.0" in result.output
    assert "- Initial" in result.output

def test_cli_release(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    with patch("rich.prompt.Confirm.ask", return_value=True), \
         patch("prepress.cli.run_cmd") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        result = runner.invoke(app, ["release"])
        assert result.exit_code == 0
        assert "Releasing v0.1.0" in result.output
        # Verify git tag was called
        mock_run.assert_any_call(["git", "tag", "-a", "v0.1.0", "-m", "Release v0.1.0"])

def test_cli_default_status(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    with patch("prepress.cli.run_cmd") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Prepress Status" in result.output
        assert "0.1.0" in result.output

def test_cli_default_no_changelog(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.1.0"\n')
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "no CHANGELOG.md detected" in result.output
    assert "pps init" in result.output

def test_cli_default_no_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "No manifest found" in result.output
    assert "pyproject.toml" in result.output
