import pytest
import shutil
from pathlib import Path
import subprocess
import shutil as _shutil

from prepress.core.drivers.python import PythonDriver
from prepress.core.drivers.rust import RustDriver
from prepress.core.drivers.node import NodeDriver
from prepress.core.drivers.go import GoDriver

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_python_complex_integration(tmp_path):
    # Setup
    src_dir = FIXTURES_DIR / "python_complex"
    dest_dir = tmp_path / "python_complex"
    shutil.copytree(src_dir, dest_dir)
    
    driver = PythonDriver(dest_dir)
    assert driver.get_version() == "1.2.3"
    
    # Bump
    driver.set_version("1.3.0")
    
    # Verify
    content = (dest_dir / "pyproject.toml").read_text()
    assert 'version = "1.3.0"' in content
    # Ensure dependencies were NOT touched
    assert 'requests>=2.25.1' in content
    assert 'typer==0.9.0' in content
    # Ensure tool config was NOT touched
    assert '# version = "0.1.0"' in content

def test_rust_complex_integration(tmp_path):
    # Setup
    src_dir = FIXTURES_DIR / "rust_complex"
    dest_dir = tmp_path / "rust_complex"
    shutil.copytree(src_dir, dest_dir)
    
    driver = RustDriver(dest_dir)
    assert driver.get_version() == "0.5.0"
    
    # Bump
    driver.set_version("0.6.0")
    
    # Verify
    content = (dest_dir / "Cargo.toml").read_text()
    assert 'version = "0.6.0"' in content
    # Ensure dependencies were NOT touched
    assert 'serde = { version = "1.0"' in content
    assert 'tokio = { version = "1.0"' in content

def test_node_complex_integration(tmp_path):
    # Setup
    src_dir = FIXTURES_DIR / "node_complex"
    dest_dir = tmp_path / "node_complex"
    shutil.copytree(src_dir, dest_dir)
    
    driver = NodeDriver(dest_dir)
    assert driver.get_version() == "2.1.0"
    
    # Bump
    driver.set_version("2.2.0")
    
    # Verify package.json
    pkg_content = (dest_dir / "package.json").read_text()
    assert '"version": "2.2.0"' in pkg_content
    assert '"lodash": "^4.17.21"' in pkg_content
    
    # Verify package-lock.json
    lock_content = (dest_dir / "package-lock.json").read_text()
    assert '"version": "2.2.0"' in lock_content
    # Check nested package version
    import json
    lock_data = json.loads(lock_content)
    assert lock_data["packages"][""]["version"] == "2.2.0"


def test_go_complex_integration(tmp_path):
    # Setup
    src_dir = FIXTURES_DIR / "go_complex"
    dest_dir = tmp_path / "go_complex"
    shutil.copytree(src_dir, dest_dir)

    if not _shutil.which("git"):
        pytest.skip("git is required for Go integration tests")

    subprocess.run(["git", "init"], cwd=dest_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=dest_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=dest_dir, check=True)
    subprocess.run(["git", "add", "go.mod"], cwd=dest_dir, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=dest_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "tag", "v0.9.0"], cwd=dest_dir, check=True)

    driver = GoDriver(dest_dir)
    assert driver.detect()
    assert driver.get_version() == "0.9.0"

    # Bump
    driver.set_version("0.10.0")

    # Verify
    tags = subprocess.run(["git", "tag", "-l"], cwd=dest_dir, check=True, capture_output=True, text=True).stdout
    assert "v0.10.0" in tags
    # Ensure go.mod wasn't modified
    go_mod = (dest_dir / "go.mod").read_text()
    assert "module example.com/go-complex" in go_mod
