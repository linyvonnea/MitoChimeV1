import subprocess
import sys


def test_cli_help_smoke():
    completed = subprocess.run(
        [sys.executable, "-m", "mitochime.cli", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "train-bigru" in completed.stdout
    assert "report-environment" in completed.stdout
