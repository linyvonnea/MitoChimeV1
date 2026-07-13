"""FASTQ helpers shared by pair-safe filtering and deep-learning preprocessing."""

from __future__ import annotations

import gzip
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

from .read_ids import normalize_base_read_id, normalize_read_token


class FastqRecord(NamedTuple):
    """Minimal FASTQ record representation."""

    header: str
    sequence: str
    plus: str
    quality: str

    @property
    def token(self) -> str:
        return normalize_read_token(self.header)

    @property
    def base_id(self) -> str:
        return normalize_base_read_id(self.header)


def open_text(path: str | Path, mode: str = "rt"):
    """Open plain text or gzip-compressed text."""

    path = str(path)
    return gzip.open(path, mode) if path.endswith(".gz") else open(path, mode)


def iter_fastq(path: str | Path) -> Iterator[FastqRecord]:
    """Yield FASTQ records from a file."""

    with open_text(path, "rt") as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            sequence = handle.readline()
            plus = handle.readline()
            quality = handle.readline()
            if not quality:
                raise ValueError(f"Malformed FASTQ record encountered in {path}")
            yield FastqRecord(header, sequence, plus, quality)


def write_fastq(path: str | Path, records: Iterable[FastqRecord]) -> None:
    """Write FASTQ records to a file."""

    with open_text(path, "wt") as handle:
        for record in records:
            handle.write(record.header)
            handle.write(record.sequence)
            handle.write(record.plus)
            handle.write(record.quality)

