import json
import subprocess
import sys
from pathlib import Path


def test_validate_pair_integrity_reports_missing_mates(tmp_path: Path):
    feature = tmp_path / "features.tsv"
    feature.write_text("read_id\tlabel\npairA/1\t0\npairA/2\t0\npairB/1\t1\n")
    sequence = tmp_path / "sequence.tsv"
    sequence.write_text("read_id\tlabel\tseq\npairA/1\t0\tAAAA\npairA/2\t0\tTTTT\npairB/1\t1\tCCCC\npairB/2\t1\tGGGG\n")
    split = tmp_path / "split.tsv"
    split.write_text("read_id\tlabel\npairA\t0\npairB\t1\n")
    report = tmp_path / "report.json"

    subprocess.run(
        [
            sys.executable,
            "scripts/validation/validate_pair_integrity.py",
            "--feature-dataset",
            str(feature),
            "--sequence-dataset",
            str(sequence),
            "--split-dataset",
            str(split),
            "--report-json",
            str(report),
        ],
        check=True,
    )

    payload = json.loads(report.read_text())
    assert payload["feature_pair_multiplicities"] == {"1": 1, "2": 1}
    assert payload["sequence_pair_multiplicities"] == {"2": 2}
    assert payload["pair_ids_only_in_sequence_dataset"] == []

