# Validation Report

## Intended Checks

- `python3 -m compileall src scripts tests`
- `python3 -m pip install -e .`
- `pytest -q`
- CLI `--help`
- pair-integrity report generation

## Notes Before Validation

- The system `python3` environment in this working tree initially failed to import `pandas` because of a local environment issue unrelated to repository source layout.
- For data-inspection and integrity-report generation during cleanup, the bundled Codex runtime Python was used with `PYTHONPATH=src`.

## Executed During Cleanup

- Pair-integrity reports:
  - `PYTHONPATH=src <bundled-python> scripts/validation/validate_pair_integrity.py --feature-dataset data/processed/PAIR_train.tsv --sequence-dataset data/processed/PAIR_train_seq_L150.tsv --split-dataset data/processed/PAIR_train.tsv --report-json results/validation/pair_integrity_train.json`
  - `PYTHONPATH=src <bundled-python> scripts/validation/validate_pair_integrity.py --feature-dataset data/processed/PAIR_test.tsv --sequence-dataset data/processed/PAIR_test_seq_L150.tsv --split-dataset data/processed/PAIR_test.tsv --report-json results/validation/pair_integrity_test.json`

## Result

Executed successfully in the bundled Codex runtime:

- `python3 -m compileall src scripts tests`
- `python3 -m pip install -e .`
- `python3 -m mitochime.cli --help`
- `pytest -q`

Observed outcomes:

- editable install succeeded
- CLI help rendered correctly
- `pytest -q` passed with `11 passed`
- pair-integrity JSON reports were written for both train and test publication datasets

Remaining caveat:

- the independent validation pass should still repeat these checks in the target release environment rather than relying only on the cleanup runtime.
