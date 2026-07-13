# Validation Report

## Executive assessment

- Validation level: independent fresh-clone audit completed against `publication/nids-cleanup` commit `3b7685a9c82f3be3eb89b0a01dffdd52ac88cb19`, followed by a limited post-review recheck of narrow local fixes in the current working tree.
- Public-release readiness: `FAIL`
- Most important successes:
  - fresh clone creation, non-editable install, editable install, wheel build, and wheel reinstall all succeeded
  - `python -m compileall src scripts tests` succeeded
  - the retained unit test suite passed after explicitly installing `pytest`
  - independent pair-integrity regeneration for `PAIR_train.tsv` and `PAIR_test.tsv` exactly matched the tracked JSON reports
  - retained classical and deep metric artifacts are present and traceable to named scripts and datasets
- Most important blockers:
  - `LICENSE` is still a placeholder, so public release remains blocked
  - the fresh clone does not contain the canonical trained model binaries under `models/`; only metadata and feature-column JSON are tracked
  - the original reviewed branch state had a broken README quick start and `make validate-pairs` path resolution failure from a non-editable install
  - active documentation and notebooks still contain portability issues such as personal absolute paths, stale pre-cleanup paths, or references to untracked model/output locations
  - full publication reproduction remains blocked by absent external FASTQ assets, absent external bioinformatics tools, and ignored large assembly/model artifacts

## Validation matrix

| Check | Status | Command or method | Evidence | Required action |
| --- | --- | --- | --- | --- |
| 1. Git state | `PARTIAL` | `git status`, `git branch`, `git log`, `git ls-files`, hygiene scans | `results/validation/independent/git-state.txt`, `repo-hygiene.txt`, `large-files.txt` | Original branch was clean before audit outputs, but tracked cache/build artifacts and large archival PDFs remain in Git. |
| 2. Fresh clone | `PASS` | `git clone --no-local . "$tmpdir/MitoChime-release-check"` | `tmpdir.txt`, `fresh-clone-git-state.txt` | None for cloning itself. |
| 3. Clean environment | `PASS` | `python3 -m venv`, `python --version`, `pip --version` | `tmpdir.txt`, `commands.log` | Keep system-Python validation as the primary release check. |
| 4. Non-editable installation | `PASS` | `python -m pip install .` | `fresh-clone-install.txt` | None for installation itself. |
| 5. Editable installation | `PASS` | `python -m pip install -e .` | `editable-install.txt` | None for installation itself. |
| 6. Wheel/sdist build | `PASS` | `python -m pip install build`, `python -m build` | `build-install.txt`, `package-build.txt`, `dist-contents.txt` | Keep validating release artifacts before publication. |
| 7. Package imports | `PARTIAL` | direct import audit of canonical modules | `import-summary.txt` | Core imports work, but classical/deep training modules require optional `xgboost` or `torch`; document this boundary clearly. |
| 8. CLI | `PARTIAL` | root help, subcommand help, quick-start commands | `cli-root-help.txt`, `cli-subcommands.txt`, `readme-*.txt`, `postfix-*.txt` | Original branch state failed `validate-pairs` from a non-editable install; local CLI fix now restores repository-root execution, but non-checkout wheel-only use remains limited. |
| 9. Makefile | `PARTIAL` | `make help`, `make report-environment`, `make validate-pairs` | `make-help.txt`, `make-report-environment.txt`, `make-validate-pairs.txt`, `postfix-make-*.txt` | Original branch state had a broken `validate-pairs` target; local fix now works, but model-training targets still depend on ignored local model/tool ecosystems. |
| 10. Unit tests | `PARTIAL` | `pytest -q` | `pytest-summary.txt`, `postfix-pytest.txt` | Tests pass, but `pytest` is not installed by default in the clean runtime environment. |
| 11. Pair-safe behavior | `PARTIAL` | test inspection plus filtering helper review | `tests/test_filtering.py`, `tests/test_build_pair_splits.py` | Core pair retention and split isolation are covered, but one-mate-positive/orphan edge cases are still lightly tested. |
| 12. Pair-integrity reports | `PASS` | regenerate train/test reports from fresh clone | `pair-integrity-train.txt`, `pair-integrity-test.txt`, `pair-integrity-compare.txt` | None for the retained reports. |
| 13. Feature schema | `PARTIAL` | compare canonical schema, JSON feature lists, retained datasets | `feature-schema-compare.txt`, `example-schema-check.txt` | Canonical 24-feature schema is consistent with `feature_cols_24.json`, but `PAIR_feature_cols.json` still carries an older 23-feature order without `strand`. |
| 14. Classical-model loading | `FAIL` | inspect fresh clone `models/` contents | `fresh-clone-model-files.txt`, `fresh-clone-tracked-model-files.txt`, `model-artifacts.txt` | Canonical tuned model binaries are absent from the fresh clone and exist only as ignored local files. |
| 15. CNN artifacts | `PARTIAL` | inspect tracked clone vs ignored local files | `fresh-clone-model-files.txt`, `model-artifacts.txt`, `ignored-untracked-files.txt` | Metrics are tracked, but the final CNN checkpoint is not in the fresh clone. |
| 16. BiGRU artifacts | `PARTIAL` | inspect tracked clone vs ignored local files | `fresh-clone-model-files.txt`, `model-artifacts.txt`, `ignored-untracked-files.txt` | Metrics are tracked, but the final BiGRU checkpoint is not in the fresh clone. |
| 17. Example workflow | `PARTIAL` | exact README quick start | `readme-report-environment.txt`, `readme-validate-pairs.txt`, `postfix-report-environment.txt`, `postfix-validate-pairs.txt` | Original branch state failed; local working-tree fix now makes the quick start succeed from the repository root. |
| 18. Lightweight inference | `FAIL` | attempted model availability check from fresh clone | `fresh-clone-model-files.txt`, `fresh-clone-tracked-model-files.txt` | No trained model binary is available in the fresh clone, so real inference cannot be reproduced from tracked files alone. |
| 19. Notebooks | `FAIL` | static audit of `notebooks/publication/*.ipynb` | `notebook-audit.txt`, `active-portability-scan.txt` | Several publication notebooks lack a descriptive first markdown cell and retain personal paths or stale model references. |
| 20. External tools | `NOT_RUN` | PATH/version checks and `report-environment` | `external-tools.txt`, `make-report-environment.txt`, `postfix-report-environment.txt` | Install and document `minimap2`, `samtools`, `seqkit`, `spades.py`, `GetOrganelle`, and `wgsim` in the intended release environment. |
| 21. Result provenance | `PARTIAL` | inspect tracked metrics/tables and provenance docs | `docs/audit/RESULTS_PROVENANCE.md`, `fresh-clone-results-files.txt` | Many metrics are traceable, but some tracked result JSON still points to legacy `reports/` or untracked `models/`/`data/assemblies_spades/` paths. |
| 22. Data availability | `PARTIAL` | inspect tracked `data/` families and manifests | `docs/audit/DATASET_INVENTORY.md`, `retained_files.csv`, `unresolved_files.csv` | Core processed pair datasets are tracked; external FASTQs remain unresolved and are not included. |
| 23. Large-artifact policy | `PARTIAL` | inspect `.gitignore`, tracked files, ignored local assets | `.gitignore`, `large-files.txt`, `ignored-untracked-files.txt`, `models/README.md` | Separate release manifests/assets are still needed for model binaries and large assembly outputs. |
| 24. Licensing | `FAIL` | inspect `LICENSE` and README | `LICENSE`, `README.md` | Choose an actual release license before public distribution. |
| 25. Citation metadata | `PARTIAL` | inspect `CITATION.cff`, `AUTHORS.md`, README | `CITATION.cff`, `AUTHORS.md` | Metadata is syntactically plausible but still lacks DOI/release URL and final publication identifiers. |
| 26. Documentation | `PARTIAL` | inspect active docs, links, and commands | `active-portability-scan.txt`, `README.md`, `docs/*.md` | Local fixes removed the most visible absolute links, but active docs and notebooks still contain stale paths and over-optimistic assumptions about asset availability. |
| 27. Secrets and portability | `PARTIAL` | targeted scans for active code/docs plus path scan | `secrets-scan-active.txt`, `path-scan.txt`, `active-portability-scan.txt` | No obvious secrets were found in active code/docs, but portability issues remain in notebooks and some active scripts. |
| 28. Public-release simulation | `FAIL` | README-driven fresh-clone walkthrough | `fresh-clone-install.txt`, `readme-*.txt`, `fresh-clone-model-files.txt` | A new researcher can install and inspect the package, but cannot fully run the claimed inference/release workflow from tracked files alone. |
| 29. Full publication reproduction | `FAIL` | synthesis of code/data/tool/model checks | this report plus `UNRESOLVED_QUESTIONS.md` | External FASTQs, external tools, missing trained binaries, and unresolved licensing prevent a full public NiDS reproduction claim. |

## Commands executed

The full command log with working directory, command, exit code, and concise result is stored at:

- `results/validation/independent/commands.log`

Supporting evidence files are stored under:

- `results/validation/independent/git-state.txt`
- `results/validation/independent/fresh-clone-git-state.txt`
- `results/validation/independent/tracked-files.txt`
- `results/validation/independent/large-files.txt`
- `results/validation/independent/repo-hygiene.txt`
- `results/validation/independent/path-scan.txt`
- `results/validation/independent/fresh-clone-install.txt`
- `results/validation/independent/editable-install.txt`
- `results/validation/independent/package-build.txt`
- `results/validation/independent/dist-contents.txt`
- `results/validation/independent/wheel-install.txt`
- `results/validation/independent/compileall.txt`
- `results/validation/independent/import-summary.txt`
- `results/validation/independent/cli-subcommands.txt`
- `results/validation/independent/make-help.txt`
- `results/validation/independent/make-report-environment.txt`
- `results/validation/independent/make-validate-pairs.txt`
- `results/validation/independent/pytest-summary.txt`
- `results/validation/independent/pair-integrity-train.txt`
- `results/validation/independent/pair-integrity-test.txt`
- `results/validation/independent/pair-integrity-compare.txt`
- `results/validation/independent/model-artifacts.txt`
- `results/validation/independent/fresh-clone-model-files.txt`
- `results/validation/independent/notebook-audit.txt`
- `results/validation/independent/external-tools.txt`
- `results/validation/independent/postfix-install.txt`
- `results/validation/independent/postfix-report-environment.txt`
- `results/validation/independent/postfix-validate-pairs.txt`
- `results/validation/independent/postfix-make-validate-pairs.txt`
- `results/validation/independent/postfix-pytest.txt`

## Release-candidate remediation

Release-candidate remediation was validated from a new temporary clone of commit `e27857f4a9ccd7f06f0aa28c13c5fe13e078f339` on `publication/nids-cleanup`. Evidence is stored under `results/validation/release_candidate/`.

| Previous blocker | Remediation | Current status | Remaining action |
| --- | --- | --- | --- |
| `LICENSE` is still a placeholder | Left licensing unchanged as instructed, but carried the unresolved decision into `RELEASE_CHECKLIST.md` and `results/validation/release_candidate/remaining_blockers.md`. | `OPEN` | Researcher must choose the actual software license before public release messaging can be finalized. |
| Fresh clone lacked canonical trained model binaries | Added `models/MODEL_MANIFEST.tsv`, clarified `docs/models.md`, tested the local GB artifact, and hardened the CLI/Bash wrappers so missing tracked models fail cleanly with model-family and override guidance. | `PARTIALLY_RESOLVED` | Decide final public storage for GB, CNN, and BiGRU artifacts. |
| README quick start and `make validate-pairs` previously failed from a clean install | Repository-root CLI detection was already fixed in the earlier remediation commit; release-candidate fresh-clone validation now confirms base install, quick-start validation, and `make validate-pairs` all succeed. | `RESOLVED` | None. |
| Active docs and notebooks still had portability issues | Normalized publication notebook paths, removed saved machine-specific outputs, added intro cells, updated notebook inventory, repaired canonical result-path references, and refreshed public-facing docs. | `RESOLVED` | Keep archived audit/manuscript material clearly separated from the canonical release surface. |
| Result metadata still pointed to stale `reports/` or duplicate model paths | Added canonical repository metadata to promoted metrics JSON files and refreshed `docs/audit/RESULTS_PROVENANCE.md`. | `RESOLVED` | None for tracked promoted metrics. |
| Reference FASTA portability was ambiguous because `mt_ref.fasta` was a symlink | Replaced the symlink with a regular tracked FASTA copy, added checksum/accession details, and documented it in `data/manifests/DATA_ARTIFACT_MANIFEST.tsv`. | `RESOLVED` | Researcher should still confirm redistribution rights for accession `NC_039553.1`. |
| Optional dependency boundaries were under-documented | Added optional-dependency guidance to the CLI and docs, pinned release-compatible base dependencies in `pyproject.toml`, and verified that base install works without `xgboost`, `catboost`, `lightgbm`, or `torch`. | `RESOLVED` | None for the base package path. |
| Full publication reproduction was overstated or underspecified | Updated README, reproducibility docs, manifests, and validation evidence to distinguish smoke-tested clone behavior from model-dependent and external-data-dependent reproduction. | `RESOLVED` | External FASTQ policy, assembly-output policy, and final archive locations remain researcher decisions. |
| Large tracked archival files had not been reviewed for GitHub release suitability | Added `results/validation/release_candidate/large_tracked_files.tsv` classifying the 30 largest tracked files. | `PARTIALLY_RESOLVED` | Researcher should review whether large archived PDFs and legacy datasets stay in Git, move to a release asset, or move to an external archive. |

### Release-candidate validation results

- Validation level: `Level 3 — Partially reproducible`
- Release decision: `READY_AFTER_MINOR_FIXES`

### Release-candidate evidence summary

- `python -m pip install .`: passed
- `python -m pip install -e ".[dev]"`: passed
- `python -m compileall src scripts tests`: passed
- `python -m mitochime.cli --help`: passed
- `python -m mitochime.cli report-environment`: passed
- `pytest -q`: passed (`12 passed`)
- `python -m build`: passed
- wheel installation plus CLI help: passed
- README quick start (`validate-pairs` on example data): passed
- `make validate-pairs`: passed
- canonical feature-schema comparison: passed (`feature_cols_24.json` matches the 24-feature canonical order; legacy `PAIR_feature_cols.json` remains 23-feature provenance)
- missing-model behavior in a fresh clone: passed as an expected controlled failure with explicit guidance to `docs/models.md`
- notebook portability scan over publication notebook source cells: passed
