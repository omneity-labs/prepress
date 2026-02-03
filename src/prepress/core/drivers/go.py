from pathlib import Path
from typing import Optional
import subprocess
import shutil

import semver

from .base import BaseDriver


class GoDriver(BaseDriver):
    """Go projects are versioned via git tags (vX.Y.Z)."""

    def detect(self) -> bool:
        return (self.root / "go.mod").exists()

    def get_version(self) -> Optional[str]:
        tags = self._list_semver_tags()
        if not tags:
            return None
        latest = max(tags, key=lambda t: t[0])
        return str(latest[0])

    def set_version(self, version: str):
        """Create a local git tag for the version if possible.

        This is intentionally non-intrusive: if git is unavailable, the repo
        has no commits, or the version is invalid, it silently no-ops.
        """
        parsed = self._parse_semver(version)
        if parsed is None:
            return

        if not shutil.which("git"):
            return

        if not self._has_commits():
            return

        tag = f"v{parsed}"
        if self._tag_exists(tag):
            return

        subprocess.run(
            ["git", "tag", "-a", tag, "-m", f"Release {tag}"],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )

    def _list_semver_tags(self) -> list[tuple[semver.Version, str]]:
        if not shutil.which("git"):
            return []

        result = subprocess.run(
            ["git", "tag", "--list"],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        tags: list[tuple[semver.Version, str]] = []
        for raw in result.stdout.splitlines():
            parsed = self._parse_semver(raw)
            if parsed is not None:
                tags.append((parsed, raw))
        return tags

    def _parse_semver(self, value: str) -> Optional[semver.Version]:
        raw = value.strip()
        if raw.startswith("v"):
            raw = raw[1:]
        try:
            return semver.Version.parse(raw)
        except ValueError:
            return None

    def _has_commits(self) -> bool:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _tag_exists(self, tag: str) -> bool:
        result = subprocess.run(
            ["git", "tag", "-l", tag],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() == tag
