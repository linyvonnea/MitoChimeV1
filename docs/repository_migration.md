# Repository Migration

This cleanup pass converted the disposable duplicate working tree into a publication-oriented repository shape.

Highlights:

- promoted the pair-safe canonical workflow into `src/`, `scripts/`, `results/`, and `docs/`
- archived legacy scripts, thesis material, and duplicate bundles under `archive/`
- repaired the broken deep-training wrapper by removing references to the missing `dl_rnn.py`
- introduced authoritative read-ID and feature-schema helpers
- added validation scripts and focused tests

See [MIGRATION_REPORT.md](../MIGRATION_REPORT.md) for the detailed record.
