"""Utilities for normalizing paired-end read identifiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReadIdParts:
    """Parsed view of a repository read identifier."""

    raw: str
    token: str
    base_id: str
    mate: str | None


def normalize_read_token(value: str) -> str:
    """Normalize a FASTQ header or TSV read identifier to its first token."""

    token = str(value).strip()
    if not token:
        return ""
    token = token.split()[0]
    if token.startswith("@"):
        token = token[1:]
    return token


def split_read_id(value: str) -> ReadIdParts:
    """Split a read identifier into base pair ID and optional mate suffix."""

    token = normalize_read_token(value)
    if token.endswith("/1"):
        return ReadIdParts(raw=str(value), token=token, base_id=token[:-2], mate="1")
    if token.endswith("/2"):
        return ReadIdParts(raw=str(value), token=token, base_id=token[:-2], mate="2")
    return ReadIdParts(raw=str(value), token=token, base_id=token, mate=None)


def normalize_base_read_id(value: str) -> str:
    """Return the pair-level read ID shared by both mates."""

    return split_read_id(value).base_id


def mate_specific_read_id(value: str, mate: str) -> str:
    """Return a canonical mate-specific ID using `/1` or `/2`."""

    if mate not in {"1", "2"}:
        raise ValueError(f"mate must be '1' or '2', got {mate!r}")
    return f"{normalize_base_read_id(value)}/{mate}"


def infer_mate_from_header(value: str) -> str | None:
    """Return the mate suffix if it is explicit in the identifier."""

    return split_read_id(value).mate


def unique_base_ids(values: Iterable[str]) -> list[str]:
    """Return base IDs in first-seen order."""

    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        base_id = normalize_base_read_id(value)
        if base_id and base_id not in seen:
            seen.add(base_id)
            ordered.append(base_id)
    return ordered

