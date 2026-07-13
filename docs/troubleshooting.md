# Troubleshooting

- Missing `minimap2` or `samtools`: install the external bioinformatics tools described in the environment notes.
- Missing model artifact errors: use `--model-path` in the CLI or `GB_MODEL`, `CNN_MODEL`, `RNN_MODEL` in the Bash wrappers, then review `docs/models.md`.
- `torch` import failures: install the optional deep-learning dependency before using CNN or BiGRU commands.
- Missing `xgboost`, `lightgbm`, or `catboost`: install `python3 -m pip install ".[classical]"` before running the full classical comparison panel.
- Pair mismatch warnings: run `mitochime validate-pairs` and inspect the JSON report in `results/validation/`.
- Case-sensitive path failures: use `models/pair_noq_tuned/` instead of the former uppercase duplicate.
