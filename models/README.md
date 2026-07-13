# Model Policy

This repository does not treat large trained model binaries as primary source artifacts.

- canonical model metadata belong in `models/metadata/`
- fresh Git clones retain model metadata, feature lists, and hashes, but not the large `.joblib` or `.pt` binaries
- local checkpoints may still exist on disk for reruns
- duplicate or non-canonical model trees have been moved under `archive/`
