"""
Git Mirror - Sync file trees with Git repositories.

This module serves as the entry point for the Git Mirror application.
It orchestrates the setup of components and execution of the mirroring process.

The application can also create a pull request if configured to do so.
"""

import argparse
import json
import sys
from typing import Any, Dict, Optional

from gitmirror.config import DictConfigProvider, IniConfigProvider
from gitmirror.exceptions import MirrorError
from gitmirror.operations.file import FileCache, FileTreeHandler
from gitmirror.operations.git import GitOperations
from gitmirror.providers import GitProviderFactory, PullRequestInfo
from gitmirror.services.mirror import MirrorService


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Git Mirror - Sync file trees with Git repositories"
    )
    parser.add_argument(
        "-c", "--config", default="config.ini", help="Path to the configuration file"
    )
    return parser.parse_args()


def setup_components(config: Any) -> tuple:
    """
    Set up and initialize all necessary components.

    Parameters
    ----------
    config : Any
        Configuration provider (either IniConfigProvider or DictConfigProvider).

    Returns
    -------
    tuple
        A tuple containing the initialized components:
        (file_tree_handler, git_provider)
    """
    file_cache = FileCache(
        config.get("Cache", "cache_file", fallback="file_cache.json")
    )
    git_ops = GitOperations()
    file_tree_handler = FileTreeHandler(file_cache, git_ops)

    git_provider = GitProviderFactory.get_provider(
        config.get("Repository", "git_server"), config.get("Repository", "repository")
    )

    return file_tree_handler, git_provider


def create_pull_request(config: Any, git_provider: Any) -> Dict[str, Any]:
    """
    Create a pull request based on the configuration.

    Parameters
    ----------
    config : Any
        The configuration provider.
    git_provider : Any
        The Git provider instance.

    Returns
    -------
    Dict[str, Any]
        The result of the pull request creation.
    """
    pr_info = PullRequestInfo(
        title=config.get("PullRequest", "title"),
        description=config.get("PullRequest", "description"),
        head_branch=config.get("Git", "new_branch"),
        base_branch=config.get("Git", "base_branch"),
        close_on_merge=config.get(
            "PullRequest", "close_on_merge", fallback="true"
        ).lower()
        == "true",
        rebase=config.get("PullRequest", "rebase", fallback="true").lower() == "true",
    )
    return git_provider.create_pull_request(pr_info)


def run_mirror_process(
    config: Any, file_tree_handler: FileTreeHandler, git_provider: Any
) -> Dict[str, Any]:
    """
    Run the mirror process and optionally create a pull request.

    Parameters
    ----------
    config : Any
        The configuration provider.
    file_tree_handler : FileTreeHandler
        The file tree handler instance.
    git_provider : Any
        The Git provider instance.

    Returns
    -------
    Dict[str, Any]
        The result of the mirroring process and pull request creation (if applicable).
    """
    mirror_service = MirrorService(config, file_tree_handler, git_provider)
    result = mirror_service.mirror_file_tree()

    if (
        result["status"] == "success"
        and config.get("PullRequest", "create", fallback="false").lower() == "true"
    ):
        pr_result = create_pull_request(config, git_provider)
        result["pull_request"] = pr_result

    return result


def mirror(config_path: Optional[str] = None, **config_params) -> Dict[str, Any]:
    """
    Main function to run the Git Mirror application.

    This function orchestrates the entire process:
    1. Sets up the configuration and components
    2. Runs the mirroring process
    3. Optionally creates a pull request

    Parameters
    ----------
    config_path : str, optional
        Path to the configuration file. If not provided, uses the default "config.ini".
    **config_params : dict
        Configuration parameters as keyword arguments. These will override file-based config if both are provided.

    Returns
    -------
    Dict[str, Any]
        The result of the mirroring process and pull request creation (if applicable).

    Raises
    ------
    Exception
        If an error occurs during the process.
    """
    try:
        if config_path:
            config = IniConfigProvider(config_path)
            for key, value in config_params.items():
                section, option = key.split(".")
                config.set(section, option, str(value))
        elif config_params:
            config = DictConfigProvider(config_params)
        else:
            config = IniConfigProvider("config.ini")

        file_tree_handler, git_provider, git_ops, folders_to_include = setup_components(
            config
        )
        mirror_service = MirrorService(
            config, file_tree_handler, git_provider, git_ops, folders_to_include
        )
        result = mirror_service.mirror_file_tree()
        return result
    except Exception as e:
        error_message = f"An error occurred during the mirroring process: {str(e)}"
        print(error_message, file=sys.stderr)
        raise MirrorError(error_message, original_error=e)


if __name__ == "__main__":
    args = parse_arguments()
    try:
        result = mirror(args.config)
        print(json.dumps(result, indent=2))
    except MirrorError as e:
        print(f"Mirror Error: {e.message}", file=sys.stderr)
        sys.exit(1)
