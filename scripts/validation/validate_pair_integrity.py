#!/usr/bin/env python3
"""Validate pair integrity across tabular and sequence publication datasets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mitochime.utils.read_ids import normalize_base_read_id


def summarize_counts(series: pd.Series) -> dict[str, int]:
    counts = Counter(series.map(normalize_base_read_id))
    return {str(k): int(v) for k, v in sorted(Counter(counts.values()).items())}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a machine-readable report for pair completeness discrepancies."
    )
    parser.add_argument("--feature-dataset", required=True)
    parser.add_argument("--sequence-dataset", required=True)
    parser.add_argument("--split-dataset")
    parser.add_argument("--report-json", required=True)
    args = parser.parse_args()

    feature_df = pd.read_csv(args.feature_dataset, sep="\t")
    sequence_df = pd.read_csv(args.sequence_dataset, sep="\t")

    feature_ids = feature_df["read_id"].map(normalize_base_read_id)
    sequence_ids = sequence_df["read_id"].map(normalize_base_read_id)

    feature_id_set = set(feature_ids)
    sequence_id_set = set(sequence_ids)
    split_id_set = None
    if args.split_dataset:
        split_df = pd.read_csv(args.split_dataset, sep="\t")
        split_id_set = set(split_df["read_id"].map(normalize_base_read_id))

    report = {
        "feature_dataset": args.feature_dataset,
        "sequence_dataset": args.sequence_dataset,
        "split_dataset": args.split_dataset,
        "feature_rows": int(len(feature_df)),
        "sequence_rows": int(len(sequence_df)),
        "feature_unique_pair_ids": int(len(feature_id_set)),
        "sequence_unique_pair_ids": int(len(sequence_id_set)),
        "feature_pair_multiplicities": summarize_counts(feature_df["read_id"]),
        "sequence_pair_multiplicities": summarize_counts(sequence_df["read_id"]),
        "pair_ids_only_in_feature_dataset": sorted(feature_id_set - sequence_id_set),
        "pair_ids_only_in_sequence_dataset": sorted(sequence_id_set - feature_id_set),
    }
    if split_id_set is not None:
        report["split_unique_pair_ids"] = int(len(split_id_set))
        report["feature_vs_split_missing_pair_ids"] = sorted(split_id_set - feature_id_set)
        report["sequence_vs_split_missing_pair_ids"] = sorted(split_id_set - sequence_id_set)

    out_path = Path(args.report_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"[OK] wrote integrity report to {out_path}")


if __name__ == "__main__":
    main()
