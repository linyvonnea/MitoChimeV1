#!/usr/bin/env python3
'''PYTHONPATH=src python3 -m mitochime.build_pair_splits \
  --all data/processed/all_reads.tsv \
  --out-train data/processed/PAIR_train.tsv \
  --out-test  data/processed/PAIR_test.tsv \
  --test-size 0.2 \
  --random-state 42'''
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .feature_schema import validate_required_columns
from .utils.read_ids import normalize_base_read_id


def build_pair_split_frame(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a raw feature table by pair-level read IDs."""

    working = frame.copy()
    validate_required_columns(working, ["read_id", "label"], label="all_reads table")
    working["pair_id"] = working["read_id"].map(normalize_base_read_id)

    pair = working[["pair_id", "label"]].drop_duplicates("pair_id")
    pair["label"] = pair["label"].astype(int)

    train_ids, test_ids = train_test_split(
        pair["pair_id"],
        test_size=test_size,
        random_state=random_state,
        stratify=pair["label"],
    )

    train_ids = set(train_ids)
    test_ids = set(test_ids)

    df_train = working[working["pair_id"].isin(train_ids)].drop(columns=["pair_id"]).copy()
    df_test = working[working["pair_id"].isin(test_ids)].drop(columns=["pair_id"]).copy()
    if not set(df_train["read_id"].map(normalize_base_read_id)).isdisjoint(
        set(df_test["read_id"].map(normalize_base_read_id))
    ):
        raise ValueError("Pair overlap detected between train and test splits.")
    return df_train, df_test


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create a deterministic pair-aware train/test split from all_reads.tsv."
    )
    ap.add_argument("--all", required=True, help="all_reads.tsv")
    ap.add_argument("--out-train", required=True)
    ap.add_argument("--out-test", required=True)
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--random-state", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.all, sep="\t")
    df_train, df_test = build_pair_split_frame(
        df,
        test_size=args.test_size,
        random_state=args.random_state,
    )

    Path(args.out_train).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_test).parent.mkdir(parents=True, exist_ok=True)

    df_train.to_csv(args.out_train, sep="\t", index=False)
    df_test.to_csv(args.out_test, sep="\t", index=False)

    print(
        "[PAIR split] train rows="
        f"{len(df_train):,} unique_pair_ids={df_train['read_id'].map(normalize_base_read_id).nunique():,}"
    )
    print(
        "[PAIR split] test rows="
        f"{len(df_test):,} unique_pair_ids={df_test['read_id'].map(normalize_base_read_id).nunique():,}"
    )

if __name__ == "__main__":
    main()
