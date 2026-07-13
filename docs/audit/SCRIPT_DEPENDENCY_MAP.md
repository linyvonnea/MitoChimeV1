# Script Dependency Map

## High-level workflow map

```mermaid
flowchart TD
    A["`data/refs/original.fasta`"] --> B["`src/scripts/make_chimeric_templates.py`"]
    A --> C["`src/scripts/simulation.py`"]
    B --> C
    C --> D["`data/interim/alignments/*.bam|*.sam`"]
    D --> E["`src/scripts/extract_features.py`"]
    E --> F["`data/features/v1/*.tsv`"]
    F --> G["`src/mitochime/build_datasets.py`"]
    G --> H["`data/processed/all_reads.tsv`"]
    H --> I["`src/mitochime/build_pair_splits.py`"]
    I --> J["`data/processed/PAIR_train.tsv`"]
    I --> K["`data/processed/PAIR_test.tsv`"]
    G --> L["`src/mitochime/make_noq_datasets.py`"]
    I --> M["`src/mitochime/make_noq_datasets_pair.py`"]
    L --> N["`train_noq.tsv` + `test_noq.tsv`"]
    M --> O["`PAIR_train_noq.tsv` + `PAIR_test_noq.tsv`"]
    O --> P["`src/mitochime/train_all_models.py`"]
    O --> Q["`src/mitochime/hyperparam_search_top.py`"]
    J --> R["`src/mitochime/deep_learning/make_seq_tsv.py`"]
    K --> R
    R --> S["`PAIR_*_seq_L150.tsv` + `PAIR_*_seq_L300.tsv`"]
    S --> T["`src/mitochime/deep_learning/make_folds.py`"]
    S --> U["`src/mitochime/deep_learning/train_deep.py`"]
    T --> U
    P --> V["`reports/metrics*` + baseline models"]
    Q --> W["tuned models + `reports/hparam_tuning*`"]
    U --> X["deep checkpoints + `reports/deep/*`"]
```

## Inference and filtering map

```mermaid
flowchart TD
    A["Input FASTQ pair"] --> B["`run_pipeline_gb.sh`"]
    A --> C["`run_pipeline_cnn.sh`"]
    A --> D["`run_pipeline_rnnkmer.sh`"]

    B --> B1["`minimap2` + `samtools`"]
    B1 --> B2["`extract_features.py`"]
    B2 --> B3["`gb_predict_filter_pairs.py`"]
    B3 --> B4["filtered FASTQ (GB)"]

    C --> C1["`dl_encode_fastq_R1_L150_4ch.py`"]
    C1 --> C2["`dl_predict_cnn.py`"]
    C2 --> C3["`filter_pairs_by_ids.py`"]
    C3 --> C4["filtered FASTQ (CNN)"]

    D --> D1["`mitochime.deep_learning.make_seq_tsv_infer`"]
    D1 --> D2["`mitochime.deep_learning.predict_deep`"]
    D2 --> D3["`filter_pairs_by_ids.py`"]
    D3 --> D4["filtered FASTQ (BiGRU)"]

    B4 --> E["`run_spades.sh`"]
    C4 --> E
    D4 --> E
    A --> E
    E --> F["SPAdes assemblies + GFA"]
```

## Canonical script relationships

| Script / notebook | Direct dependencies | Produces | Notes |
| --- | --- | --- | --- |
| `src/scripts/make_chimeric_templates.py` | original FASTA | chimera FASTA | Called manually or from `simulation.py`. |
| `src/scripts/simulation.py` | `make_chimeric_templates.py`, `wgsim`, `minimap2`, `samtools`, `awk` | raw FASTQ plus alignment intermediates | Interactive and monolithic; likely earliest simulation implementation. |
| `src/scripts/extract_features.py` | sorted BAM | 30-column feature TSV | Canonical feature extraction step. |
| `src/mitochime/build_datasets.py` | clean/chimera feature TSVs | `all_reads.tsv`, `train.tsv`, `test.tsv` | Builds non-pair-aware tabular split first. |
| `src/mitochime/build_pair_splits.py` | `all_reads.tsv` | `PAIR_train.tsv`, `PAIR_test.tsv` | Pair-safe split based on base `read_id`. |
| `src/mitochime/make_noq_datasets_pair.py` | `PAIR_train.tsv`, `PAIR_test.tsv` | `PAIR_train_noq.tsv`, `PAIR_test_noq.tsv` | Final classical branch appears to use this dataset. |
| `src/mitochime/train_all_models.py` | `*_noq.tsv` or `PAIR_*_noq.tsv`, `data_utils.py`, `model_zoo.py` | baseline joblib models, metrics summaries | Generates `reports/metrics*`. |
| `src/mitochime/hyperparam_search_top.py` | pair/noq TSVs | tuned models, best-param JSON, tuned summary TSV | Generates `reports/hparam_tuning_*`. |
| `src/mitochime/deep_learning/make_seq_tsv.py` | pair split TSV + raw FASTQ | labeled sequence TSVs | Bridges pair split into deep-learning branch. |
| `src/mitochime/deep_learning/make_folds.py` | `PAIR_train_seq_L150.tsv` | fold assignment TSV | Pair-safe fold driver for deep CV. |
| `src/mitochime/deep_learning/train_deep.py` | sequence TSVs, model classes | deep checkpoints and reports | Currently blocked by missing `dl_rnn.py` import. |
| `src/scripts/run_pipeline_gb.sh` | reference FASTA, tuned GB model, `extract_features.py`, `gb_predict_filter_pairs.py` | feature TSV + filtered FASTQ | Canonical reference-guided inference path. |
| `src/scripts/run_pipeline_cnn.sh` | CNN checkpoint, `dl_encode_fastq_R1_L150_4ch.py`, `dl_predict_cnn.py`, `filter_pairs_by_ids.py` | encoded arrays, prediction TSV, filtered FASTQ | Canonical reference-free CNN inference path. |
| `src/scripts/run_pipeline_rnnkmer.sh` | BiGRU checkpoint, `make_seq_tsv_infer`, `predict_deep`, `filter_pairs_by_ids.py` | seq TSV, prediction TSV, filtered FASTQ | Canonical reference-free BiGRU inference path. |
| `src/scripts/run_spades.sh` | paired FASTQ, `spades.py` | SPAdes outputs | Canonical assembly wrapper for evaluation. |
| `src/scripts/run_final_all_t0p5.sh` | all three inference branches + SPAdes | final evaluation TSV and `final_run` assemblies | Best publication-facing batch evaluation script. |
| `notebooks/03_compare_tuned_vs_baseline_pair.ipynb` | `reports/metrics_pair_noq`, `reports/hparam_tuning_pair_noq`, tuned pair models | compare plots, feature-selection artifacts | Strong classical-results provenance notebook. |
| `notebooks/cnn_rnn_analysis.ipynb` | `reports/deep/*`, `reports/gb_vs_cnn_test.tsv` | deep-result summaries and figures | Strong DL provenance notebook. |
| `notebooks/05_spades_metrics_compare.ipynb` | `data/assemblies_spades/final_run`, `reports/final_run/eval_final_all_t0p5.tsv` | final assembly tables | Key assembly-results notebook. |

## Notebook-to-result dependencies

| Notebook | Main inputs | Main outputs / narrative role |
| --- | --- | --- |
| `notebooks/01_eda_pair.ipynb` | `data/processed/all_reads.tsv` | class-wise feature summaries and EDA plots used by chapter 4. |
| `notebooks/02_model_analysis_pair.ipynb` | `reports/metrics_pair_noq/metrics_summary.tsv` | baseline pair-noq performance plots. |
| `notebooks/03_compare_tuned_vs_baseline_pair.ipynb` | pair-noq metrics, tuned models, feature JSON | tuned-vs-baseline plots, permutation importance, feature-selection artifacts. |
| `notebooks/04_C4_pair.ipynb` | pair-noq metrics and tuned models | thesis/publication tables and figures. |
| `notebooks/cnn_rnn_analysis.ipynb` | `reports/deep/*`, `reports/gb_vs_cnn_test.tsv` | CNN/BiGRU held-out and CV figures plus summary comparison. |
| `notebooks/05_spades_metrics_compare.ipynb` | `data/assemblies_spades/final_run/*`, `reports/final_run/eval_final_all_t0p5.tsv` | final SPAdes comparison tables. |
| `notebooks/external_test.ipynb` | `data/assemblies_spades/final_run/*` | lower-level assembly/GFA inspection. |

## External command-line dependencies

| Tool | Used by | Purpose |
| --- | --- | --- |
| `wgsim` | `simulation.py` | Paired-end read simulation |
| `minimap2` | `simulation.py`, `run_pipeline_gb.sh` | Read alignment |
| `samtools` | `simulation.py`, `run_pipeline_gb.sh` | BAM/SAM conversion, sorting, indexing |
| `seqkit` | evaluation and filtering scripts | FASTQ statistics and filtering checks |
| `spades.py` | `run_spades.sh`, batch evaluation scripts | Assembly evaluation |
| `awk`, `gzip`, `sed`, `diff` | shell scripts | FASTQ and text processing |
| `torch` | deep-learning scripts | CNN/BiGRU/Transformer training and inference |
| `xgboost`, `lightgbm`, `catboost` | classical training/tuning scripts | Tuned classical model families |

## Broken or unresolved dependencies

| Location | Problem | Impact |
| --- | --- | --- |
| `src/mitochime/deep_learning/train_deep.py` | Imports missing `src/mitochime/deep_learning/dl_rnn.py` | Blocks rerunning deep training unless code is patched. |
| `src/mitochime/cli.py` + `Makefile` | CLI commands are stubs | The advertised top-level package interface is not the real workflow. |
| `src/scripts/run_batch_lemuru_spades.sh` | Assumes old GB output naming with `_gb` suffix | Legacy batch path is inconsistent with current `run_pipeline_gb.sh`. |
| `configs/*.yaml` | Match stub CLI only | Config layer is not wired into operational shell workflows. |
| `data/raw/*` references in comments | `data/raw/` directory is absent in current tree | Raw simulation FASTQ location is not preserved as a top-level source-data folder. |

## Likely duplicate workflows

- `run_batch_lemuru_all.sh` and `run_batch_lemuru_spades.sh` implement overlapping Lemuru threshold/assembly sweeps.
- `gb_predict_filter.py` and `06_predict_ml.py` are older non-pair-safe prediction paths superseded by `gb_predict_filter_pairs.py`.
- `dl_encode_fastq_pairs.py` overlaps with `dl_encode_fastq_R1_L150_4ch.py`.
- `kaggle_bundle_mitochime/src/mitochime` duplicates `src/mitochime`.
- `models_PAIR_noq_tuned/` duplicates `models_pair_noq_tuned/`.

## Audit conclusion

The repository has enough explicit dependencies to reconstruct the paper workflow, but the true operational path is the shell-script + processed-data layer, not the stub package CLI. Any cleanup should preserve that distinction until the working scripts are consolidated into a single documented interface.
