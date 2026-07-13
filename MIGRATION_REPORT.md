# Migration Report

## Scope

This pass converted the disposable duplicate repository into a publication-oriented working tree centered on the pair-aware, pair-safe, no-quality MitoChime workflow.

## Major Changes

- Established a real repository baseline with `chore: capture pre-cleanup source snapshot`.
- Created and switched to `publication/nids-cleanup`.
- Replaced the stub CLI with a thin executable interface exposing only verified commands.
- Moved operational scripts out of `src/scripts/` into `scripts/`.
- Added authoritative read-ID and feature-schema utilities under `src/mitochime/`.
- Repaired deep training by removing references to the missing `dl_rnn.py` implementation.
- Promoted publication-facing outputs into `results/`.
- Moved thesis, defense, draft, duplicate, and review-needed material into `archive/`.
- Added integrity validation, example data, and focused tests.

## Canonical Workflow After Cleanup

- Tabular pair-safe branch:
  - `scripts/data_prep/extract_features.py`
  - `python -m mitochime.cli build-dataset`
  - `python -m mitochime.cli split`
  - `python -m mitochime.make_noq_datasets_pair`
  - `python -m mitochime.cli train-classical`
- Deep branch:
  - `python -m mitochime.deep_learning.make_seq_tsv`
  - `python -m mitochime.cli train-cnn`
  - `python -m mitochime.cli train-bigru`
- Filtering branch:
  - `bash scripts/inference/run_pipeline_gb.sh ...`
  - `bash scripts/inference/run_pipeline_cnn.sh ...`
  - `bash scripts/inference/run_pipeline_rnnkmer.sh ...`
- Assembly branch:
  - `bash scripts/assembly/run_spades.sh ...`

## Duplicate Resolution

- `models_pair_noq_tuned/` was treated as the canonical tuned Gradient Boosting artifact directory and moved to `models/pair_noq_tuned/`.
- `models_PAIR_noq_tuned/` remained a duplicate and was moved into `archive/duplicate_bundles/`.
- The Kaggle bundle and ZIP were removed from the active repository surface and placed under `archive/duplicate_bundles/`.

## Deep-Training Repair

- `train_deep.py` no longer imports the missing `dl_rnn.py`.
- Unsupported base-level RNN modes were removed from the exposed training interface.
- Verified retained training modes are `cnn`, `rnn_kmer_gru`, and optional `transformer`.

## Data Integrity Handling

- Added `scripts/validation/validate_pair_integrity.py`.
- Generated machine-readable pair-integrity reports in `results/validation/`.
- Preserved the publication datasets without filling or deleting the 15 incomplete feature-derived pairs.

## Remaining Limits

- External FASTQ release policy remains unresolved.
- Notebook intro-cell normalization was not completed in this pass.
- Large model binaries and assembly outputs remain local assets, not curated release artifacts.
- A separate independent validation pass is still required.

