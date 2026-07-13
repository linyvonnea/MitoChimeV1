#!/usr/bin/env python3
"""Pair-safe Gradient Boosting inference and FASTQ filtering."""

from __future__ import annotations

import argparse
import json

import joblib
import pandas as pd

from mitochime.feature_schema import prepare_feature_frame
from mitochime.filtering import filter_pair_fastqs
from mitochime.utils.read_ids import normalize_base_read_id


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Score a feature table with the tuned GB model and filter paired FASTQ reads."
    )
    ap.add_argument("--r1", required=True)
    ap.add_argument("--r2", required=True)
    ap.add_argument("--features", required=True, help="TSV from extract_features.py")
    ap.add_argument("--model", required=True)
    ap.add_argument("--feature-cols", required=True, help="JSON list of columns in correct order")
    ap.add_argument("--thresh", type=float, required=True)
    ap.add_argument("--out-r1", required=True)
    ap.add_argument("--out-r2", required=True)
    args = ap.parse_args()

    with open(args.feature_cols) as f:
        feature_cols = json.load(f)

    df = pd.read_csv(args.features, sep="\t")
    if "read_id" not in df.columns:
        raise SystemExit("[ERROR] TSV missing required column: read_id")
    df["read_id"] = df["read_id"].map(normalize_base_read_id)

    X_df = prepare_feature_frame(df, expected_features=feature_cols)
    X = X_df.to_numpy(dtype=float)
    print(f"[INFO] X shape after preprocessing: {X.shape}")

    model = joblib.load(args.model)

    exp = getattr(model, "n_features_in_", None)
    if exp is not None and X.shape[1] != exp:
        raise SystemExit(f"[ERROR] Model expects {exp} features, but got {X.shape[1]}")

    proba = model.predict_proba(X)[:, 1]
    keep_mask = proba < args.thresh
    keep_ids = set(df.loc[keep_mask, "read_id"].astype(str).tolist())
    summary = filter_pair_fastqs(
        r1_path=args.r1,
        r2_path=args.r2,
        kept_ids=keep_ids,
        out_r1_path=args.out_r1,
        out_r2_path=args.out_r2,
    )

    print("[OK] GB pair-safe filtered outputs:")
    print(f"  {args.out_r1}")
    print(f"  {args.out_r2}")
    print(f"[INFO] kept pairs: {summary.kept_pairs:,}")


if __name__ == "__main__":
    main()
