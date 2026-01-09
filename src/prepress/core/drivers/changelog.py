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
            # Try to anchor it above the first version found
            version_match = re.search(r'## \[v?\d+\.\d+\.\d+\]', content)
            if version_match:
                index = version_match.start()
                content = content[:index] + "## [Unreleased]\n\n" + content[index:]
            else:
                # Fallback to after the title if no versions found
                if "# Changelog" in content:
                    content = content.replace("# Changelog", "# Changelog\n\n## [Unreleased]", 1)
                else:
                    content = "## [Unreleased]\n\n" + content
        
        section_header = f"### {section}"
        # Ensure section header exists specifically in the Unreleased section
        unreleased_match = re.search(r'## \[Unreleased\]', content)
        if unreleased_match:
            unreleased_end_match = re.search(r'\n## \[', content[unreleased_match.end():])
            unreleased_end = unreleased_match.end() + unreleased_end_match.start() if unreleased_end_match else len(content)
            unreleased_block = content[unreleased_match.start():unreleased_end]
            
            if section_header not in unreleased_block:
                # Add section under Unreleased
                pos = unreleased_match.end()
                content = content[:pos].rstrip() + f"\n\n{section_header}\n\n" + content[pos:].lstrip()
        
        # Append note to the first occurrence of the section header
        section_pattern = rf'({re.escape(section_header)}\s*)'
        new_content = re.sub(section_pattern, rf'\1- {message}\n', content, count=1)
        
        # Ensure there's a newline before the next header if we just appended to the end of Unreleased
        if re.search(rf'- {re.escape(message)}\n## \[', new_content):
            new_content = new_content.replace(f"- {message}\n## [", f"- {message}\n\n## [")

        self.path.write_text(new_content)
