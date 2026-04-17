"""Custom exception hierarchy for vnvspec.

All user-facing errors inherit from :class:`VnvspecError` and carry a
``help_url`` attribute pointing to the relevant documentation page.
"""

from __future__ import annotations


class VnvspecError(Exception):
    """Base exception for all vnvspec errors.

    Example:
        >>> raise VnvspecError("something went wrong")
        Traceback (most recent call last):
            ...
        vnvspec.core.errors.VnvspecError: something went wrong
    """

    help_url: str = "https://ai-vnv.kfupm.io/vnvspec/concepts/"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        super().__init__(message)
        if help_url is not None:
            self.help_url = help_url


class SpecError(VnvspecError):
    """Raised when a Spec is invalid or inconsistent.

    Example:
        >>> raise SpecError("duplicate requirement id")
        Traceback (most recent call last):
            ...
        vnvspec.core.errors.SpecError: duplicate requirement id
    """

    help_url: str = "https://ai-vnv.kfupm.io/vnvspec/concepts/spec/"


class RequirementError(VnvspecError):
    """Raised when a Requirement is invalid.

    Example:
        >>> raise RequirementError("empty statement")
        Traceback (most recent call last):
            ...
        vnvspec.core.errors.RequirementError: empty statement
    """

    help_url: str = "https://ai-vnv.kfupm.io/vnvspec/concepts/requirement/"


class ContractError(VnvspecError):
    """Raised when an IOContract is invalid or a validation fails.

    Example:
        >>> raise ContractError("invariant violated")
        Traceback (most recent call last):
            ...
        vnvspec.core.errors.ContractError: invariant violated
    """

    help_url: str = "https://ai-vnv.kfupm.io/vnvspec/concepts/io-contract/"


class AssessmentError(VnvspecError):
    """Raised when an assessment operation fails.

    Example:
        >>> raise AssessmentError("model adapter not compatible")
        Traceback (most recent call last):
            ...
        vnvspec.core.errors.AssessmentError: model adapter not compatible
    """

    help_url: str = "https://ai-vnv.kfupm.io/vnvspec/concepts/assessment/"
