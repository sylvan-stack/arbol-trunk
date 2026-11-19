"""Placeholder phases around Steady's single Driver run."""

from .end import End


def intake() -> None:
    """Pass the accepted Exchange through without adding context or labels."""


def planning() -> None:
    """Continue directly to Execution."""


def finalization(outcome: End) -> End:
    """Pass the outcome to the shared Exchange end handling."""
    return outcome
