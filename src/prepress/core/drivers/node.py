import json
from pathlib import Path
from typing import Optional
from .base import BaseDriver

class NodeDriver(BaseDriver):
    def detect(self) -> bool:
        return (self.root / "package.json").exists()

    def get_version(self) -> Optional[str]:
        pkg_path = self.root / "package.json"
        if not pkg_path.exists():
            return None
        
        with open(pkg_path, "r") as f:
            data = json.load(f)
            return data.get("version")

    def set_version(self, version: str):
        pkg_path = self.root / "package.json"
        with open(pkg_path, "r") as f:
            data = json.load(f)
        
        data["version"] = version
        
        with open(pkg_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        
        # Also update package-lock.json if it exists
        lock_path = self.root / "package-lock.json"
        if lock_path.exists():
            with open(lock_path, "r") as f:
                lock_data = json.load(f)
            
            lock_data["version"] = version
            if "packages" in lock_data and "" in lock_data["packages"]:
                lock_data["packages"][""]["version"] = version
            
            with open(lock_path, "w") as f:
                json.dump(lock_data, f, indent=2)
                f.write("\n")
        
