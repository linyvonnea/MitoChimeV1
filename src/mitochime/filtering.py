"""Pair-safe FASTQ filtering helpers used by operational inference scripts."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .utils.fastq import FastqRecord, iter_fastq, write_fastq
from .utils.read_ids import normalize_base_read_id


@dataclass(frozen=True)
class PairFilterSummary:
    """Summary of a pair-safe FASTQ filtering run."""

    total_r1: int
    total_r2: int
    kept_pairs: int
    orphan_r2: int


def _materialize_kept_r1(r1_path: str | Path, kept_ids: set[str]) -> tuple[dict[str, FastqRecord], int]:
    records: dict[str, FastqRecord] = {}
    total = 0
    for record in iter_fastq(r1_path):
        total += 1
        if record.base_id in kept_ids:
            records[record.base_id] = record
    return records, total


def filter_pair_fastqs(
    *,
    r1_path: str | Path,
    r2_path: str | Path,
    kept_ids: Iterable[str],
    out_r1_path: str | Path,
    out_r2_path: str | Path,
) -> PairFilterSummary:
    """Write filtered FASTQ files while keeping mate membership synchronized."""

    normalized_ids = {normalize_base_read_id(value) for value in kept_ids if normalize_base_read_id(value)}
    kept_r1, total_r1 = _materialize_kept_r1(r1_path, normalized_ids)

    r2_kept: list[FastqRecord] = []
    total_r2 = 0
    orphan_r2 = 0
    matched_ids: set[str] = set()
    for record in iter_fastq(r2_path):
        total_r2 += 1
        base_id = record.base_id
        if base_id not in kept_r1:
            if base_id in normalized_ids:
                orphan_r2 += 1
            continue
        matched_ids.add(base_id)
        r2_kept.append(record)

    kept_r1_records = [kept_r1[base_id] for base_id in kept_r1 if base_id in matched_ids]
    write_fastq(out_r1_path, kept_r1_records)
    write_fastq(out_r2_path, r2_kept)

    return PairFilterSummary(
        total_r1=total_r1,
        total_r2=total_r2,
        kept_pairs=len(matched_ids),
        orphan_r2=orphan_r2,
    )
