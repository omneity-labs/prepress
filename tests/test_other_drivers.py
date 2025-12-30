import pytest
from pathlib import Path
from prepress.core.drivers.rust import RustDriver
from prepress.core.drivers.node import NodeDriver

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
