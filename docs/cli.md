# CLI

Available commands:

- `mitochime extract-features`
- `mitochime build-dataset`
- `mitochime split`
- `mitochime train-classical`
- `mitochime train-cnn`
- `mitochime train-bigru`
- `mitochime filter --mode {gb,cnn,bigru}`
- `mitochime validate-pairs`
- `mitochime validate-models`
- `mitochime report-environment`

The CLI is intentionally thin. It only exposes commands backed by verified code paths from this cleanup pass.

Notes:

- `mitochime filter --mode {gb,cnn,bigru}` now accepts `--model-path` to override the default canonical artifact location.
- `mitochime validate-models` verifies the tracked canonical GB, CNN, and BiGRU checkpoints against the JSON checksum manifest and runs a tiny deterministic smoke prediction for each family.
- `mitochime report-environment` reports both Python dependency availability and external bioinformatics tool availability without crashing when tools are absent.
- Base installation is sufficient for CLI help, pair-integrity validation, and lightweight example checks.
