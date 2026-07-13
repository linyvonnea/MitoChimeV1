#!/usr/bin/env python3
"""
Make a sequence TSV for INFERENCE (no labels) from arbitrary FASTQ/FASTQ.GZ.

Output columns:
  read_id   seq

Example:
PYTHONPATH=src python3 -m mitochime.deep_learning.make_seq_tsv_infer \
  --r1 reads_R1.fastq.gz \
  --r2 reads_R2.fastq.gz \
  --L 150 \
  --out data/dl/myrun.seq.tsv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Tuple

from ..utils.read_ids import infer_mate_from_header, mate_specific_read_id, normalize_base_read_id, normalize_read_token

from ..utils.fastq import iter_fastq as iter_fastq_records_raw


def iter_fastq(path: str) -> Iterable[Tuple[str, str]]:
    """
    Yield (read_id, seq) from FASTQ.
    """
    for record in iter_fastq_records(path):
        yield record


def pad_or_trim(seq: str, L: int) -> str:
    seq = seq.upper()
    if len(seq) >= L:
        return seq[:L]
    return seq + ("N" * (L - len(seq)))


def iter_fastq_records(path: str) -> Iterable[Tuple[str, str]]:
    """Yield `(read_id, seq)` pairs from FASTQ records."""

    for record in iter_fastq_records_raw(path):
        yield normalize_read_token(record.header), record.sequence.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r1", required=True)
    ap.add_argument("--r2", required=True)
    ap.add_argument("--L", type=int, default=150)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    r1_map = {}
    for rid, seq in iter_fastq(args.r1):
        base = normalize_base_read_id(rid)
        mate = infer_mate_from_header(rid) or "1"
        r1_map[base] = (mate_specific_read_id(base, mate), pad_or_trim(seq, args.L))

    rows = []
    kept_pairs = 0
    scanned_r2 = 0

    for rid2, seq2 in iter_fastq(args.r2):
        scanned_r2 += 1
        base = normalize_base_read_id(rid2)
        if base not in r1_map:
            continue

        rid1, seq1 = r1_map[base]
        seq2 = pad_or_trim(seq2, args.L)

        rid2 = mate_specific_read_id(base, infer_mate_from_header(rid2) or "2")

        rows.append((rid1, seq1))
        rows.append((rid2, seq2))
        kept_pairs += 1

    if kept_pairs == 0:
        raise SystemExit("[ERROR] No paired reads found between R1 and R2.")

    # Write TSV
    with out_path.open("w") as out:
        out.write("read_id\tseq\n")
        for rid, seq in rows:
            out.write(f"{rid}\t{seq}\n")

    print(f"[make_seq_tsv_infer] wrote {len(rows):,} reads ({kept_pairs:,} pairs) to {out_path}")
    print(f"[make_seq_tsv_infer] scanned R2 records: {scanned_r2:,}")


if __name__ == "__main__":
    main()
