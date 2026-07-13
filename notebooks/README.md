# Notebooks

| Notebook | Purpose | Required inputs | Required models | Required tools | Publication output | Current execution status |
| --- | --- | --- | --- | --- | --- | --- |
| `publication/01_eda_pair.ipynb` | Exploratory summaries of the pair-aware feature dataset | `data/processed/all_reads.tsv` | none | none | feature summary table and EDA figures under `results/` | Not rerun in this remediation pass; normalized for repo-relative paths |
| `publication/02_model_analysis_pair.ipynb` | Review baseline pair-noq classical metrics | `results/metrics/classical/baseline_pair_noq/metrics_summary.tsv` | none | none | baseline metric plots | Not rerun in this remediation pass; expected to work from tracked metrics |
| `publication/03_compare_tuned_vs_baseline_pair.ipynb` | Compare tuned vs baseline classical models and feature ablations | processed pair-noq TSVs and retained classical metrics | tuned classical `.joblib` artifacts | optional `.[classical]` Python packages | ablation JSON/TSV artifacts and comparison plots | Requires local tuned model binaries; normalized but may remain non-executable in a fresh clone |
| `publication/04_C4_pair.ipynb` | Generate chapter-ready tables and classical comparison figures | processed pair-noq TSVs and retained metrics | tuned classical `.joblib` artifacts for ROC/PR cells | optional `.[classical]` Python packages | LaTeX tables and publication figures | Normalized to canonical paths; still depends on local tuned model binaries for some cells |
| `publication/cnn_rnn_analysis.ipynb` | Summarize CNN and BiGRU metrics and compare against tuned GB | retained deep metrics and tuned GB summary TSV | none for metric-only cells; deep checkpoints only if extended beyond retained outputs | optional plotting stack only | comparison tables and deep-learning figures | Not rerun in this remediation pass; normalized to canonical `results/` paths |
| `publication/05_spades_metrics_compare.ipynb` | Summarize final assembly comparison outputs | local assembly directories and retained final-evaluation TSVs | none | `spades.py` outputs must already exist locally | final assembly tables | Local-only because assembly outputs are not tracked |
| `publication/external_test.ipynb` | Inspect external-test assembly outputs and graph metrics | local external-test assembly directories | none | external assembly outputs must already exist locally | external-test summary TSVs | Local-only because required assemblies are not tracked |

Additional notes:

- `reproducibility/` contains lab rerun support material, not canonical publication notebooks.
- `archive/non_pair/` preserves older non-pair analyses.
- Notebook outputs should be treated as publication support material, not proof of fresh execution in a tracked clone.
