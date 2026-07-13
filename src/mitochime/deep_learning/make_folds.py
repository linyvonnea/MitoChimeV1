#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedKFold

from ..utils.read_ids import normalize_base_read_id

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create pair-safe fold assignments for deep-learning sequence TSVs."
    )
    ap.add_argument("--train-seq-tsv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.train_seq_tsv, sep="\t")
    if "read_id" not in df.columns or "label" not in df.columns:
        raise ValueError("train sequence TSV must contain read_id and label columns")
    df["base_id"] = df["read_id"].map(normalize_base_read_id)

    # pair-level label should be identical for both mates; take first per base_id
    base_df = df.groupby("base_id", as_index=False)["label"].first()

    skf = StratifiedKFold(n_splits=args.n_splits, shuffle=True, random_state=args.seed)
    base_df["fold"] = -1

    for fold, (_, val_idx) in enumerate(skf.split(base_df["base_id"], base_df["label"])):
        base_df.loc[val_idx, "fold"] = fold

    # map fold back to each read_id
    fold_map = dict(zip(base_df["base_id"], base_df["fold"]))
    df_out = df[["read_id"]].copy()
    df_out["fold"] = df["base_id"].map(fold_map).astype(int)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, sep="\t", index=False)

    # sanity
    print(f"[make_folds] wrote {len(df_out):,} read folds to {out_path}")
    print("[make_folds] folds counts:\n", df_out["fold"].value_counts().sort_index())
    # verify mates in same fold
    mates_ok = df.assign(fold=df_out["fold"]).groupby("base_id")["fold"].nunique().max() == 1
    print(f"[make_folds] mates_same_fold={mates_ok}")

if __name__ == "__main__":
    main()
