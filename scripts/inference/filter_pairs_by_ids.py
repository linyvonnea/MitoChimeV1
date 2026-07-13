#!/usr/bin/env python3
"""Pair-safe FASTQ filtering by base read IDs."""

from __future__ import annotations

import argparse

from mitochime.filtering import filter_pair_fastqs
from mitochime.utils.fastq import iter_fastq, open_text
from mitochime.utils.read_ids import normalize_base_read_id


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Remove paired-end reads using a one-ID-per-line removal list."
    )
    ap.add_argument("--r1", required=True)
    ap.add_argument("--r2", required=True)
    ap.add_argument("--remove-ids", required=True, help="one base read_id per line")
    ap.add_argument("--out-r1", required=True)
    ap.add_argument("--out-r2", required=True)
    args = ap.parse_args()

    remove = set()
    with open_text(args.remove_ids, "rt") as f:
        for line in f:
            x = line.strip()
            if x:
                remove.add(normalize_base_read_id(x))

    keep_ids = {
        record.base_id
        for record in iter_fastq(args.r1)
        if record.base_id not in remove
    }

    summary = filter_pair_fastqs(
        r1_path=args.r1,
        r2_path=args.r2,
        kept_ids=keep_ids,
        out_r1_path=args.out_r1,
        out_r2_path=args.out_r2,
    )

    print("[OK] Pair-safe filtered outputs:")
    print(f"  {args.out_r1}")
    print(f"  {args.out_r2}")
    print(f"[INFO] total_r1={summary.total_r1:,} total_r2={summary.total_r2:,}")
    print(f"[INFO] kept_pairs={summary.kept_pairs:,} orphan_r2={summary.orphan_r2:,}")

if __name__ == "__main__":
    main()
