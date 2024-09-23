import argparse
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from gitmirror.exceptions import MirrorError
from gitmirror.mirror import (
    create_pull_request,
    mirror,
    parse_arguments,
    run_mirror_process,
    setup_components,
)


@pytest.fixture
def mock_config():
    config = Mock()
    config.get.side_effect = lambda section, key, fallback=None: {
        ("Cache", "cache_file"): "file_cache.json",
        ("Repository", "git_server"): "github",
        ("Repository", "repository"): "user/repo",
        ("PullRequest", "create"): "true",
        ("PullRequest", "title"): "Test PR",
        ("PullRequest", "description"): "Test Description",
        ("Git", "new_branch"): "feature-branch",
        ("Git", "base_branch"): "main",
        ("PullRequest", "close_on_merge"): "true",
        ("PullRequest", "rebase"): "true",
    }.get((section, key), fallback)
    return config


@pytest.fixture
def mock_file_tree_handler():
    return Mock()


@pytest.fixture
def mock_git_provider():
    return Mock()


def test_parse_arguments():
    with patch("sys.argv", ["mirror.py", "-c", "custom_config.ini"]):
        args = parse_arguments()
        assert args.config == "custom_config.ini"


@patch("gitmirror.mirror.FileCache")
@patch("gitmirror.mirror.GitOperations")
@patch("gitmirror.mirror.FileTreeHandler")
@patch("gitmirror.mirror.GitProviderFactory.get_provider")
def test_setup_components(
    mock_get_provider,
    mock_file_tree_handler,
    mock_git_ops,
    mock_file_cache,
    mock_config,
):
    mock_get_provider.return_value = Mock()
    file_tree_handler, git_provider = setup_components(mock_config)

    assert isinstance(file_tree_handler, Mock)
    assert isinstance(git_provider, Mock)
    mock_file_cache.assert_called_once_with("file_cache.json")
    mock_get_provider.assert_called_once_with("github", "user/repo")


def test_create_pull_request(mock_config, mock_git_provider):
    create_pull_request(mock_config, mock_git_provider)

    mock_git_provider.create_pull_request.assert_called_once()
    call_args = mock_git_provider.create_pull_request.call_args[0][0]
    assert call_args.title == "Test PR"
    assert call_args.description == "Test Description"
    assert call_args.head_branch == "feature-branch"
    assert call_args.base_branch == "main"
    assert call_args.close_on_merge == True
    assert call_args.rebase == True


@patch("gitmirror.mirror.MirrorService")
def test_run_mirror_process(
    mock_mirror_service, mock_config, mock_file_tree_handler, mock_git_provider
):
    mock_mirror_service_instance = Mock()
    mock_mirror_service.return_value = mock_mirror_service_instance
    mock_mirror_service_instance.mirror_file_tree.return_value = {"status": "success"}

    result = run_mirror_process(mock_config, mock_file_tree_handler, mock_git_provider)

    mock_mirror_service.assert_called_once_with(
        mock_config, mock_file_tree_handler, mock_git_provider
    )
    mock_mirror_service_instance.mirror_file_tree.assert_called_once()
    assert "pull_request" in result


@patch("gitmirror.mirror.IniConfigProvider")
@patch("gitmirror.mirror.DictConfigProvider")
@patch("gitmirror.mirror.setup_components")
@patch("gitmirror.mirror.MirrorService")
def test_mirror_with_config_file(
    mock_mirror_service, mock_setup, mock_dict_config, mock_ini_config
):
    mock_config = Mock()
    mock_ini_config.return_value = mock_config
    mock_setup.return_value = (Mock(), Mock(), Mock(), [])
    mock_mirror_service_instance = Mock()
    mock_mirror_service.return_value = mock_mirror_service_instance
    mock_mirror_service_instance.mirror_file_tree.return_value = {"status": "success"}

    mock_config.get.side_effect = (
        lambda section, key, fallback=None: "/path/to/base"
        if key == "base_path"
        else fallback
    )

    result = mirror(config_path="config.ini")

    assert result == {"status": "success"}
    mock_ini_config.assert_called_once_with("config.ini")
    mock_setup.assert_called_once_with(mock_config)
    mock_mirror_service.assert_called_once()
    mock_mirror_service_instance.mirror_file_tree.assert_called_once()


@patch("gitmirror.mirror.DictConfigProvider")
@patch("gitmirror.mirror.setup_components")
@patch("gitmirror.mirror.MirrorService")
def test_mirror_with_config_params(mock_mirror_service, mock_setup, mock_dict_config):
    mock_config = Mock()
    mock_dict_config.return_value = mock_config
    mock_setup.return_value = (Mock(), Mock(), Mock(), [])
    mock_mirror_service_instance = Mock()
    mock_mirror_service.return_value = mock_mirror_service_instance
    mock_mirror_service_instance.mirror_file_tree.return_value = {"status": "success"}

    mock_config.get.side_effect = (
        lambda section, key, fallback=None: "/path/to/base"
        if key == "base_path"
        else fallback
    )

    result = mirror(Repository__git_server="github", Repository__repository="user/repo")

    assert result == {"status": "success"}
    mock_dict_config.assert_called_once()
    mock_setup.assert_called_once_with(mock_config)
    mock_mirror_service.assert_called_once()
    mock_mirror_service_instance.mirror_file_tree.assert_called_once()


@patch("gitmirror.mirror.IniConfigProvider")
@patch("gitmirror.mirror.setup_components")
def test_mirror_with_error(mock_setup, mock_ini_config):
    mock_setup.side_effect = ValueError(
        "not enough values to unpack (expected 4, got 0)"
    )

    with pytest.raises(MirrorError) as exc_info:
        mirror(config_path="config.ini")

    assert "An error occurred during the mirroring process:" in str(exc_info.value)
    assert isinstance(exc_info.value.original_error, ValueError)
    assert "not enough values to unpack (expected 4, got 0)" in str(
        exc_info.value.original_error
    )


if __name__ == "__main__":
    pytest.main()
