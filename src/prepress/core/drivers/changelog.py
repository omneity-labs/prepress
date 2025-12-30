import re
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

class ChangelogDriver:
    def __init__(self, path: Path):
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def get_latest_version(self) -> Optional[str]:
        if not self.exists():
            return None
        content = self.path.read_text()
        match = re.search(r'## \[(\d+\.\d+\.\d+)\]', content)
        return match.group(1) if match else None

    def get_unreleased_notes(self) -> str:
        if not self.exists():
            return ""
        content = self.path.read_text()
        # Find content between ## [Unreleased] and the next ## section
        match = re.search(r'## \[Unreleased\]\s*(.*?)(?=\n## \[|\Z)', content, re.DOTALL)
        if not match:
            return ""
        return match.group(1).strip()

    def bump(self, new_version: str):
        if not self.exists():
            return
        
        content = self.path.read_text()
        today = date.today().isoformat()
        
        # Replace [Unreleased] with the new version and date
        new_header = f"## [{new_version}] - {today}"
        
        # Check if [Unreleased] exists
        if "## [Unreleased]" in content:
            # Insert a new empty [Unreleased] section above the newly bumped version
            replacement = f"## [Unreleased]\n\n### Added\n\n{new_header}"
            new_content = content.replace("## [Unreleased]", replacement)
        else:
            # If no [Unreleased], just prepend or handle as needed
            # For now, assume [Unreleased] exists as per "Keep a Changelog"
            new_content = content
            
        self.path.write_text(new_content)

    def add_note(self, message: str, section: str = "Added"):
        if not self.exists():
            return
        
        content = self.path.read_text()
        if "## [Unreleased]" not in content:
            # Create Unreleased section if missing
            content = content.replace("# Changelog\n", f"# Changelog\n\n## [Unreleased]\n\n### Added\n")
        
        section_header = f"### {section}"
        if section_header not in content:
            # Add section under Unreleased
            unreleased_match = re.search(r'## \[Unreleased\]\s*', content)
            if unreleased_match:
                pos = unreleased_match.end()
                content = content[:pos] + f"\n{section_header}\n" + content[pos:]
        
        # Append note to section
        section_pattern = rf'({re.escape(section_header)}\s*)'
        new_content = re.sub(section_pattern, rf'\1- {message}\n', content, count=1)
        self.path.write_text(new_content)
