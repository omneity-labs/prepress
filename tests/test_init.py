import pytest
from typer.testing import CliRunner
from prepress.cli import app
from pathlib import Path
from unittest.mock import patch

runner = CliRunner()

def test_cli_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-pkg"\nversion = "0.1.0"\n')
    
    # Mock Confirm.ask to return True for all questions
    with patch("rich.prompt.Confirm.ask", return_value=True):
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Initializing Prepress" in result.output
        
        assert (tmp_path / "CHANGELOG.md").exists()
        assert (tmp_path / ".github" / "workflows" / "publish.yml").exists()
        
        publish_yml = (tmp_path / ".github" / "workflows" / "publish.yml").read_text()
        assert "test-pkg" in publish_yml

def test_cli_init_modernize_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-pkg"\nversion = "0.1.0"\n')
    pkg_dir = tmp_path / "test_pkg"
    pkg_dir.mkdir()
    init_py = pkg_dir / "__init__.py"
    init_py.write_text('__version__ = "0.1.0"')
    
    with patch("rich.prompt.Confirm.ask", return_value=True):
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Modernized test_pkg/__init__.py" in result.output
        
        content = init_py.read_text()
        assert "importlib.metadata" in content
        assert 'version("test-pkg")' in content
