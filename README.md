# git-mirror

![GitHub stars](https://img.shields.io/github/stars/victor-mariano-leite/git-mirror?style=social)
![PyPI version](https://img.shields.io/pypi/v/git-mirror.svg)
![Python versions](https://img.shields.io/pypi/pyversions/git-mirror.svg)
![License](https://img.shields.io/github/license/victor-mariano-leite/git-mirror.svg)

git-mirror is a powerful, flexible, and efficient Python library designed to seamlessly synchronize file trees with Git repositories. Whether you're managing documentation, code bases, or any directory structure, git-mirror provides a robust solution for keeping your Git repositories up-to-date with local file systems.

## Features

- 🔄 **Incremental Updates**: Efficiently sync only changed files, saving time and bandwidth.
- 🎛️ **Configurable**: Easy-to-use INI configuration for customizing sync behavior.
- 🔍 **Smart Filtering**: Ignore specific files or patterns to keep your repository clean.
- 💾 **Caching**: Utilize file caching to speed up subsequent syncs.
- 🔍 **Improved Diff Detection**: Accurately identify and sync only modified files.
- ↩️ **Automatic Rollback**: Built-in error handling with automatic rollback to maintain repository consistency.
- 🔀 **Multi-Provider Support**: Works with GitHub, GitLab, Bitbucket, AWS CodeCommit, and Azure DevOps.
- 🤝 **Pull Request Integration**: Automatically create pull requests after syncing changes.
- 📁 **Sparse Checkout**: Selectively sync specific folders to reduce data transfer and improve performance.
- 🔒 **Flexible Authentication**: Support for various authentication methods across different Git providers.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

You can install git-mirror using pip:

```bash
pip install git-file-mirror
```

Ensure you have Python 3.7 or higher installed.

## Quick Start

1. Install git-mirror:
   ```bash
   pip install git-file-mirror
   ```

2. Create a configuration file `config.ini`:
   ```ini
   [Paths]
   base_path = /path/to/source/directory

   [Git]
   commit_msg = Update mirrored files
   base_branch = main
   new_branch = update-branch

   [Repository]
   git_server = github
   repository = username/repo-name
   folders_to_include = folder1,folder2/subfolder,folder3

   [Filters]
   ignore_patterns = *.tmp,*.log,**/temp/*

   [PullRequest]
   create = true
   title = Update mirrored files
   description = This PR updates the mirrored files from the source directory.
   close_on_merge = true
   rebase = true
   ```

3. Run git-mirror:
   ```python
   from gitmirror.mirror import mirror

   result = mirror(config_path="config.ini")
   print(result)
   ```

## Configuration

git-mirror uses an INI configuration file for easy customization. The `config.ini` file supports the following sections:

- `[Paths]`: Specify the source directory to mirror.
- `[Git]`: Configure Git-related settings like commit messages and branch names.
- `[Repository]`: Set the Git provider and repository details.
- `[Filters]`: Define patterns for files to ignore during mirroring.
- `[PullRequest]`: Configure automatic pull request creation.

For a full list of configuration options, please refer to our [documentation](https://git-mirror.readthedocs.io).

## Usage

### Basic Usage

```python
from gitmirror.mirror import mirror

result = mirror(config_path="config.ini")
print(result)
```

### Using Configuration Parameters

You can also provide configuration parameters directly:

```python
from gitmirror.mirror import mirror

result = mirror(
    Paths__base_path="/path/to/source",
    Repository__git_server="github",
    Repository__repository="username/repo-name",
    Repository__folders_to_include="folder1,folder2/subfolder"
)
print(result)
```

## Advanced Usage

### Custom Git Operations

```python
from gitmirror.operations.git import GitOperations

# Clone a repository with sparse checkout
git_url = "https://github.com/username/repo.git"
base_branch = "main"
temp_repo_path = "/path/to/temp/repo"
folders_to_include = ["folder1", "folder2"]

GitOperations.clone_repository(git_url, base_branch, temp_repo_path, folders_to_include)

# Push changes
commit_msg = "Update mirrored files"
new_branch = "update-branch"
commit_hash = GitOperations.push_changes(temp_repo_path, commit_msg, new_branch)
print(f"Changes pushed. Commit hash: {commit_hash}")
```

For more detailed usage instructions and API documentation, please refer to our [documentation](https://git-mirror.readthedocs.io).

## Contributing

We welcome contributions to git-mirror! Here's how you can help:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Submit a pull request.

Please make sure to update tests as appropriate and adhere to the [code of conduct](CODE_OF_CONDUCT.md).

## License

git-mirror is released under the MIT License. See the [LICENSE](LICENSE) file for details.

---

git-mirror is maintained by [victor-mariano-leite]. If you encounter any issues or have questions, please [open an issue](https://github.com/victor-mariano-leite/git-mirror/issues) on GitHub.
