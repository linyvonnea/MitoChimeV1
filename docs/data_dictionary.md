# Data Dictionary

Key dataset families:

- `all_reads.tsv`: merged labeled feature table
- `PAIR_train.tsv`, `PAIR_test.tsv`: pair-aware split with full raw feature columns
- `PAIR_train_noq.tsv`, `PAIR_test_noq.tsv`: canonical classical-model datasets
- `PAIR_train_seq_L150.tsv`, `PAIR_test_seq_L150.tsv`: canonical deep-learning datasets

Important identifiers:

- `read_id`: read-level ID, often ending in `/1` or `/2`
- pair/base ID: normalized `read_id` without mate suffix
- `label`: `0` for clean, `1` for chimeric

