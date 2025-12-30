import re
from pathlib import Path
from typing import Optional
from .base import BaseDriver

class RustDriver(BaseDriver):
    def detect(self) -> bool:
        return (self.root / "Cargo.toml").exists()

    def get_version(self) -> Optional[str]:
        cargo_path = self.root / "Cargo.toml"
        if not cargo_path.exists():
            return None
        
        content = cargo_path.read_text()
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def set_version(self, version: str):
        cargo_path = self.root / "Cargo.toml"
        content = cargo_path.read_text()
        
        if "[package]" in content:
            parts = content.split("[package]", 1)
            if len(parts) == 2:
                before, after = parts
                new_after = re.sub(
                    r'(?m)^version\s*=\s*"[^"]+"',
                    f'version = "{version}"',
                    after,
                    count=1
                )
                cargo_path.write_text(before + "[package]" + new_after)
                return

        new_content = re.sub(
            r'(?m)^version\s*=\s*"[^"]+"',
            f'version = "{version}"',
            content,
            count=1
        )
        cargo_path.write_text(new_content)
