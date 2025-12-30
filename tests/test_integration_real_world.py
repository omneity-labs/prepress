import pytest
import shutil
from pathlib import Path
from prepress.core.drivers.python import PythonDriver
from prepress.core.drivers.rust import RustDriver
from prepress.core.drivers.node import NodeDriver

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
