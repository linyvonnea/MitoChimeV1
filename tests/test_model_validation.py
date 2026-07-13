import json
from pathlib import Path

import pytest

from mitochime.model_validation import (
    ArtifactRecord,
    CANONICAL_MODEL_PATHS,
    ModelValidationError,
    compute_sha256,
    inspect_artifact,
    load_artifact_manifest,
    resolve_repo_path,
    select_canonical_model_artifacts,
)


def test_load_artifact_manifest_parses_expected_records(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "path": CANONICAL_MODEL_PATHS["gb"],
                    "size_bytes": 12,
                    "sha256": "abc123",
                }
            ]
        )
    )

    records = load_artifact_manifest(manifest)

    assert records == [ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=12, sha256="abc123")]


def test_load_artifact_manifest_rejects_missing_fields(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"path": CANONICAL_MODEL_PATHS["gb"], "size_bytes": 12}]))

    with pytest.raises(ModelValidationError, match="missing required fields"):
        load_artifact_manifest(manifest)


def test_select_canonical_model_artifacts_filters_noncanonical_entries():
    records = [
        ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=1, sha256="gb"),
        ArtifactRecord(path="models/pair_noq_tuned/feature_cols_24.json", size_bytes=2, sha256="schema"),
        ArtifactRecord(path=CANONICAL_MODEL_PATHS["cnn"], size_bytes=3, sha256="cnn"),
        ArtifactRecord(path=CANONICAL_MODEL_PATHS["bigru"], size_bytes=4, sha256="bigru"),
    ]

    selected = select_canonical_model_artifacts(records)

    assert set(selected) == {"gb", "cnn", "bigru"}
    assert selected["cnn"].sha256 == "cnn"


def test_select_canonical_model_artifacts_requires_all_three_models():
    records = [
        ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=1, sha256="gb"),
        ArtifactRecord(path=CANONICAL_MODEL_PATHS["cnn"], size_bytes=3, sha256="cnn"),
    ]

    with pytest.raises(ModelValidationError, match="missing canonical model entries"):
        select_canonical_model_artifacts(records)


def test_resolve_repo_path_joins_repo_root_and_relative_path(tmp_path: Path):
    resolved = resolve_repo_path(tmp_path, CANONICAL_MODEL_PATHS["gb"])
    assert resolved == tmp_path / CANONICAL_MODEL_PATHS["gb"]


def test_inspect_artifact_reports_matching_checksum_and_size(tmp_path: Path):
    artifact_path = tmp_path / CANONICAL_MODEL_PATHS["gb"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(b"canonical-model")
    digest = compute_sha256(artifact_path)
    record = ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=artifact_path.stat().st_size, sha256=digest)

    report = inspect_artifact(tmp_path, record)

    assert report["size_matches"] is True
    assert report["sha256_matches"] is True
    assert report["observed_sha256"] == digest


def test_inspect_artifact_flags_corrupted_contents(tmp_path: Path):
    artifact_path = tmp_path / CANONICAL_MODEL_PATHS["gb"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(b"corrupted-model")
    record = ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=artifact_path.stat().st_size, sha256="deadbeef")

    report = inspect_artifact(tmp_path, record)

    assert report["size_matches"] is True
    assert report["sha256_matches"] is False


def test_inspect_artifact_raises_for_missing_model_file(tmp_path: Path):
    record = ArtifactRecord(path=CANONICAL_MODEL_PATHS["gb"], size_bytes=1, sha256="abc")

    with pytest.raises(FileNotFoundError, match="Tracked artifact not found"):
        inspect_artifact(tmp_path, record)
