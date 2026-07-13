# Models

Canonical inference families:

- tuned Gradient Boosting for pair-safe tabular inference
- CNN1D for one-hot sequence inference
- BiGRU k-mer for tokenized sequence inference

Tracked clones keep:

- model metadata under `models/metadata/`
- retained feature-schema JSON files under `models/pair_noq_tuned/`
- release policy and checksums in [models/MODEL_MANIFEST.tsv](../models/MODEL_MANIFEST.tsv)

Tracked clones do not currently keep trained `.joblib` or `.pt` binaries.

Model-specific notes:

- Gradient Boosting is the canonical tabular inference model used by `scripts/inference/run_pipeline_gb.sh`.
- CNN1D and BiGRU are canonical sequence-based comparison and filtering models, but their checkpoints remain local-only in this working tree.
- Comparison-only tuned classical models remain useful for publication tables, but they are not required for the lightweight example workflow.

Override behavior:

- `python3 -m mitochime.cli filter --mode gb --model-path /path/to/gradient_boosting_tuned.joblib`
- `python3 -m mitochime.cli filter --mode cnn --model-path /path/to/cnn_final.pt`
- `python3 -m mitochime.cli filter --mode bigru --model-path /path/to/rnn_kmer_gru_best.pt`
- Bash wrappers also accept `GB_MODEL`, `CNN_MODEL`, and `RNN_MODEL`.

Availability, checksums, expected inputs, and release recommendations are recorded in [models/MODEL_MANIFEST.tsv](../models/MODEL_MANIFEST.tsv).
