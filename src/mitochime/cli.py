"""Thin command-line interface for the verified MitoChime workflow."""

from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable
MODEL_DOC_PATH = "docs/models.md"
MODEL_DEFAULTS = {
    "gb": Path("models/pair_noq_tuned/gradient_boosting_tuned.joblib"),
    "cnn": Path("models/deep/cnn_final_L150_seed42_fixedep25/cnn_final.pt"),
    "bigru": Path("models/deep/rnnkmer_bigru_final_L150_seed42/rnn_kmer_gru_best.pt"),
}
MODEL_OVERRIDE_ARGS = {
    "gb": "--model-path",
    "cnn": "--model-path",
    "bigru": "--model-path",
}
MODEL_OVERRIDE_ENV = {
    "gb": "GB_MODEL",
    "cnn": "CNN_MODEL",
    "bigru": "RNN_MODEL",
}
MODEL_FAMILIES = {
    "gb": "tuned Gradient Boosting",
    "cnn": "CNN1D",
    "bigru": "BiGRU k-mer",
}


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


def _run(command: list[str], *, env: dict[str, str] | None = None) -> int:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT or Path.cwd(),
        env=env or ENV,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def _require_python_modules(modules: list[tuple[str, str]], *, used_for: str, install_hint: str) -> None:
    missing = []
    for import_name, package_name in modules:
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append(package_name)
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(
            "[ERROR] "
            f"{used_for} requires optional Python dependencies that are not installed: {missing_list}. "
            f"Install them with `{install_hint}`."
        )


def _missing_model_error(mode: str, expected_path: Path) -> str:
    return (
        "[ERROR] "
        f"{MODEL_FAMILIES[mode]} model not found at {expected_path}. "
        f"Override the default model location with `{MODEL_OVERRIDE_ARGS[mode]}` "
        f"or the `{MODEL_OVERRIDE_ENV[mode]}` environment variable. "
        f"See {MODEL_DOC_PATH} for model availability and release policy."
    )


def _tool_version(tool: str, args: list[str]) -> str:
    tool_path = shutil.which(tool)
    if tool_path is None:
        return "not installed"
    try:
        completed = subprocess.run(
            [tool, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return f"detected at {tool_path} (version unavailable: {exc.__class__.__name__})"

    output = (completed.stdout or completed.stderr).strip().splitlines()
    if output:
        return output[0]
    return f"detected at {tool_path}"


def _module_status(import_name: str) -> str:
    try:
        module = importlib.import_module(import_name)
    except Exception:
        return "not installed"
    version = getattr(module, "__version__", None)
    if version is None and import_name == "Bio":
        version = getattr(module, "__version__", None)
    return str(version or "installed")


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
    _require_python_modules(
        [
            ("xgboost", "xgboost"),
            ("lightgbm", "lightgbm"),
            ("catboost", "catboost"),
        ],
        used_for="train-classical",
        install_hint="pip install .[classical]",
    )
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
    _require_python_modules(
        [("torch", "torch")],
        used_for=f"train-{mode}",
        install_hint="pip install .[deep]",
    )
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
    model_path = Path(args.model_path) if args.model_path else MODEL_DEFAULTS[args.mode]
    if not model_path.is_file():
        raise SystemExit(_missing_model_error(args.mode, model_path))
    env = dict(ENV)
    env[MODEL_OVERRIDE_ENV[args.mode]] = str(model_path)
    script_map = {
        "gb": repo_root / "scripts" / "inference" / "run_pipeline_gb.sh",
        "cnn": repo_root / "scripts" / "inference" / "run_pipeline_cnn.sh",
        "bigru": repo_root / "scripts" / "inference" / "run_pipeline_rnnkmer.sh",
    }
    command = ["bash", str(script_map[args.mode]), args.r1, args.r2, args.run_name, str(args.threshold)]
    if args.mode == "gb":
        feature_cols = repo_root / "models" / "pair_noq_tuned" / "feature_cols_24.json"
        if not feature_cols.is_file():
            raise SystemExit(
                "[ERROR] Canonical feature schema not found at "
                f"{feature_cols}. See {MODEL_DOC_PATH} for the retained model metadata."
            )
        command.extend([str(args.threads), args.reference])
    return _run(command, env=env)


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
    external_tools = {
        "minimap2": ["--version"],
        "samtools": ["--version"],
        "seqkit": ["version"],
        "spades.py": ["--version"],
        "get_organelle_from_reads.py": ["--version"],
        "wgsim": [],
    }
    python_modules = {
        "numpy": "numpy",
        "pandas": "pandas",
        "scikit-learn": "sklearn",
        "joblib": "joblib",
        "pysam": "pysam",
        "biopython": "Bio",
        "pyyaml": "yaml",
        "tqdm": "tqdm",
        "xgboost": "xgboost",
        "lightgbm": "lightgbm",
        "catboost": "catboost",
        "torch": "torch",
    }
    print(f"Python executable: {PYTHON}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Package root: {PACKAGE_ROOT}")
    print(f"Repository root: {REPO_ROOT or 'NOT DETECTED'}")
    print("Python dependencies:")
    for label, import_name in python_modules.items():
        print(f"  {label}: {_module_status(import_name)}")
    print("External tools:")
    for tool, args in external_tools.items():
        print(f"  {tool}: {_tool_version(tool, args)}")
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
        "--model-path",
        help=(
            "Override the default retained model artifact path. "
            "See docs/models.md for availability and storage policy."
        ),
    )
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
