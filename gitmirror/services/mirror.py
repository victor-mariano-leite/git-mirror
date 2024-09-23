"""
Mirror service module for Git Mirror.

This module provides the main service class for mirroring file trees
to Git repositories. It orchestrates the file operations, Git operations,
and uses the configured Git provider.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List

from gitmirror.config import ConfigProvider
from gitmirror.operations.file import FileTreeHandler
from gitmirror.operations.git import GitOperations
from gitmirror.providers import BaseProvider


class MirrorService:
    """
    Service class that orchestrates the file tree mirroring process.
    """

    def __init__(
        self,
        config: ConfigProvider,
        file_tree_handler: FileTreeHandler,
        git_provider: BaseProvider,
        git_ops: GitOperations = GitOperations,
        folders_to_include: List[str] = None,
    ):
        """
        Initialize the MirrorService.

        Parameters
        ----------
        config : ConfigProvider
            Provider for configuration values.
        file_tree_handler : FileTreeHandler
            Handler for file tree operations.
        git_provider : BaseProvider
            Provider for Git operations.
        """
        self.config = config
        self.file_tree_handler = file_tree_handler
        self.git_provider = git_provider
        self.git_ops = git_ops
        self.folders_to_include = folders_to_include or []

    def mirror_file_tree(self) -> Dict[str, Any]:
        """
        Mirror the file tree from source to destination Git repository.

        This method performs the following steps:
        1. Clone the repository
        2. Detect changes between the source and destination
        3. Copy the file tree, updating only changed files
        4. Commit and push changes if any are detected
        5. Handle errors and perform rollback if necessary

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the operation status and any changes made.
            Possible keys:
            - 'status': 'success' or 'error'
            - 'changes': Dict of file changes (for successful operations)
            - 'commit_hash': Hash of the commit (for successful operations with changes)
            - 'message': Description of the result or error message
        """
        base_path = Path(self.config.get("Paths", "base_path")).resolve()
        commit_msg = self.config.get("Git", "commit_msg")
        base_branch = self.config.get("Git", "base_branch", fallback="main")
        new_branch = self.config.get("Git", "new_branch")
        ignore_patterns = self.config.get(
            "Filters", "ignore_patterns", fallback=""
        ).split(",")
        changes = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo_path = Path(temp_dir) / "repo"
            try:
                self.git_ops.clone_repository(
                    self.git_provider.repository,
                    base_branch,
                    str(temp_repo_path),
                    self.folders_to_include,
                )
                changes = self.file_tree_handler.detect_file_changes(
                    base_path, temp_repo_path
                )
                self.file_tree_handler.copy_file_tree(
                    base_path, temp_repo_path, ignore_patterns
                )

                if changes:
                    commit_hash = self.git_ops.push_changes(
                        str(temp_repo_path), commit_msg, new_branch
                    )
                    return {
                        "status": "success",
                        "changes": changes,
                        "commit_hash": commit_hash,
                    }
                else:
                    return {
                        "status": "success",
                        "changes": {},
                        "message": "No changes detected",
                    }

            except Exception as e:
                self.git_ops.create_rollback_commit(temp_repo_path, changes)
                self.git_ops.push_changes(
                    str(temp_repo_path),
                    "Rollback: Undoing last mirror operation",
                    new_branch,
                )
                return {"status": "error", "message": str(e)}
