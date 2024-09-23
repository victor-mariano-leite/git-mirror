import os
from unittest.mock import Mock, patch

import pytest

from gitmirror.providers import (
    AWSCodeCommitProvider,
    AzureDevOpsProvider,
    BaseProvider,
    BitbucketProvider,
    GitHubProvider,
    GitLabProvider,
    GitProviderFactory,
    PullRequestInfo,
)


@pytest.fixture
def sample_pr_info():
    return PullRequestInfo(
        title="Test PR",
        description="This is a test PR",
        head_branch="feature-branch",
        base_branch="main",
        close_on_merge=True,
        rebase=True,
    )


@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {
        "id": 1,
        "number": 101,
        "html_url": "https://example.com/pr/101",
    }
    return mock


class TestPullRequestInfo:
    def test_pull_request_info_creation(self):
        pr_info = PullRequestInfo(
            title="Test PR",
            description="This is a test PR",
            head_branch="feature-branch",
            base_branch="main",
        )
        assert pr_info.title == "Test PR"
        assert pr_info.description == "This is a test PR"
        assert pr_info.head_branch == "feature-branch"
        assert pr_info.base_branch == "main"
        assert pr_info.close_on_merge == True
        assert pr_info.rebase == True


class TestBaseProvider:
    def test_base_provider_initialization(self):
        class ConcreteProvider(BaseProvider):
            def create_pull_request(self, pr_info):
                """
                Mocked method for creating a pull request.
                """
                pass

        provider = ConcreteProvider("test/repo")
        assert provider.repository == "test/repo"

    def test_base_provider_abstract_method(self):
        with pytest.raises(TypeError):
            BaseProvider("test/repo")


class TestGitHubProvider:
    @patch("gitmirror.providers.requests.post")
    def test_create_pull_request(self, mock_post, sample_pr_info, mock_response):
        mock_post.return_value = mock_response
        provider = GitHubProvider("test/repo")
        result = provider.create_pull_request(sample_pr_info)
        assert result == mock_response.json()
        mock_post.assert_called_once()


class TestBitbucketProvider:
    @patch("gitmirror.providers.requests.post")
    def test_create_pull_request(self, mock_post, sample_pr_info, mock_response):
        mock_post.return_value = mock_response
        provider = BitbucketProvider("workspace/repo")
        result = provider.create_pull_request(sample_pr_info)
        assert result == mock_response.json()
        mock_post.assert_called_once()


class TestGitLabProvider:
    @patch("gitmirror.providers.requests.post")
    def test_create_pull_request(self, mock_post, sample_pr_info, mock_response):
        mock_post.return_value = mock_response
        provider = GitLabProvider("group/project")
        result = provider.create_pull_request(sample_pr_info)
        assert result == mock_response.json()
        mock_post.assert_called_once()


class TestAWSCodeCommitProvider:
    @patch("gitmirror.providers.requests.post")
    def test_create_pull_request(self, mock_post, sample_pr_info, mock_response):
        mock_post.return_value = mock_response
        provider = AWSCodeCommitProvider("test-repo")
        result = provider.create_pull_request(sample_pr_info)
        assert result == mock_response.json()
        mock_post.assert_called_once()


class TestAzureDevOpsProvider:
    @patch("gitmirror.providers.requests.post")
    def test_create_pull_request(self, mock_post, sample_pr_info, mock_response):
        mock_post.return_value = mock_response
        provider = AzureDevOpsProvider("org/project/repo")
        result = provider.create_pull_request(sample_pr_info)
        assert result == mock_response.json()
        mock_post.assert_called_once()


class TestGitProviderFactory:
    @pytest.mark.parametrize(
        "git_server,expected_provider",
        [
            ("github", GitHubProvider),
            ("bitbucket", BitbucketProvider),
            ("gitlab", GitLabProvider),
            ("aws", AWSCodeCommitProvider),
            ("azure", AzureDevOpsProvider),
        ],
    )
    def test_get_provider(self, git_server, expected_provider):
        provider = GitProviderFactory.get_provider(git_server, "test/repo")
        assert isinstance(provider, expected_provider)

    def test_get_provider_unsupported(self):
        with pytest.raises(ValueError):
            GitProviderFactory.get_provider("unsupported", "test/repo")


@pytest.mark.parametrize(
    "provider_class,expected_token_env",
    [
        (GitHubProvider, "GITHUB_TOKEN"),
        (BitbucketProvider, "BITBUCKET_TOKEN"),
        (GitLabProvider, "GITLAB_TOKEN"),
        (AzureDevOpsProvider, "AZURE_DEVOPS_TOKEN"),
    ],
)
def test_provider_uses_correct_token(
    provider_class, expected_token_env, sample_pr_info
):
    with patch("gitmirror.providers.requests.post") as mock_post, patch.dict(
        os.environ, {expected_token_env: "test_token"}
    ):
        provider = provider_class(
            "test/project/repo"
            if provider_class == AzureDevOpsProvider
            else "test/repo"
        )
        provider.create_pull_request(sample_pr_info)
        called_headers = mock_post.call_args[1]["headers"]
        assert called_headers["Authorization"] == "Bearer test_token"


def test_aws_provider_uses_correct_credentials(sample_pr_info):
    with patch("gitmirror.providers.requests.post") as mock_post, patch.dict(
        os.environ,
        {"AWS_ACCESS_KEY_ID": "test_key", "AWS_SECRET_ACCESS_KEY": "test_secret"},
    ):
        provider = AWSCodeCommitProvider("test-repo")
        provider.create_pull_request(sample_pr_info)
        called_headers = mock_post.call_args[1]["headers"]
        assert called_headers["Authorization"] == "Bearer test_key:test_secret"


if __name__ == "__main__":
    pytest.main()
