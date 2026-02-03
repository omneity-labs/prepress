import pytest
from pathlib import Path
import shutil
import subprocess

from prepress.core.drivers.rust import RustDriver
from prepress.core.drivers.node import NodeDriver
from prepress.core.drivers.go import GoDriver


def _init_git_repo(path: Path):
    if not shutil.which("git"):
        pytest.skip("git is required for Go driver tests")

    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)

    (path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True, text=True)

def test_rust_driver(tmp_path):
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text("[package]\nname = \"test\"\nversion = \"0.1.0\"\n")
    driver = RustDriver(tmp_path)
    assert driver.detect()
    assert driver.get_version() == "0.1.0"
    driver.set_version("0.2.0")
    assert "version = \"0.2.0\"" in cargo.read_text()

def test_node_driver(tmp_path):
    pkg = tmp_path / "package.json"
    pkg.write_text('{"name": "test", "version": "0.1.0"}')
    driver = NodeDriver(tmp_path)
    assert driver.detect()
    assert driver.get_version() == "0.1.0"
    driver.set_version("0.2.0")
    assert '"version": "0.2.0"' in pkg.read_text()


def test_go_driver(tmp_path):
    (tmp_path / "go.mod").write_text("module example.com/test\n\ngo 1.22\n")
    _init_git_repo(tmp_path)
    subprocess.run(["git", "tag", "v0.1.0"], cwd=tmp_path, check=True)

    driver = GoDriver(tmp_path)
    assert driver.detect()
    assert driver.get_version() == "0.1.0"

    driver.set_version("0.2.0")
    tags = subprocess.run(["git", "tag", "-l"], cwd=tmp_path, check=True, capture_output=True, text=True).stdout
    assert "v0.2.0" in tags
