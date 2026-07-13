# Model Policy

This repository tracks only the three canonical pretrained release artifacts needed for direct clone-and-run validation.

- canonical model metadata belong in `models/metadata/`
- fresh Git clones retain the tuned Gradient Boosting, CNN1D, and BiGRU k-mer checkpoints under their canonical paths
- comparison-only, debug, cross-validation, and duplicate model trees remain local-only or archived
- duplicate or non-canonical model trees have been moved under `archive/`
- canonical availability, checksums, and storage guidance are recorded in `models/MODEL_MANIFEST.tsv`
- `python3 -m mitochime.cli validate-models` verifies the tracked artifacts against `models/metadata/canonical_model_artifacts.json`
