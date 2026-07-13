#!/usr/bin/env python3
"""
PYTHONPATH=src python3 -m mitochime.deep_learning.make_seq_tsv \
  --split-tsv data/processed/PAIR_train.tsv \
  --fastq data/raw/ref1.fastq data/raw/ref2.fastq data/raw/chime1.fastq data/raw/chime2.fastq \
  --L 150 \
  --out data/processed/PAIR_train_seq_L150.tsv

PYTHONPATH=src python3 -m mitochime.deep_learning.make_seq_tsv \
  --split-tsv data/processed/PAIR_test.tsv \
  --fastq data/raw/ref1.fastq data/raw/ref2.fastq data/raw/chime1.fastq data/raw/chime2.fastq \
  --L 150 \
  --out data/processed/PAIR_test_seq_L150.tsv
  
Build sequence TSVs for deep learning from a split TSV + FASTQ files.

Supports two split styles:
  (A) Pair-level IDs (no /1 or /2): e.g. "NC_..._abc"
      -> we include BOTH mates (base/1 and base/2) if present in FASTQs.

  (B) Read-level IDs (explicit /1 or /2): e.g. "NC_..._abc/1"
      -> we include only the explicit mates listed.

Output TSV columns:
  read_id   label   seq   [qual if --with-qual]

Example:
PYTHONPATH=src python3 -m mitochime.deep_learning.make_seq_tsv \
  --split-tsv data/processed/PAIR_train.tsv \
  --fastq data/raw/ref1.fastq data/raw/ref2.fastq data/raw/chime1.fastq data/raw/chime2.fastq \
  --L 150 \
  --out data/processed/PAIR_train_seq_L150.tsv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

import pandas as pd
from ..utils.fastq import open_text
from ..utils.read_ids import infer_mate_from_header, mate_specific_read_id, normalize_base_read_id, normalize_read_token, split_read_id


def iter_fastq_records(path: Path) -> Iterable[Tuple[str, str, str]]:
    """
    Yields (base_id, mate, seq, qual) per FASTQ record.
    """
    with open_text(path, "rt") as f:
        while True:
            h = f.readline()
            if not h:
                break
            seq = f.readline()
            plus = f.readline()
            qual = f.readline()
            if not qual:
                break
            base = normalize_base_read_id(h)
            mate = infer_mate_from_header(h) or "0"
            yield base, mate, seq.strip(), qual.strip()


def pad_or_trim(seq: str, L: int) -> str:
    seq = seq.upper()
    if len(seq) >= L:
        return seq[:L]
    return seq + ("N" * (L - len(seq)))


def pad_or_trim_qual(qual: str, L: int) -> str:
    if len(qual) >= L:
        return qual[:L]
    return qual + ("!" * (L - len(qual)))


def load_split_labels(tsv_path: Path) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Reads split TSV and returns:
      pair_labels:  base_id -> label   (if TSV has no /1 /2)
      read_labels:  base_id/mate -> label (if TSV explicitly has /1 or /2)

    If TSV mixes both, we support both simultaneously.
    """
    df = pd.read_csv(tsv_path, sep="\t")
    if "read_id" not in df.columns or "label" not in df.columns:
        raise ValueError(f"{tsv_path} must contain columns: read_id, label")

    df = df[["read_id", "label"]].copy()
    df["read_id"] = df["read_id"].astype(str)
    df["label"] = df["label"].astype(int)

    pair_labels: Dict[str, int] = {}
    read_labels: Dict[str, int] = {}

    for rid, lab in zip(df["read_id"], df["label"]):
        parts = split_read_id(rid)
        base, mate = parts.base_id, parts.mate
        if mate is None:
            # pair-level row
            if base not in pair_labels:
                pair_labels[base] = int(lab)
        else:
            # explicit mate-level row
            full = f"{base}/{mate}"
            if full not in read_labels:
                read_labels[full] = int(lab)

    return pair_labels, read_labels


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-tsv", required=True)
    ap.add_argument("--fastq", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--L", type=int, default=300)
    ap.add_argument("--with-qual", action="store_true")
    args = ap.parse_args()

    split_path = Path(args.split_tsv)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pair_labels, read_labels = load_split_labels(split_path)

    # For reporting
    wanted_pair = set(pair_labels.keys())
    wanted_reads = set(read_labels.keys())

    rows = []
    scanned = 0

    # Avoid duplicates across multiple FASTQs
    seen_reads: Set[str] = set()

    for fq in args.fastq:
        fq_path = Path(fq)
        for base, mate, seq, qual in iter_fastq_records(fq_path):
            scanned += 1

            # Build FASTQ-style read id
            rid = mate_specific_read_id(base, mate)

            # Determine if this FASTQ read is wanted
            label: Optional[int] = None
            if rid in read_labels:
                label = read_labels[rid]
            elif base in pair_labels and mate in ("1", "2"):
                # pair-level split => include BOTH mates as separate rows
                label = pair_labels[base]
            else:
                continue

            if rid in seen_reads:
                continue
            seen_reads.add(rid)

            row = {
                "read_id": rid,
                "label": label,
                "seq": pad_or_trim(seq, args.L),
            }
            if args.with_qual:
                row["qual"] = pad_or_trim_qual(qual or "", args.L)
            rows.append(row)

    if len(rows) == 0:
        raise RuntimeError(
            "No FASTQ reads matched the split TSV.\n"
            "Check that your FASTQs correspond to the same simulated dataset,\n"
            "and that your split TSV read_ids match the FASTQ headers (base ids or /1,/2)."
        )

    df_out = pd.DataFrame(rows).sort_values("read_id").reset_index(drop=True)
    df_out.to_csv(out_path, sep="\t", index=False)

    # Reporting: how many pairs were satisfied?
    matched_bases = {normalize_base_read_id(rid) for rid in df_out["read_id"].tolist()}
    missing_pairs = len(wanted_pair - matched_bases)

    print(f"[make_seq_tsv] scanned={scanned:,} FASTQ records")
    print(f"[make_seq_tsv] split pairs={len(wanted_pair):,} | split explicit reads={len(wanted_reads):,}")
    print(f"[make_seq_tsv] wrote={len(df_out):,} reads to {out_path}  shape={df_out.shape}")
    if len(wanted_pair) > 0:
        print(f"[make_seq_tsv] matched pair-bases={len(matched_bases):,} | missing pair-bases={missing_pairs:,}")
    print(f"[make_seq_tsv] unique read_ids in output={df_out['read_id'].nunique():,}")


if __name__ == "__main__":
    main()
