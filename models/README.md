# Model Policy

This repository does not treat large trained model binaries as primary source artifacts.

- canonical model metadata belong in `models/metadata/`
- fresh Git clones retain model metadata and feature-schema files, but not the trained `.joblib` or `.pt` binaries
- local checkpoints may still exist on disk for reruns
- duplicate or non-canonical model trees have been moved under `archive/`
- canonical availability, checksums, and storage guidance are recorded in `models/MODEL_MANIFEST.tsv`
