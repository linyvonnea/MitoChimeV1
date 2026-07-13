# Models

Canonical inference families:

- tuned Gradient Boosting for pair-safe tabular inference
- CNN1D for one-hot sequence inference
- BiGRU k-mer for tokenized sequence inference

Tracked clones keep:

- the canonical tuned Gradient Boosting checkpoint at `models/pair_noq_tuned/gradient_boosting_tuned.joblib`
- the canonical CNN1D checkpoint at `models/deep/cnn_final_L150_seed42_fixedep25/cnn_final.pt`
- the canonical BiGRU k-mer checkpoint at `models/deep/rnnkmer_bigru_final_L150_seed42/rnn_kmer_gru_best.pt`
- model metadata under `models/metadata/`
- retained feature-schema JSON files under `models/pair_noq_tuned/`
- release policy and checksums in [models/MODEL_MANIFEST.tsv](../models/MODEL_MANIFEST.tsv)

Model-specific notes:

- Gradient Boosting is the canonical tabular inference model used by `scripts/inference/run_pipeline_gb.sh`.
- CNN1D and BiGRU are canonical sequence-based comparison and filtering models and are now tracked directly in Git.
- Comparison-only tuned classical models remain useful for publication tables, but they are not required for the lightweight example workflow.
- Non-canonical debug, cross-validation, and duplicate checkpoints remain untracked on purpose.

Override behavior:

- `python3 -m mitochime.cli filter --mode gb --model-path /path/to/gradient_boosting_tuned.joblib`
- `python3 -m mitochime.cli filter --mode cnn --model-path /path/to/cnn_final.pt`
- `python3 -m mitochime.cli filter --mode bigru --model-path /path/to/rnn_kmer_gru_best.pt`
- Bash wrappers also accept `GB_MODEL`, `CNN_MODEL`, and `RNN_MODEL`.

Validation behavior:

- `python3 -m mitochime.cli validate-models` checks that the three tracked canonical checkpoints are present at their default paths.
- The command recomputes SHA-256 digests against `models/metadata/canonical_model_artifacts.json`, loads each model, validates its expected input schema or shape, and runs a small smoke prediction from `data/example/`.
- The same default artifact paths are used by `mitochime filter --mode {gb,cnn,bigru}` unless you override them with `--model-path` or the corresponding environment variable.

Availability, checksums, expected inputs, and release recommendations are recorded in [models/MODEL_MANIFEST.tsv](../models/MODEL_MANIFEST.tsv).
