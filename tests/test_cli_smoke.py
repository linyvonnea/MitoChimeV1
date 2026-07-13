import subprocess
import sys
from pathlib import Path


def test_cli_help_smoke():
    completed = subprocess.run(
        [sys.executable, "-m", "mitochime.cli", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "train-bigru" in completed.stdout
    assert "validate-models" in completed.stdout
    assert "report-environment" in completed.stdout


def test_filter_missing_model_reports_override_and_docs(tmp_path: Path):
    r1 = tmp_path / "reads_R1.fastq"
    r2 = tmp_path / "reads_R2.fastq"
    r1.write_text("@pairA/1\nACGT\n+\nIIII\n")
    r2.write_text("@pairA/2\nTGCA\n+\nIIII\n")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mitochime.cli",
            "filter",
            "--mode",
            "gb",
            "--r1",
            str(r1),
            "--r2",
            str(r2),
            "--run-name",
            "smoke",
            "--model-path",
            str(tmp_path / "missing.joblib"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "Gradient Boosting" in completed.stderr
    assert "--model-path" in completed.stderr
    assert "docs/models.md" in completed.stderr
