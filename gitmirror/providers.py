"""
Git provider module for Git Mirror.

This module provides classes for interacting with various Git hosting services,
including GitHub, GitLab, Bitbucket, AWS CodeCommit, and Azure DevOps.
It also includes a factory class for creating provider instances based on
the specified Git server.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class PullRequestInfo:
    """
    Data class to hold pull request information.

    Attributes
    ----------
    title : str
        The title of the pull request.
    description : str
        The description of the pull request.
    head_branch : str
        The name of the branch containing the changes.
    base_branch : str
        The name of the branch to merge into.
    close_on_merge : bool, optional
        Whether to close the source branch after merging (default is True).
    rebase : bool, optional
        Whether to use rebase strategy for merging (default is True).
    """

    title: str
    description: str
    head_branch: str
    base_branch: str
    close_on_merge: bool = True
    rebase: bool = True


class BaseProvider(ABC):
    """
    Abstract base class for Git providers.

    This class defines the interface for Git providers, allowing
    for different Git hosting services to be supported.
    """

    def __init__(self, repository: str):
        """
        Initialize the BaseProvider.

        Parameters
        ----------
        repository : str
            The name of the repository.
        """
        self.repository = repository

    @abstractmethod
    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.
        """
        pass


class GitHubProvider(BaseProvider):
    """
    GitHub provider implementation.

    This class implements the BaseProvider interface for GitHub repositories.
    """

    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request on GitHub.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.

        Raises
        ------
        requests.exceptions.RequestException
            If there's an error in the API request.
        """
        api_url = f"https://api.github.com/repos/{self.repository}/pulls"
        payload = {
            "title": pr_info.title,
            "head": pr_info.head_branch,
            "base": pr_info.base_branch,
            "body": pr_info.description,
            "maintainer_can_modify": True,
            "draft": False,
        }
        headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class BitbucketProvider(BaseProvider):
    """
    Bitbucket provider implementation.

    This class implements the BaseProvider interface for Bitbucket repositories.
    """

    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request on Bitbucket.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.

        Raises
        ------
        requests.exceptions.RequestException
            If there's an error in the API request.
        """
        workspace, repo_slug = self.repository.split("/")
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"
        payload = {
            "title": pr_info.title,
            "source": {"branch": {"name": pr_info.head_branch}},
            "destination": {"branch": {"name": pr_info.base_branch}},
            "description": pr_info.description,
            "close_source_branch": pr_info.close_on_merge,
            "merge_strategy": "squash" if pr_info.rebase else "merge_commit",
        }
        headers = {"Authorization": f"Bearer {os.getenv('BITBUCKET_TOKEN')}"}
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class GitLabProvider(BaseProvider):
    """
    GitLab provider implementation.

    This class implements the BaseProvider interface for GitLab repositories.
    """

    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request on GitLab.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.

        Raises
        ------
        requests.exceptions.RequestException
            If there's an error in the API request.
        """
        api_url = f"https://gitlab.com/api/v4/projects/{self.repository.replace('/', '%2F')}/merge_requests"
        payload = {
            "title": pr_info.title,
            "source_branch": pr_info.head_branch,
            "target_branch": pr_info.base_branch,
            "description": pr_info.description,
            "remove_source_branch": pr_info.close_on_merge,
            "squash": pr_info.rebase,
        }
        headers = {"Authorization": f"Bearer {os.getenv('GITLAB_TOKEN')}"}
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class AWSCodeCommitProvider(BaseProvider):
    """
    AWS CodeCommit provider implementation.

    This class implements the BaseProvider interface for AWS CodeCommit repositories.
    """

    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request on AWS CodeCommit.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.

        Raises
        ------
        requests.exceptions.RequestException
            If there's an error in the API request.
        """
        api_url = f"https://git-codecommit.us-east-1.amazonaws.com/v1/repos/{self.repository}/pull-requests"
        payload = {
            "title": pr_info.title,
            "sourceReference": pr_info.head_branch,
            "destinationReference": pr_info.base_branch,
            "description": pr_info.description,
            "closeSourceBranch": pr_info.close_on_merge,
            "mergeStrategy": "FAST_FORWARD_MERGE"
            if pr_info.rebase
            else "THREE_WAY_MERGE",
        }
        headers = {
            "Authorization": f"Bearer {os.getenv('AWS_ACCESS_KEY_ID')}:{os.getenv('AWS_SECRET_ACCESS_KEY')}"
        }
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class AzureDevOpsProvider(BaseProvider):
    """
    Azure DevOps provider implementation.

    This class implements the BaseProvider interface for Azure DevOps repositories.
    """

    def create_pull_request(self, pr_info: PullRequestInfo) -> Dict[str, Any]:
        """
        Create a pull request on Azure DevOps.

        Parameters
        ----------
        pr_info : PullRequestInfo
            Information about the pull request.

        Returns
        -------
        Dict[str, Any]
            Details of the created pull request.

        Raises
        ------
        requests.exceptions.RequestException
            If there's an error in the API request.
        """
        organization, project, repo_slug = self.repository.split("/")
        api_url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_slug}/pullrequests?api-version=6.0"
        payload = {
            "title": pr_info.title,
            "sourceRefName": f"refs/heads/{pr_info.head_branch}",
            "targetRefName": f"refs/heads/{pr_info.base_branch}",
            "description": pr_info.description,
            "completionOptions": {
                "deleteSourceBranch": pr_info.close_on_merge,
                "squashMerge": pr_info.rebase,
            },
        }
        headers = {"Authorization": f"Bearer {os.getenv('AZURE_DEVOPS_TOKEN')}"}
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class GitProviderFactory:
    """
    Factory class for creating Git provider instances.
    """

    @staticmethod
    def get_provider(git_server: str, repository: str) -> BaseProvider:
        """
        Get the appropriate Git provider based on the server type.

        Parameters
        ----------
        git_server : str
            The type of Git server.
        repository : str
            The repository name.

        Returns
        -------
        BaseProvider
            An instance of a Git provider.

        Raises
        ------
        ValueError
            If the git_server type is unsupported.
        """
        providers = {
            "github": GitHubProvider,
            "bitbucket": BitbucketProvider,
            "gitlab": GitLabProvider,
            "aws": AWSCodeCommitProvider,
            "azure": AzureDevOpsProvider,
        }
        provider_class = providers.get(git_server.lower())
        if not provider_class:
            raise ValueError(f"Unsupported git_server: {git_server}")
        return provider_class(repository)
