import hashlib
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gitmirror.operations.git import GitOperations


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess.run and subprocess.check_output."""
    with patch("gitmirror.operations.git.subprocess.run") as mock_run, patch(
        "gitmirror.operations.git.subprocess.check_output"
    ) as mock_check_output:
        yield mock_run, mock_check_output


def test_clone_repository(mock_subprocess, temp_dir):
    mock_run, _ = mock_subprocess
    git_url = "https://github.com/user/repo.git"
    base_branch = "main"
    temp_repo_path = str(temp_dir / "repo")
    folders_to_include = ["folder1", "folder2"]

    GitOperations.clone_repository(
        git_url, base_branch, temp_repo_path, folders_to_include
    )

    assert mock_run.call_count == 4
    mock_run.assert_any_call(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--sparse",
            git_url,
            "-b",
            base_branch,
            temp_repo_path,
        ],
        check=True,
    )
    mock_run.assert_any_call(
        ["git", "sparse-checkout", "init", "--cone"], cwd=temp_repo_path, check=True
    )
    mock_run.assert_any_call(
        ["git", "sparse-checkout", "set"] + folders_to_include,
        cwd=temp_repo_path,
        check=True,
    )


@pytest.mark.parametrize("new_branch", [None, "feature-branch"])
def test_push_changes(mock_subprocess, temp_dir, new_branch):
    mock_run, mock_check_output = mock_subprocess
    temp_repo_path = str(temp_dir / "repo")
    commit_msg = "Test commit"
    mock_check_output.return_value = "abcdef1234567890"

    result = GitOperations.push_changes(temp_repo_path, commit_msg, new_branch)

    assert mock_run.call_count == 3 if new_branch is None else 4
    mock_run.assert_any_call(["git", "add", "."], cwd=temp_repo_path, check=True)
    mock_run.assert_any_call(
        ["git", "commit", "-m", commit_msg], cwd=temp_repo_path, check=True
    )
    if new_branch:
        mock_run.assert_any_call(
            ["git", "checkout", "-b", new_branch], cwd=temp_repo_path, check=True
        )
    mock_run.assert_any_call(
        ["git", "push", "origin", new_branch or "HEAD"], cwd=temp_repo_path, check=True
    )
    mock_check_output.assert_called_once_with(
        ["git", "rev-parse", "HEAD"], cwd=temp_repo_path, universal_newlines=True
    )
    assert result == "abcdef1234567890"


def test_get_file_hash(temp_dir):
    test_file = temp_dir / "test_file.txt"
    test_content = b"Hello, World!"
    test_file.write_bytes(test_content)

    result = GitOperations.get_file_hash(str(test_file))

    expected_hash = hashlib.md5(test_content).hexdigest()
    assert result == expected_hash


def test_copy_file(temp_dir):
    src_file = temp_dir / "source.txt"
    dest_file = temp_dir / "destination.txt"
    src_content = "Test content"
    src_file.write_text(src_content)

    GitOperations.copy_file(src_file, dest_file)

    assert dest_file.exists()
    assert dest_file.read_text() == src_content


def test_create_rollback_commit(mock_subprocess, temp_dir):
    mock_run, _ = mock_subprocess
    repo_path = temp_dir / "repo"
    repo_path.mkdir()
    changes = {
        "added.txt": "added",
        "modified.txt": "modified",
        "deleted.txt": "deleted",
    }

    # Create mock files
    (repo_path / "added.txt").touch()
    (repo_path / "modified.txt").write_text("modified content")
    (repo_path / "modified.txt.bak").write_text("original content")
    (repo_path / "deleted.txt.bak").write_text("deleted content")

    GitOperations.create_rollback_commit(repo_path, changes)

    assert not (repo_path / "added.txt").exists()
    assert (repo_path / "modified.txt").read_text() == "original content"
    assert (repo_path / "deleted.txt").read_text() == "deleted content"

    assert mock_run.call_count == 2
    mock_run.assert_any_call(["git", "add", "."], cwd=repo_path, check=True)
    mock_run.assert_any_call(
        ["git", "commit", "-m", "Rollback: Undoing last mirror operation"],
        cwd=repo_path,
        check=True,
    )


if __name__ == "__main__":
    pytest.main()
