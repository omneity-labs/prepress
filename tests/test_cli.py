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

def test_cli_bump_auto_approve(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    result = runner.invoke(app, ["-y", "bump", "minor"])
    assert result.exit_code == 0
    assert "auto-approved" in result.output
    assert "0.2.0" in result.output
    assert 'version = "0.2.0"' in (mock_repo / "pyproject.toml").read_text()

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

def test_cli_release_branch_detection(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    with patch("rich.prompt.Confirm.ask", return_value=True), \
         patch("prepress.cli.run_cmd") as mock_run:
        
        # Configure mock_run side effects for multiple calls
        def side_effect(cmd, **kwargs):
            if cmd == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
                return MagicMock(stdout="feature-branch")
            if cmd == ["git", "config", "branch.feature-branch.remote"]:
                return MagicMock(stdout="upstream")
            if cmd == ["git", "tag", "-l", "v0.1.0"]:
                return MagicMock(stdout="")
            return MagicMock(returncode=0, stdout="")
            
        mock_run.side_effect = side_effect
        
        result = runner.invoke(app, ["release"])
        assert result.exit_code == 0
        
        # Verify it pushed to the correct branch and remote
        mock_run.assert_any_call(["git", "push", "upstream", "feature-branch"], capture=False)
        mock_run.assert_any_call(["git", "push", "upstream", "v0.1.0"], capture=False)
        assert "Pushing to upstream/feature-branch" in result.output

def test_cli_release_tag_exists(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    with patch("rich.prompt.Confirm.ask", return_value=True), \
         patch("prepress.cli.run_cmd") as mock_run:
        
        def side_effect(cmd, **kwargs):
            if cmd == ["git", "tag", "-l", "v0.1.0"]:
                return MagicMock(stdout="v0.1.0\n")
            return MagicMock(returncode=0, stdout="")
            
        mock_run.side_effect = side_effect
        
        result = runner.invoke(app, ["release"])
        assert result.exit_code == 0
        assert "Tag v0.1.0 already exists." in result.output
        
        # Verify git tag -a was NOT called
        for call in mock_run.call_args_list:
            assert call.args[0] != ["git", "tag", "-a", "v0.1.0", "-m", "Release v0.1.0"]

def test_cli_release_auto_approve(mock_repo, monkeypatch):
    monkeypatch.chdir(mock_repo)
    with patch("prepress.cli.run_cmd") as mock_run:
        # No mock for Confirm.ask needed because of -y
        mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
        
        result = runner.invoke(app, ["-y", "release"])
        assert result.exit_code == 0
        assert "auto-approved" in result.output
        assert "Releasing v0.1.0" in result.output
        # Verify it pushed - branch and remote will both be "main" based on our mock's return value
        mock_run.assert_any_call(["git", "push", "main", "main"], capture=False)
