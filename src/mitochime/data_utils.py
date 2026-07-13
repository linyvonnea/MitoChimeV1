#!/usr/bin/env python3
"""Utilities for loading and validating canonical feature tables."""

from __future__ import annotations

from typing import Tuple

import pandas as pd

from .feature_schema import CANONICAL_PAIR_NOQ_FEATURE_COLUMNS, prepare_feature_frame


def load_feature_table(path: str) -> pd.DataFrame:
    """Load a tabular feature dataset."""

    return pd.read_csv(path, sep="\t")


def prepare_X_y(
    df: pd.DataFrame,
    *,
    expected_features: list[str] | None = None,
    allow_extra: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Turn a raw feature table into `(X, y)` with fixed feature ordering.

    The canonical publication workflow expects the pair-safe no-quality feature
    order recovered from `feature_cols_24.json`, including `strand`.
    """

    expected = expected_features or CANONICAL_PAIR_NOQ_FEATURE_COLUMNS
    working = df.copy()
    if "label" not in working.columns:
        raise ValueError("Expected a 'label' column in the feature table.")
    working["label"] = pd.to_numeric(working["label"], errors="raise").astype(int)
    X = prepare_feature_frame(
        working,
        expected_features=expected,
        allow_extra=allow_extra,
    )
    y = working["label"]
    return X, y
