"""Helpers for validating tracked canonical model artifacts."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .feature_schema import CANONICAL_PAIR_NOQ_FEATURE_COLUMNS, prepare_feature_frame

CANONICAL_MODEL_MANIFEST = Path("models/metadata/canonical_model_artifacts.json")
CANONICAL_MODEL_PATHS = {
    "gb": "models/pair_noq_tuned/gradient_boosting_tuned.joblib",
    "cnn": "models/deep/cnn_final_L150_seed42_fixedep25/cnn_final.pt",
    "bigru": "models/deep/rnnkmer_bigru_final_L150_seed42/rnn_kmer_gru_best.pt",
}
CANONICAL_MODEL_FAMILIES = {
    "gb": "tuned Gradient Boosting",
    "cnn": "CNN1D",
    "bigru": "BiGRU k-mer",
}
FEATURE_SCHEMA_PATH = Path("models/pair_noq_tuned/feature_cols_24.json")
EXAMPLE_FEATURES_PATH = Path("data/example/example_pair_features.tsv")
EXAMPLE_SEQUENCE_PATH = Path("data/example/example_pair_seq.tsv")


class ModelValidationError(RuntimeError):
    """Raised when tracked model validation fails."""


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    size_bytes: int
    sha256: str


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_artifact_manifest(path: Path) -> list[ArtifactRecord]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ModelValidationError(f"Artifact manifest must be a JSON list: {path}")

    records: list[ArtifactRecord] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ModelValidationError(f"Artifact manifest entry {index} is not an object: {path}")
        missing = [field for field in ("path", "size_bytes", "sha256") if field not in item]
        if missing:
            raise ModelValidationError(
                f"Artifact manifest entry {index} is missing required fields: {', '.join(missing)}"
            )
        records.append(
            ArtifactRecord(
                path=str(item["path"]),
                size_bytes=int(item["size_bytes"]),
                sha256=str(item["sha256"]),
            )
        )
    return records


def select_canonical_model_artifacts(records: list[ArtifactRecord]) -> dict[str, ArtifactRecord]:
    by_path = {record.path: record for record in records}
    selected: dict[str, ArtifactRecord] = {}
    missing: list[str] = []
    for key, relative_path in CANONICAL_MODEL_PATHS.items():
        record = by_path.get(relative_path)
        if record is None:
            missing.append(relative_path)
            continue
        selected[key] = record
    if missing:
        raise ModelValidationError(
            "Artifact manifest is missing canonical model entries: " + ", ".join(sorted(missing))
        )
    return selected


def resolve_repo_path(repo_root: Path, relative_path: str | Path) -> Path:
    return repo_root / Path(relative_path)


def inspect_artifact(repo_root: Path, record: ArtifactRecord) -> dict[str, Any]:
    artifact_path = resolve_repo_path(repo_root, record.path)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Tracked artifact not found: {artifact_path}")

    observed_size = artifact_path.stat().st_size
    observed_sha = compute_sha256(artifact_path)
    return {
        "path": record.path,
        "absolute_path": str(artifact_path),
        "expected_size_bytes": record.size_bytes,
        "observed_size_bytes": observed_size,
        "size_matches": observed_size == record.size_bytes,
        "expected_sha256": record.sha256,
        "observed_sha256": observed_sha,
        "sha256_matches": observed_sha == record.sha256,
    }


def package_version(import_name: str) -> str:
    try:
        module = importlib.import_module(import_name)
    except Exception:
        return "not installed"
    return str(getattr(module, "__version__", "installed"))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _assert_finite_probabilities(values: np.ndarray, *, label: str) -> None:
    if values.ndim != 1:
        raise ModelValidationError(f"{label} probabilities must be one-dimensional, got shape {values.shape}")
    if values.size == 0:
        raise ModelValidationError(f"{label} produced no probabilities")
    if not np.isfinite(values).all():
        raise ModelValidationError(f"{label} produced non-finite probabilities")
    if ((values < 0.0) | (values > 1.0)).any():
        raise ModelValidationError(f"{label} produced probabilities outside [0, 1]")


def _validate_gb_model(repo_root: Path, record: ArtifactRecord) -> dict[str, Any]:
    artifact = inspect_artifact(repo_root, record)
    if not artifact["size_matches"] or not artifact["sha256_matches"]:
        raise ModelValidationError(
            f"{CANONICAL_MODEL_FAMILIES['gb']} checksum mismatch for {artifact['absolute_path']}"
        )

    schema_path = resolve_repo_path(repo_root, FEATURE_SCHEMA_PATH)
    expected_schema = _load_json(schema_path)
    if expected_schema != CANONICAL_PAIR_NOQ_FEATURE_COLUMNS:
        raise ModelValidationError(f"Canonical feature schema mismatch in {schema_path}")

    feature_path = resolve_repo_path(repo_root, EXAMPLE_FEATURES_PATH)
    feature_df = pd.read_csv(feature_path, sep="\t")
    feature_frame = prepare_feature_frame(feature_df)
    if feature_frame.columns.tolist() != CANONICAL_PAIR_NOQ_FEATURE_COLUMNS:
        raise ModelValidationError("Prepared feature frame does not match the canonical 24-feature order")

    model = joblib.load(resolve_repo_path(repo_root, record.path))
    n_features = getattr(model, "n_features_in_", None)
    if n_features is not None and int(n_features) != len(CANONICAL_PAIR_NOQ_FEATURE_COLUMNS):
        raise ModelValidationError(
            f"Gradient Boosting checkpoint expects {n_features} features, not {len(CANONICAL_PAIR_NOQ_FEATURE_COLUMNS)}"
        )

    probabilities = np.asarray(model.predict_proba(feature_frame)[:, 1], dtype=float)
    _assert_finite_probabilities(probabilities, label=CANONICAL_MODEL_FAMILIES["gb"])
    return {
        "family": CANONICAL_MODEL_FAMILIES["gb"],
        "artifact": artifact,
        "expected_input": {
            "type": "tabular",
            "shape": [int(feature_frame.shape[0]), int(feature_frame.shape[1])],
            "feature_schema_path": str(FEATURE_SCHEMA_PATH),
        },
        "load_check": {
            "class_name": model.__class__.__name__,
            "n_features_in": None if n_features is None else int(n_features),
        },
        "smoke_prediction": {
            "rows": int(len(feature_frame)),
            "probabilities": [round(float(value), 8) for value in probabilities.tolist()],
        },
    }


def _require_torch(used_for: str):
    try:
        import torch
    except Exception as exc:
        raise ModelValidationError(
            f"{used_for} requires torch. Install the deep extras with `pip install -e \".[deep]\"`."
        ) from exc
    return torch


def _load_example_sequences(repo_root: Path, *, length: int):
    torch = _require_torch("Sequence model validation")
    from .deep_learning.dl_data import load_seq_tsv

    _ = torch  # keep local import explicit for lint clarity
    return load_seq_tsv(str(resolve_repo_path(repo_root, EXAMPLE_SEQUENCE_PATH)), L=length)


def _validate_cnn_model(repo_root: Path, record: ArtifactRecord) -> dict[str, Any]:
    artifact = inspect_artifact(repo_root, record)
    if not artifact["size_matches"] or not artifact["sha256_matches"]:
        raise ModelValidationError(
            f"{CANONICAL_MODEL_FAMILIES['cnn']} checksum mismatch for {artifact['absolute_path']}"
        )

    torch = _require_torch(CANONICAL_MODEL_FAMILIES["cnn"])
    from .deep_learning.dl_cnn import CNN1D
    from .deep_learning.dl_data import one_hot_4ch

    checkpoint = torch.load(resolve_repo_path(repo_root, record.path), map_location="cpu")
    if not isinstance(checkpoint, dict) or "model_state" not in checkpoint:
        raise ModelValidationError("CNN checkpoint must be a dict containing `model_state`")

    model = CNN1D(in_ch=4, dropout=0.2)
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.eval()

    sequence_df = _load_example_sequences(repo_root, length=150)
    encoded = np.stack([one_hot_4ch(seq) for seq in sequence_df["seq"].tolist()], axis=0)
    if encoded.shape[1:] != (4, 150):
        raise ModelValidationError(f"CNN input tensor shape must end with (4, 150), got {encoded.shape}")

    with torch.no_grad():
        logits = model(torch.from_numpy(encoded))
        probabilities = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()

    _assert_finite_probabilities(np.asarray(probabilities, dtype=float), label=CANONICAL_MODEL_FAMILIES["cnn"])
    return {
        "family": CANONICAL_MODEL_FAMILIES["cnn"],
        "artifact": artifact,
        "expected_input": {
            "type": "one_hot_sequence",
            "shape": [int(encoded.shape[0]), int(encoded.shape[1]), int(encoded.shape[2])],
        },
        "load_check": {
            "class_name": model.__class__.__name__,
            "in_channels": int(model.features[0].in_channels),
            "checkpoint_keys": sorted(checkpoint.keys()),
        },
        "smoke_prediction": {
            "rows": int(encoded.shape[0]),
            "probabilities": [round(float(value), 8) for value in probabilities.tolist()],
        },
    }


def _validate_bigru_model(repo_root: Path, record: ArtifactRecord) -> dict[str, Any]:
    artifact = inspect_artifact(repo_root, record)
    if not artifact["size_matches"] or not artifact["sha256_matches"]:
        raise ModelValidationError(
            f"{CANONICAL_MODEL_FAMILIES['bigru']} checksum mismatch for {artifact['absolute_path']}"
        )

    torch = _require_torch(CANONICAL_MODEL_FAMILIES["bigru"])
    from .deep_learning.dl_data import seq_to_kmer_tokens
    from .deep_learning.dl_rnn_kmer import RNNKmerClassifier

    checkpoint = torch.load(resolve_repo_path(repo_root, record.path), map_location="cpu")
    state_dict = checkpoint["model_state"] if isinstance(checkpoint, dict) and "model_state" in checkpoint else checkpoint

    model = RNNKmerClassifier(
        rnn_type="gru",
        vocab_size=(4 ** 4) + 1,
        embed_dim=64,
        hidden_size=256,
        num_layers=1,
        bidirectional=True,
        dropout=0.2,
        pool="last",
    )
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    sequence_df = _load_example_sequences(repo_root, length=150)
    encoded = np.stack(
        [seq_to_kmer_tokens(seq, k=4, L_kmers=147) for seq in sequence_df["seq"].tolist()],
        axis=0,
    )
    if encoded.shape[1] != 147:
        raise ModelValidationError(f"BiGRU token tensor shape must end with 147, got {encoded.shape}")

    with torch.no_grad():
        logits = model(torch.from_numpy(encoded))
        probabilities = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()

    _assert_finite_probabilities(np.asarray(probabilities, dtype=float), label=CANONICAL_MODEL_FAMILIES["bigru"])
    return {
        "family": CANONICAL_MODEL_FAMILIES["bigru"],
        "artifact": artifact,
        "expected_input": {
            "type": "kmer_tokens",
            "shape": [int(encoded.shape[0]), int(encoded.shape[1])],
            "k": 4,
            "L_kmers": 147,
        },
        "load_check": {
            "class_name": model.__class__.__name__,
            "vocab_size": int(model.embed.num_embeddings),
            "bidirectional": bool(model.bidirectional),
            "pool": model.pool,
        },
        "smoke_prediction": {
            "rows": int(encoded.shape[0]),
            "probabilities": [round(float(value), 8) for value in probabilities.tolist()],
        },
    }


def run_model_validation(repo_root: Path, *, manifest_path: Path | None = None) -> dict[str, Any]:
    manifest_path = manifest_path or resolve_repo_path(repo_root, CANONICAL_MODEL_MANIFEST)
    records = load_artifact_manifest(manifest_path)
    selected = select_canonical_model_artifacts(records)
    validators = {
        "gb": _validate_gb_model,
        "cnn": _validate_cnn_model,
        "bigru": _validate_bigru_model,
    }

    report: dict[str, Any] = {
        "repo_root": str(repo_root),
        "manifest_path": str(manifest_path),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "dependency_versions": {
            "numpy": package_version("numpy"),
            "pandas": package_version("pandas"),
            "joblib": package_version("joblib"),
            "scikit-learn": package_version("sklearn"),
            "torch": package_version("torch"),
        },
        "models": {},
    }

    failures = 0
    for key in ("gb", "cnn", "bigru"):
        try:
            model_report = validators[key](repo_root, selected[key])
            model_report["status"] = "PASS"
        except Exception as exc:
            failures += 1
            model_report = {
                "family": CANONICAL_MODEL_FAMILIES[key],
                "artifact": {
                    "path": selected[key].path,
                    "absolute_path": str(resolve_repo_path(repo_root, selected[key].path)),
                },
                "status": "FAIL",
                "error": str(exc),
                "error_type": exc.__class__.__name__,
            }
        report["models"][key] = model_report

    report["summary"] = {
        "passed_models": sum(1 for item in report["models"].values() if item["status"] == "PASS"),
        "failed_models": failures,
        "success": failures == 0,
    }
    return report
