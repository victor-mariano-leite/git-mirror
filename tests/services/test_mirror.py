from unittest.mock import Mock, patch

import pytest

from gitmirror.exceptions import MirrorError
from gitmirror.operations.git import GitOperations
from gitmirror.services.mirror import MirrorService


@pytest.fixture
def mock_config():
    config = Mock()
    config.get.side_effect = lambda section, key, fallback=None: {
        ("Paths", "base_path"): "/path/to/source",
        ("Git", "commit_msg"): "Test commit",
        ("Git", "base_branch"): "main",
        ("Git", "new_branch"): "feature-branch",
        ("Filters", "ignore_patterns"): "*.log,*.tmp",
    }.get((section, key), fallback)
    return config


@pytest.fixture
def mock_file_tree_handler():
    return Mock()


@pytest.fixture
def mock_git_provider():
    provider = Mock()
    provider.repository = "https://github.com/user/repo.git"
    return provider


@pytest.fixture
def mock_git_ops():
    mock = Mock(spec=GitOperations)
    mock.clone_repository = Mock()
    mock.push_changes = Mock()
    mock.create_rollback_commit = Mock()
    return mock


@pytest.fixture
def mirror_service(
    mock_config, mock_file_tree_handler, mock_git_provider, mock_git_ops
):
    return MirrorService(
        mock_config, mock_file_tree_handler, mock_git_provider, mock_git_ops
    )


def test_mirror_file_tree_success_with_changes(
    mirror_service, mock_git_ops, mock_file_tree_handler
):
    # Setup
    changes = {"file1.txt": "modified", "file2.txt": "added"}
    mock_file_tree_handler.detect_file_changes.return_value = changes
    mock_git_ops.push_changes.return_value = "abcdef1234567890"

    # Execute
    result = mirror_service.mirror_file_tree()

    # Assert
    assert result == {
        "status": "success",
        "changes": changes,
        "commit_hash": "abcdef1234567890",
    }
    mock_git_ops.clone_repository.assert_called_once()
    mock_file_tree_handler.detect_file_changes.assert_called_once()
    mock_file_tree_handler.copy_file_tree.assert_called_once()
    mock_git_ops.push_changes.assert_called_once()


def test_mirror_file_tree_success_no_changes(
    mirror_service, mock_git_ops, mock_file_tree_handler
):
    # Setup
    mock_file_tree_handler.detect_file_changes.return_value = {}

    # Execute
    result = mirror_service.mirror_file_tree()

    # Assert
    assert result == {
        "status": "success",
        "changes": {},
        "message": "No changes detected",
    }
    mock_git_ops.clone_repository.assert_called_once()
    mock_file_tree_handler.detect_file_changes.assert_called_once()
    mock_file_tree_handler.copy_file_tree.assert_called_once()
    mock_git_ops.push_changes.assert_not_called()


def test_mirror_file_tree_error(mirror_service, mock_git_ops, mock_file_tree_handler):
    # Setup
    mock_git_ops.clone_repository.side_effect = Exception("Git error")

    # Execute
    result = mirror_service.mirror_file_tree()

    # Assert
    assert result == {"status": "error", "message": "Git error"}
    mock_git_ops.clone_repository.assert_called_once()
    mock_git_ops.create_rollback_commit.assert_called_once()
    mock_git_ops.push_changes.assert_called_once()


@patch("gitmirror.services.mirror.tempfile.TemporaryDirectory")
def test_mirror_file_tree_temp_directory_usage(
    mock_temp_dir, mirror_service, mock_git_ops
):
    # Setup
    mock_temp_dir.return_value.__enter__.return_value = "/tmp"

    # Execute
    mirror_service.mirror_file_tree()

    # Assert
    mock_temp_dir.assert_called_once()
    mock_git_ops.clone_repository.assert_called_once_with(
        "https://github.com/user/repo.git", "main", "/tmp/repo", []
    )


if __name__ == "__main__":
    pytest.main()
