"""Helpers for reporting optional dependency availability."""

from __future__ import annotations

import importlib


class OptionalDependencyError(ImportError):
    """Raised when an optional dependency is required but unavailable."""


def import_optional_dependency(
    import_name: str,
    *,
    package_name: str | None = None,
    extra_name: str,
    used_for: str,
):
    """Import an optional dependency or raise a clear installation hint."""

    package_label = package_name or import_name
    try:
        return importlib.import_module(import_name)
    except Exception as exc:  # pragma: no cover - exercised through callers
        raise OptionalDependencyError(
            f"{package_label} is required for {used_for}. "
            f"Install the optional dependency group with `pip install .[{extra_name}]`."
        ) from exc
