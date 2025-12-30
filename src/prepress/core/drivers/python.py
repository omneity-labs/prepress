import re
from pathlib import Path
from typing import Optional
import libcst as cst
from .base import BaseDriver

try:
    import tomllib
except ImportError:
    import tomli as tomllib

class PythonDriver(BaseDriver):
    def detect(self) -> bool:
        return (self.root / "pyproject.toml").exists()

    def get_version(self) -> Optional[str]:
        pyproject_path = self.root / "pyproject.toml"
        if not pyproject_path.exists():
            return None
        
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version")

    def set_version(self, version: str):
        self._update_pyproject(version)
        self._update_init_py(version)

    def _update_pyproject(self, version: str):
        pyproject_path = self.root / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # More robust replacement: only replace version under [project]
        if "[project]" in content:
            parts = content.split("[project]", 1)
            if len(parts) == 2:
                before, after = parts
                # Only replace the first version = "..." after [project]
                new_after = re.sub(
                    r'(?m)^version\s*=\s*"[^"]+"',
                    f'version = "{version}"',
                    after,
                    count=1
                )
                pyproject_path.write_text(before + "[project]" + new_after)
                return

        # Fallback
        new_content = re.sub(
            r'(?m)^version\s*=\s*"[^"]+"',
            f'version = "{version}"',
            content,
            count=1
        )
        pyproject_path.write_text(new_content)

    def _update_init_py(self, version: str):
        # Find __init__.py in src/<pkg>/ or <pkg>/
        # This is a simplified search
        for path in self.root.rglob("__init__.py"):
            content = path.read_text()
            if "__version__" in content:
                # Use libcst to safely update __version__
                tree = cst.parse_module(content)
                
                class VersionTransformer(cst.CSTTransformer):
                    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
                        for target in original_node.targets:
                            if (
                                isinstance(target.target, cst.Name) 
                                and target.target.value == "__version__"
                                and isinstance(original_node.value, cst.SimpleString)
                            ):
                                return updated_node.with_changes(
                                    value=cst.SimpleString(f'"{version}"')
                                )
                        return updated_node

                new_tree = tree.visit(VersionTransformer())
                path.write_text(new_tree.code)
