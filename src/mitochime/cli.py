"""Thin command-line interface for the verified MitoChime workflow."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


def _looks_like_repo_root(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "pyproject.toml").is_file()
        and (path / "src" / "mitochime").is_dir()
        and (path / "scripts").is_dir()
    )


def _detect_repo_root() -> Path | None:
    env_root = os.environ.get("MITOCHIME_REPO_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if _looks_like_repo_root(candidate):
            return candidate

    candidates = [Path.cwd(), *Path.cwd().parents]
    editable_candidate = PACKAGE_ROOT.parents[1]
    if editable_candidate not in candidates:
        candidates.insert(0, editable_candidate)

    for candidate in candidates:
        candidate = candidate.resolve()
        if _looks_like_repo_root(candidate):
            return candidate
    return None


REPO_ROOT = _detect_repo_root()
ENV = {**os.environ}
if REPO_ROOT is not None:
    ENV["PYTHONPATH"] = str(REPO_ROOT / "src")


def _require_repo_root(command_name: str) -> Path:
    if REPO_ROOT is None:
        raise SystemExit(
            "[ERROR] "
            f"{command_name} requires a cloned MitoChime repository checkout containing "
            "`pyproject.toml`, `src/`, and `scripts/`. Run the command from the repository root "
            "or set MITOCHIME_REPO_ROOT."
        )
    return REPO_ROOT


def _existing_file(path: str, *, label: str) -> Path:
    candidate = Path(path)
    if not candidate.is_file():
        raise SystemExit(f"[ERROR] {label} not found: {candidate}")
    return candidate


def _existing_dir(path: str, *, label: str) -> Path:
    candidate = Path(path)
    if not candidate.is_dir():
        raise SystemExit(f"[ERROR] {label} not found: {candidate}")
    return candidate


def _run(command: list[str]) -> int:
    completed = subprocess.run(command, cwd=REPO_ROOT or Path.cwd(), env=ENV, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def cmd_build_dataset(args: argparse.Namespace) -> int:
    _existing_file(args.clean, label="clean feature table")
    _existing_file(args.chim, label="chimeric feature table")
    return _run(
        [
            PYTHON,
            "-m",
            "mitochime.build_datasets",
            "--clean",
            args.clean,
            "--chim",
            args.chim,
            "--out-all",
            args.out_all,
            "--train",
            args.train,
            "--test",
            args.test,
            "--test-size",
            str(args.test_size),
            "--random-state",
            str(args.random_state),
        ]
    )


def cmd_split(args: argparse.Namespace) -> int:
    _existing_file(args.all_reads, label="all_reads table")
    return _run(
        [
            PYTHON,
            "-m",
            "mitochime.build_pair_splits",
            "--all",
            args.all_reads,
            "--out-train",
            args.out_train,
            "--out-test",
            args.out_test,
            "--test-size",
            str(args.test_size),
            "--random-state",
            str(args.random_state),
        ]
    )


def cmd_train_classical(args: argparse.Namespace) -> int:
    _existing_file(args.train, label="training TSV")
    _existing_file(args.test, label="test TSV")
    return _run(
        [
            PYTHON,
            "-m",
            "mitochime.train_all_models",
            "--train",
            args.train,
            "--test",
            args.test,
            "--models-dir",
            args.models_dir,
            "--reports-dir",
            args.reports_dir,
        ]
    )


def _train_deep(mode: str, args: argparse.Namespace) -> int:
    _existing_file(args.train_tsv, label="training sequence TSV")
    _existing_file(args.test_tsv, label="test sequence TSV")
    return _run(
        [
            PYTHON,
            "-m",
            "mitochime.deep_learning.train_deep",
            "--mode",
            mode,
            "--train-tsv",
            args.train_tsv,
            "--test-tsv",
            args.test_tsv,
            "--out-dir",
            args.out_dir,
            "--reports-dir",
            args.reports_dir,
            "--L",
            str(args.L),
            "--batch",
            str(args.batch),
            "--epochs",
            str(args.epochs),
            "--lr",
            str(args.lr),
            "--weight-decay",
            str(args.weight_decay),
            "--seed",
            str(args.seed),
            "--save-predictions",
        ]
        + (
            [
                "--k",
                str(args.k),
                "--L-kmers",
                str(args.L_kmers),
                "--embed-dim",
                str(args.embed_dim),
                "--hidden",
                str(args.hidden),
                "--rnn-layers",
                str(args.rnn_layers),
                "--pool",
                args.pool,
                "--bidirectional",
            ]
            if mode == "rnn_kmer_gru"
            else []
        )
    )


def cmd_train_cnn(args: argparse.Namespace) -> int:
    return _train_deep("cnn", args)


def cmd_train_bigru(args: argparse.Namespace) -> int:
    return _train_deep("rnn_kmer_gru", args)


def cmd_extract_features(args: argparse.Namespace) -> int:
    _existing_file(args.bam, label="input BAM")
    repo_root = _require_repo_root("extract-features")
    return _run(
        [
            PYTHON,
            str(repo_root / "scripts" / "data_prep" / "extract_features.py"),
            "--bam",
            args.bam,
            "--out",
            args.out,
            "--label",
            str(args.label),
            "--k",
            str(args.k),
            "--micro-window",
            str(args.micro_window),
        ]
    )


def cmd_filter(args: argparse.Namespace) -> int:
    _existing_file(args.r1, label="R1 FASTQ")
    _existing_file(args.r2, label="R2 FASTQ")
    repo_root = _require_repo_root("filter")
    script_map = {
        "gb": repo_root / "scripts" / "inference" / "run_pipeline_gb.sh",
        "cnn": repo_root / "scripts" / "inference" / "run_pipeline_cnn.sh",
        "bigru": repo_root / "scripts" / "inference" / "run_pipeline_rnnkmer.sh",
    }
    command = ["bash", str(script_map[args.mode]), args.r1, args.r2, args.run_name, str(args.threshold)]
    if args.mode == "gb":
        command.extend([str(args.threads), args.reference])
    return _run(command)


def cmd_validate_pairs(args: argparse.Namespace) -> int:
    repo_root = _require_repo_root("validate-pairs")
    command = [
        PYTHON,
        str(repo_root / "scripts" / "validation" / "validate_pair_integrity.py"),
        "--feature-dataset",
        args.feature_dataset,
        "--sequence-dataset",
        args.sequence_dataset,
        "--report-json",
        args.report_json,
    ]
    if args.split_dataset:
        command.extend(["--split-dataset", args.split_dataset])
    return _run(command)


def cmd_report_environment(_: argparse.Namespace) -> int:
    external_tools = ["minimap2", "samtools", "seqkit", "spades.py", "get_organelle_from_reads.py", "wgsim"]
    print(f"Python executable: {PYTHON}")
    print(f"Package root: {PACKAGE_ROOT}")
    print(f"Repository root: {REPO_ROOT or 'NOT DETECTED'}")
    print("External tools:")
    for tool in external_tools:
        print(f"  {tool}: {shutil.which(tool) or 'NOT FOUND'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mitochime", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract-features", help="Extract the canonical 30-column feature table.")
    extract_parser.add_argument("--bam", required=True, help="Coordinate-sorted BAM file.")
    extract_parser.add_argument("--out", required=True, help="Output feature TSV.")
    extract_parser.add_argument("--label", type=int, required=True, help="Class label to assign (0, 1, or -1).")
    extract_parser.add_argument("--k", type=int, default=6, help="k-mer size used for composition features.")
    extract_parser.add_argument(
        "--micro-window",
        type=int,
        default=40,
        help="Window size for microhomology extraction around the inferred breakpoint.",
    )
    extract_parser.set_defaults(func=cmd_extract_features)

    build_parser_cmd = subparsers.add_parser("build-dataset", help="Build all_reads/train/test from clean and chimeric features.")
    build_parser_cmd.add_argument("--clean", required=True)
    build_parser_cmd.add_argument("--chim", required=True)
    build_parser_cmd.add_argument("--out-all", required=True)
    build_parser_cmd.add_argument("--train", required=True)
    build_parser_cmd.add_argument("--test", required=True)
    build_parser_cmd.add_argument("--test-size", type=float, default=0.2)
    build_parser_cmd.add_argument("--random-state", type=int, default=42)
    build_parser_cmd.set_defaults(func=cmd_build_dataset)

    split_parser = subparsers.add_parser("split", help="Create the pair-aware train/test split.")
    split_parser.add_argument("--all-reads", required=True)
    split_parser.add_argument("--out-train", required=True)
    split_parser.add_argument("--out-test", required=True)
    split_parser.add_argument("--test-size", type=float, default=0.2)
    split_parser.add_argument("--random-state", type=int, default=42)
    split_parser.set_defaults(func=cmd_split)

    train_classical_parser = subparsers.add_parser("train-classical", help="Train the baseline classical-model comparison panel.")
    train_classical_parser.add_argument("--train", required=True)
    train_classical_parser.add_argument("--test", required=True)
    train_classical_parser.add_argument("--models-dir", required=True)
    train_classical_parser.add_argument("--reports-dir", required=True)
    train_classical_parser.set_defaults(func=cmd_train_classical)

    for command_name, help_text, func in [
        ("train-cnn", "Train the canonical CNN1D model.", cmd_train_cnn),
        ("train-bigru", "Train the canonical BiGRU k-mer model.", cmd_train_bigru),
    ]:
        deep_parser = subparsers.add_parser(command_name, help=help_text)
        deep_parser.add_argument("--train-tsv", required=True)
        deep_parser.add_argument("--test-tsv", required=True)
        deep_parser.add_argument("--out-dir", required=True)
        deep_parser.add_argument("--reports-dir", required=True)
        deep_parser.add_argument("--L", type=int, default=150)
        deep_parser.add_argument("--batch", type=int, default=128)
        deep_parser.add_argument("--epochs", type=int, default=25 if command_name == "train-cnn" else 30)
        deep_parser.add_argument("--lr", type=float, default=1e-3)
        deep_parser.add_argument("--weight-decay", type=float, default=1e-4)
        deep_parser.add_argument("--seed", type=int, default=42)
        deep_parser.add_argument("--k", type=int, default=4)
        deep_parser.add_argument("--L-kmers", dest="L_kmers", type=int, default=147)
        deep_parser.add_argument("--embed-dim", dest="embed_dim", type=int, default=64)
        deep_parser.add_argument("--hidden", type=int, default=256)
        deep_parser.add_argument("--rnn-layers", dest="rnn_layers", type=int, default=1)
        deep_parser.add_argument("--pool", choices=["last", "mean", "max"], default="last")
        deep_parser.set_defaults(func=func)

    filter_parser = subparsers.add_parser("filter", help="Run one of the verified pair-safe inference/filtering pipelines.")
    filter_parser.add_argument("--mode", choices=["gb", "cnn", "bigru"], required=True)
    filter_parser.add_argument("--r1", required=True)
    filter_parser.add_argument("--r2", required=True)
    filter_parser.add_argument("--run-name", required=True)
    filter_parser.add_argument("--threshold", type=float, default=0.5)
    filter_parser.add_argument("--threads", type=int, default=8, help="Used by the GB pipeline.")
    filter_parser.add_argument(
        "--reference",
        default="data/refs/original.fasta",
        help="Reference FASTA used by the GB pipeline.",
    )
    filter_parser.set_defaults(func=cmd_filter)

    validate_parser = subparsers.add_parser("validate-pairs", help="Audit pair-level integrity across publication datasets.")
    validate_parser.add_argument("--feature-dataset", required=True)
    validate_parser.add_argument("--sequence-dataset", required=True)
    validate_parser.add_argument("--split-dataset")
    validate_parser.add_argument("--report-json", required=True)
    validate_parser.set_defaults(func=cmd_validate_pairs)

    env_parser = subparsers.add_parser("report-environment", help="Report Python and external bioinformatics tool availability.")
    env_parser.set_defaults(func=cmd_report_environment)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
