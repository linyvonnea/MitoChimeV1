"""Authoritative feature-schema definitions for canonical MitoChime data."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


RAW_DATASET_COLUMNS = [
    "read_id",
    "label",
    "read_length",
    "mean_base_quality",
    "ref_name",
    "ref_start_1based",
    "strand",
    "mapq",
    "cigar",
    "has_sa",
    "sa_count",
    "num_segments",
    "sa_diff_contig",
    "sa_min_delta_pos",
    "sa_max_delta_pos",
    "sa_mean_delta_pos",
    "sa_same_strand_count",
    "sa_opp_strand_count",
    "sa_max_mapq",
    "sa_mean_mapq",
    "sa_min_nm",
    "sa_mean_nm",
    "softclip_left",
    "softclip_right",
    "total_clipped_bases",
    "breakpoint_read_pos",
    "kmer_cosine_diff",
    "kmer_js_divergence",
    "microhomology_length",
    "microhomology_gc",
]

NON_FEATURE_COLUMNS = ["read_id", "label", "ref_name", "cigar"]
NOQ_DROP_COLUMNS = ["mean_base_quality", "ref_start_1based"]

CANONICAL_PAIR_NOQ_FEATURE_COLUMNS = [
    "read_length",
    "strand",
    "mapq",
    "has_sa",
    "sa_count",
    "num_segments",
    "sa_diff_contig",
    "sa_min_delta_pos",
    "sa_max_delta_pos",
    "sa_mean_delta_pos",
    "sa_same_strand_count",
    "sa_opp_strand_count",
    "sa_max_mapq",
    "sa_mean_mapq",
    "sa_min_nm",
    "sa_mean_nm",
    "softclip_left",
    "softclip_right",
    "total_clipped_bases",
    "breakpoint_read_pos",
    "kmer_cosine_diff",
    "kmer_js_divergence",
    "microhomology_length",
    "microhomology_gc",
]


def validate_required_columns(frame: pd.DataFrame, required: Iterable[str], *, label: str) -> None:
    """Raise a clear error when required columns are missing."""

    required = list(required)
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def normalize_strand_value(value) -> float:
    """Normalize strand encodings to the canonical numeric representation."""

    if pd.isna(value):
        return float("nan")
    text = str(value).strip()
    if text in {"+", "1", "1.0", "forward", "plus", "fwd", "F"}:
        return 1.0
    if text in {"-", "0", "0.0", "reverse", "minus", "rev", "R"}:
        return 0.0
    try:
        numeric = float(text)
    except ValueError:
        return float("nan")
    if numeric in {0.0, 1.0}:
        return numeric
    return float("nan")


def prepare_feature_frame(
    frame: pd.DataFrame,
    *,
    expected_features: Iterable[str] = CANONICAL_PAIR_NOQ_FEATURE_COLUMNS,
    allow_extra: bool = True,
) -> pd.DataFrame:
    """Prepare a feature-only frame with deterministic column ordering."""

    expected = list(expected_features)
    working = frame.copy()
    validate_required_columns(working, ["label"], label="feature table")

    if "strand" in working.columns:
        working["strand"] = working["strand"].map(normalize_strand_value)

    for column in working.columns:
        if column not in {"read_id", "ref_name", "cigar"}:
            working[column] = pd.to_numeric(working[column], errors="coerce")

    missing = [column for column in expected if column not in working.columns]
    if missing:
        raise ValueError(
            "feature table is missing canonical features: " + ", ".join(missing)
        )

    if not allow_extra:
        unexpected = [
            column
            for column in working.columns
            if column not in expected and column not in NON_FEATURE_COLUMNS
        ]
        if unexpected:
            raise ValueError(
                "feature table contains unexpected feature columns: "
                + ", ".join(unexpected)
            )

    feature_frame = working.reindex(columns=expected)
    for column in feature_frame.columns:
        median = feature_frame[column].median(skipna=True)
        feature_frame[column] = feature_frame[column].fillna(0.0 if pd.isna(median) else median)
    return feature_frame
