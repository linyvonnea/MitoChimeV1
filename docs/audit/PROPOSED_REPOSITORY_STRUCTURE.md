# Proposed Repository Structure

## Recommended target layout

```text
.
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── requirements.txt
├── environment.yml
├── environment.arm.yml
├── Makefile
├── src/
│   └── mitochime/
├── scripts/
│   ├── data_prep/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   └── assembly/
├── notebooks/
│   ├── publication/
│   ├── reproducibility/
│   └── archive/
├── data/
│   ├── refs/
│   ├── processed/
│   ├── example/
│   └── manifests/
├── models/
│   ├── released/
│   └── manifests/
├── results/
│   ├── metrics/
│   ├── figures/
│   ├── tables/
│   └── assembly/
├── docs/
│   ├── manuscript/
│   ├── defense/
│   ├── reproducibility/
│   └── audit/
└── archive/
    ├── legacy/
    ├── draft_docs/
    ├── duplicate_bundles/
    └── generated_large/
```

## Mapping from current tree

| Current location | Proposed destination | Rationale |
| --- | --- | --- |
| `src/mitochime/*` | `src/mitochime/*` | Keep package code as the core importable source tree. |
| `src/scripts/make_chimeric_templates.py`, `simulation.py`, `extract_features.py` | `scripts/data_prep/` | Separate simulation and feature-generation steps from model training. |
| `src/scripts/run_pipeline_gb.sh`, `run_pipeline_cnn.sh`, `run_pipeline_rnnkmer.sh`, helpers | `scripts/inference/` | These are the actual operational filtering pipelines. |
| `src/scripts/run_spades.sh` | `scripts/assembly/` | Single-purpose assembly wrapper. |
| `src/scripts/run_final_all_t0p5.sh`, threshold batch scripts | `scripts/evaluation/` | Keeps evaluation orchestration distinct from model inference. |
| `notebooks/*pair*.ipynb`, `cnn_rnn_analysis.ipynb`, `05_spades_metrics_compare.ipynb`, `external_test.ipynb` | `notebooks/publication/` | These are the strongest publication-facing notebooks. |
| `mitochime_local_lab_runs.ipynb` | `notebooks/reproducibility/` | Useful rerun notebook, but not a canonical paper notebook. |
| `notebooks/01_eda.ipynb`, `02_model_analysis.ipynb`, `03_compare_tuned_vs_baseline.ipynb`, `04_C4.ipynb` | `notebooks/archive/non_pair/` | Historical non-pair branch. |
| `data/refs/*` | `data/refs/` | Small, canonical reproducibility inputs. |
| `data/processed/*` | `data/processed/` | Core released processed datasets. |
| `data/external_test/*` | `data/example/` or external archive + `data/manifests/` | Depends on release rights and size strategy. |
| `models_pair_noq_tuned/*`, final deep checkpoints | `models/released/` | Keep only the canonical released models. |
| duplicate model dirs and debug checkpoints | `archive/duplicate_bundles/` or `archive/legacy/` | Avoid parallel model trees in the final repo. |
| `reports/*` | split into `results/metrics/`, `results/tables/`, `results/figures/` | Convert mixed report tree into publication-oriented outputs. |
| `data/assemblies_spades/final_run/*` | `results/assembly/final_run/` or external asset + manifest | High-value result artifacts, but bulky. |
| `data/assemblies/*`, `data/gb/*`, `data/dl/*`, `data/predictions/*`, `data/filtered_reads/*` | `archive/generated_large/` or external release asset | Generated run artifacts should not dominate the cleaned source repo. |
| `documentation/chapter_*.tex`, `documentation/main.tex`, bibliography | `docs/manuscript/` | Keep manuscript source distinct from code and results. |
| `documentation/defense/*` | `docs/defense/` | Optional supporting material. |
| `documentation/draft/*` | `archive/draft_docs/` | Historical draft set. |
| `kaggle_bundle_mitochime/` and `.zip` | `archive/duplicate_bundles/kaggle_bundle/` | Companion release only; avoid duplicate source tree in main repo. |

## Directory design principles

1. Keep importable code under `src/mitochime` and move shell workflows into a clearly documented `scripts/` tree.
2. Keep only one canonical copy of each model family, script family, and notebook family.
3. Treat `data/processed/` as the core reproducibility dataset layer.
4. Separate publication outputs (`results/`) from manuscript sources (`docs/manuscript/`).
5. Push large generated run outputs into `archive/` or an external release asset with manifests and checksums.

## Files that should likely be added in the cleanup phase

- `LICENSE`
- `CITATION.cff`
- a fuller `README.md`
- `.gitignore`
- optionally `.gitattributes` if Git LFS is used
- `data/README.md`
- `models/README.md`
- `results/README.md`

## What not to overcomplicate

- Do not introduce a workflow engine unless the researcher wants one.
- Do not split the package into many subpackages beyond the existing `deep_learning` boundary.
- Do not retain both the stub CLI and the shell pipelines as equal front doors.
- Do not keep duplicate upper/lowercase model directories or repeated bundled source trees in the final publication repo.
