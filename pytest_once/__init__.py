"""pytest-once: xdist-safe 'run once' fixture decorator for pytest."""

from importlib.metadata import version

from pytest_once.decorator import once_fixture

__version__ = version("pytest-once")

__all__ = ["once_fixture"]
