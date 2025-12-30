import pytest
from pathlib import Path
from prepress.core.drivers.python import PythonDriver

def test_python_detect(tmp_path):
    driver = PythonDriver(tmp_path)
    assert not driver.detect()
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"0.1.0\"")
    assert driver.detect()

def test_get_version(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"1.2.3\"")
    driver = PythonDriver(tmp_path)
    assert driver.get_version() == "1.2.3"

def test_set_version_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = \"test\"\nversion = \"0.1.0\"\n")
    driver = PythonDriver(tmp_path)
    driver.set_version("0.2.0")
    
    assert "version = \"0.2.0\"" in pyproject.read_text()

def test_set_version_init_py(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"0.1.0\"")
    pkg_dir = tmp_path / "src" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    init_py = pkg_dir / "__init__.py"
    init_py.write_text("__version__ = \"0.1.0\"\n")
    
    driver = PythonDriver(tmp_path)
    driver.set_version("0.2.0")
    
    assert "__version__ = \"0.2.0\"" in init_py.read_text()

def test_set_version_init_py_modern(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"0.1.0\"")
    pkg_dir = tmp_path / "src" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    init_py = pkg_dir / "__init__.py"
    init_py.write_text("""from importlib.metadata import version
__version__ = version("test_pkg")
""")
    
    driver = PythonDriver(tmp_path)
    driver.set_version("0.2.0")
    
    # Should NOT change __version__ if it's using importlib.metadata
    # Actually, my current implementation might try to change it if it sees __version__
    # Let's see what happens.
    content = init_py.read_text()
    assert "version(\"test_pkg\")" in content
