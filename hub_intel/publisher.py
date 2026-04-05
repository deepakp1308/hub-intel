"""Publish reports to GitHub repository and GitHub Pages."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

from hub_intel.config import DOCS_DIR, REPORTS_DIR, ROOT_DIR

logger = logging.getLogger(__name__)


class GitHubPublisher:
    """Manages git operations for report publishing."""

    def __init__(self, repo_dir: Optional[Path] = None):
        self.repo_dir = repo_dir or ROOT_DIR

    def publish(self, date_str: str, commit_msg: Optional[str] = None) -> bool:
        """Stage, commit, and push new report files."""
        if commit_msg is None:
            commit_msg = f"HUB-INTEL report: {date_str}"

        try:
            self._run_git("add", "reports/", "docs/")
            self._run_git("commit", "-m", commit_msg)
            self._run_git("push", "origin", "main")
            logger.info("Published report for %s", date_str)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Git publish failed: %s", e)
            return False

    def init_repo(self) -> bool:
        """Initialize git repo if not already initialized."""
        git_dir = self.repo_dir / ".git"
        if git_dir.exists():
            return True
        try:
            self._run_git("init")
            return True
        except subprocess.CalledProcessError:
            return False

    def has_changes(self) -> bool:
        """Check if there are uncommitted changes in reports/docs."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "reports/", "docs/"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def _run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=str(self.repo_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
