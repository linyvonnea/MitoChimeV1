#!/usr/bin/env python3
"""Validate tracked canonical MitoChime model artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mitochime.model_validation import CANONICAL_MODEL_MANIFEST, run_model_validation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate tracked canonical model artifacts, checksums, and smoke predictions."
    )
    parser.add_argument(
        "--manifest",
        default=str(CANONICAL_MODEL_MANIFEST),
        help="Relative path to the canonical JSON checksum manifest.",
    )
    parser.add_argument(
        "--report-json",
        help="Optional output path for the machine-readable validation report.",
    )
    args = parser.parse_args()

    manifest_path = REPO_ROOT / args.manifest
    report = run_model_validation(REPO_ROOT, manifest_path=manifest_path)

    for key in ("gb", "cnn", "bigru"):
        item = report["models"][key]
        if item["status"] == "PASS":
            artifact = item["artifact"]
            smoke = item["smoke_prediction"]
            print(
                f"[PASS] {key}: {item['family']} | {artifact['path']} | "
                f"sha256={artifact['observed_sha256']} | smoke_rows={smoke['rows']}"
            )
        else:
            print(f"[FAIL] {key}: {item['family']} | {item['error']}", file=sys.stderr)

    if args.report_json:
        out_path = REPO_ROOT / args.report_json
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n")
        print(f"[OK] wrote model validation report to {out_path}")

    summary = report["summary"]
    if summary["success"]:
        print(f"[OK] validated {summary['passed_models']} canonical model artifacts")
        return 0

    print(
        f"[ERROR] model validation failed for {summary['failed_models']} model family/families",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
