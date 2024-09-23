"""
Custom exceptions for the GitMirror library.
"""


class GitMirrorError(Exception):
    """Base exception class for GitMirror errors."""

    pass


class MirrorError(GitMirrorError):
    """Exception raised for errors in the mirroring process."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
