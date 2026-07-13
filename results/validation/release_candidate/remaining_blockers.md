# Remaining blockers

## Researcher decisions still required

- `LICENSE` is still a placeholder. Decide the actual software license before describing the repository as open source.
- Decide whether to track the tested `gradient_boosting_tuned.joblib` artifact directly in Git. It is only about 501 KB and loaded successfully in the release-candidate environment, but it was not committed automatically.
- Decide the public release locations for the canonical CNN and BiGRU checkpoints. The manifests now describe them clearly, but tracked clones still do not contain the `.pt` files.
- Confirm redistribution policy for the retained mitochondrial reference accession `NC_039553.1` and for the unresolved external FASTQ datasets.

## Repository-surface review still recommended before pushing

- Review the large tracked archive and manuscript files listed in `results/validation/release_candidate/large_tracked_files.tsv`. The biggest files are archival PDFs and legacy datasets rather than canonical runtime assets.
- Decide whether large archived PDFs and legacy datasets should remain in the GitHub repository, move to a release attachment, or move to an external archive.
- Decide whether final SPAdes assembly outputs and external-test FASTQs will stay external-only or receive a documented archive location.

## Current technical status

- Fresh clones now install successfully with `python -m pip install .`.
- CLI help, example `validate-pairs`, `make validate-pairs`, editable install, wheel build, wheel install, and `pytest -q` all passed in the release-candidate validation.
- Tracked clones still fail real inference by design because trained model binaries are not included; the failure path is now explicit and points users to `docs/models.md`.
