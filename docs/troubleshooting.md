# Troubleshooting

- Missing `minimap2` or `samtools`: install the external bioinformatics tools described in the environment notes.
- `torch` import failures: install the optional deep-learning dependency before using CNN or BiGRU commands.
- Pair mismatch warnings: run `mitochime validate-pairs` and inspect the JSON report in `results/validation/`.
- Case-sensitive path failures: use `models/pair_noq_tuned/` instead of the former uppercase duplicate.

