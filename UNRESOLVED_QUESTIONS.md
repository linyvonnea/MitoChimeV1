# Unresolved Questions

## Scientific Methodology

- Was the final classical-model branch for the paper definitively `PAIR_train_noq.tsv` / `PAIR_test_noq.tsv`, or were any reported results taken from the non-pair `train_noq.tsv` / `test_noq.tsv` branch?
- Should `strand` be part of the canonical tuned pair-noq feature set? Both `feature_cols_24.json` and `PAIR_feature_cols.json` exist, and they differ on whether `strand` is included.
- Was the final CNN intentionally fixed at `25` epochs (`cnn_final_L150_seed42_fixedep25`) despite the presence of a separate non-fixed final run?
- Is the transformer branch part of the intended publication scope, or should it be archived as exploratory/appendix-only material?

## Canonical Scripts

- Which Lemuru batch driver is authoritative: `src/scripts/run_batch_lemuru_all.sh` or `src/scripts/run_batch_lemuru_spades.sh`?
- Are `src/scripts/run_final_all_t0p5.sh` and `reports/final_run/*` the definitive assembly-evaluation path, or do any results in the manuscript depend on older `data/assemblies/*` runs?
- Should the final publication interface expose the shell workflows directly, or should the package CLI be upgraded to wrap them?

## Datasets

- What is the authoritative source and licensing status of `data/external_test/*` FASTQ datasets?
- Why are 15 mate rows missing from `all_reads.tsv` / feature-table derivatives while the deep sequence TSVs reconstruct full pairs from FASTQ?
- Are the `L300` sequence datasets part of the publication record, or can they be archived as earlier deep-learning experiments?

## Models

- Do you want to release all trained models, or only the final tuned Gradient Boosting, final CNN, and final BiGRU checkpoints?
- Which of the duplicate tuned-model directories should survive: `models_pair_noq_tuned/` or `models_PAIR_noq_tuned/`?
- Are the older BiLSTM checkpoints in `models/deep/bilstm_*` scientifically relevant, or only historical experiments?

## Notebooks

- Which notebook set is canonical for publication figures and tables: the `*_pair.ipynb` notebooks only, or both pair and non-pair variants?
- Should `mitochime_local_lab_runs.ipynb` be included as supplementary reproducibility material, or archived as internal lab support?
- Are `notebooks/test/test.ipynb` and the `notebooks/reports/*` compare-table derivatives meant to be retained in the release repo?

## Results

- Which assembly summary files are canonical: `reports/final_*` or `notebooks/reports/compare_tables/*`?
- Should the final release retain both the raw per-run assembly outputs and the condensed summary tables, or only the latter plus manifests?
- Are the perfect-score `reports/metrics_pair/metrics_summary.tsv` results intentionally retained for historical comparison, or should they be excluded from the publication repository as non-canonical?

## Environment

- What is the officially supported reproduction target: Linux only, macOS ARM, or both?
- Do you want one environment manifest for publication, or separate manifests for classical-only, deep-learning, and assembly workflows?
- Should the final release require `seqkit`, `spades.py`, `minimap2`, `samtools`, and `wgsim` locally, or should large downstream evaluation steps be documented as optional?

## Publication Scope

- Is the release intended to cover only the Springer/NiDS paper workflow, or also thesis-era appendices, defense slides, and supplementary exploratory analyses?
- Should the defense deck under `documentation/defense/` remain in the main repository, or move to an archive/supporting-materials area?
- Is the Kaggle deep-learning bundle meant to be shipped as part of the main repository or as a separate companion release asset?

## Licensing

- What license should govern the code?
- Are the processed datasets, trained models, and assembly outputs releasable under the same license as the code?

## External Data Hosting

- Where should large assets live in the final publication package: Git LFS, Zenodo, Kaggle, institutional storage, or a mixed strategy?
- Do you want checksums and manifests for external FASTQ datasets, model bundles, and assembly outputs in the cleaned repository?
