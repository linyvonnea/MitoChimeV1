# Data Integrity

The original publication artifacts are preserved as-is, including a known mismatch between tabular and sequence-derived mate completeness.

Observed discrepancy:

- `all_reads.tsv` and downstream feature-derived pair splits contain 15 pair IDs with only one mate row.
- `PAIR_*_seq_L150.tsv` reconstruct both mates from FASTQ for those same pair IDs.

This cleanup pass does not repair or overwrite those publication datasets. Instead it adds:

- `scripts/validation/validate_pair_integrity.py`
- machine-readable validation outputs under `results/validation/`
- explicit documentation in the README and reproducibility notes

