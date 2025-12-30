from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class BaseDriver(ABC):
    def __init__(self, root: Path):
        self.root = root

    @abstractmethod
    def detect(self) -> bool:
        """Return True if this driver is applicable to the project."""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Return the current version string."""
        pass

    @abstractmethod
    def set_version(self, version: str):
        """Update the version string in the project files."""
        pass
