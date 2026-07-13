# Canonical Workflow Proposal

## Proposed canonical execution order

| Stage name | Canonical source file | Input | Output | Key parameters | External dependency | Required for paper | Can currently be executed? | Competing or duplicate implementations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Reference preparation | `data/refs/original.fasta` plus `src/scripts/make_chimeric_templates.py` | Original mitochondrial FASTA | `chimera.fasta` | `--num-templates 1000`, `--template-len 300`, distance and microhomology bounds | None beyond Python stdlib | Yes for full simulation rerun | Yes | None obvious |
| 2. Read simulation and initial alignment | `src/scripts/simulation.py` | reference directory with original/chimera FASTA | `ref1.fastq`, `ref2.fastq`, `chime1.fastq`, `chime2.fastq`, `clean.sorted.bam`, `chimeric.sorted.bam` | read length 150, `NUM_READS=10000` in script, minimap2 short-read mapping | `wgsim`, `minimap2`, `samtools`, `awk`, `conda run` assumptions | Yes for raw-data regeneration | Partially | Script is interactive and monolithic; no cleaner batch equivalent exists yet |
| 3. Feature extraction | `src/scripts/extract_features.py` | sorted BAM | feature TSV | `--k 6`, `--micro-window 40` for main branch | `pysam`, `numpy` | Yes | Yes | None |
| 4. Merge clean/chimeric feature sets | `src/mitochime/build_datasets.py` | `clean_features_k6.tsv`, `chimera_features_k6.tsv` | `all_reads.tsv`, `train.tsv`, `test.tsv` | `--test-size 0.2`, `--random-state 42` | `pandas`, `scikit-learn` | Yes | Yes | None |
| 5. Pair-aware split | `src/mitochime/build_pair_splits.py` | `all_reads.tsv` | `PAIR_train.tsv`, `PAIR_test.tsv` | `--test-size 0.2`, `--random-state 42` | `pandas`, `scikit-learn` | Yes | Yes | None |
| 6. No-quality pair-safe dataset creation | `src/mitochime/make_noq_datasets_pair.py` | `PAIR_train.tsv`, `PAIR_test.tsv` | `PAIR_train_noq.tsv`, `PAIR_test_noq.tsv` | Drops `mean_base_quality`, `ref_start_1based` | `pandas` | Yes | Yes | `make_noq_datasets.py` for non-pair branch |
| 7. Baseline classical model training | `src/mitochime/train_all_models.py` | `PAIR_train_noq.tsv`, `PAIR_test_noq.tsv` | baseline joblib models, `reports/metrics_pair_noq/metrics_summary.tsv` | 5-fold CV, default zoo, random state 42 | `scikit-learn`, `xgboost`, `lightgbm`, `catboost` | Yes | Yes if dependencies exist | Non-pair `metrics_noq` branch also exists |
| 8. Tuned classical model training | `src/mitochime/hyperparam_search_top.py` | `PAIR_train_noq.tsv`, `PAIR_test_noq.tsv` | tuned models, best-params JSON, `tuned_models_summary.tsv` | `--n-iter 25`, random state 42 | same as above | Yes | Yes if dependencies exist | Non-pair `hparam_tuning_noq` branch also exists |
| 9. Sequence TSV generation for deep learning | `src/mitochime/deep_learning/make_seq_tsv.py` | `PAIR_train.tsv`, `PAIR_test.tsv`, raw FASTQ | `PAIR_train_seq_L150.tsv`, `PAIR_test_seq_L150.tsv` | `--L 150`; optional `--with-qual` not used in final artifacts | `pandas` | Yes | Yes, but requires raw FASTQ availability | `L300` variants and older sequence tables also exist |
| 10. Fold generation for deep CV | `src/mitochime/deep_learning/make_folds.py` | `PAIR_train_seq_L150.tsv` | fold assignment TSV | `--n-splits 5`, `--seed 42` | `pandas`, `scikit-learn` | Yes for cross-validation | Yes | none |
| 11. Deep model training: CNN | `src/mitochime/deep_learning/train_deep.py --mode cnn` | `PAIR_train_seq_L150.tsv`, `PAIR_test_seq_L150.tsv` | CNN checkpoint and reports | `epochs=25` for fixed final artifact; `batch=128`, `lr=0.001`, `weight_decay=1e-4`, `seed=42` | `torch` | Yes | No, blocked by missing `dl_rnn.py` import | Older `cnn_final_L150_seed42` and CV folds exist |
| 12. Deep model training: BiGRU | `src/mitochime/deep_learning/train_deep.py --mode rnn_kmer_gru` | same sequence TSVs | BiGRU checkpoint and reports | `k=4`, `L_kmers=147`, `hidden=256`, `embed_dim=64`, `epochs=30`, `bidirectional`, `pool=last`, `seed=42` | `torch` | Yes | No, blocked by missing `dl_rnn.py` import | Older BiLSTM checkpoints exist but look non-canonical |
| 13. Optional deep model training: Transformer | `src/mitochime/deep_learning/train_deep.py --mode transformer` | same sequence TSVs | transformer checkpoint and reports | `k=6`, `L_kmers=256`, `d_model=128`, `layers=4`, `heads=4`, `epochs=15` | `torch` | Maybe | No, blocked by same import issue | `run_pipeline_transformer.sh` and transformer metrics exist |
| 14. GB inference and pair-safe FASTQ filtering | `src/scripts/run_pipeline_gb.sh` | paired FASTQ, reference FASTA, tuned GB model | feature TSV + filtered FASTQ | threshold usually `0.3`, `0.5`, or `0.7`; model path `models_pair_noq_tuned/gradient_boosting_tuned.joblib` | `minimap2`, `samtools`, Python libs | Yes | Likely yes if tools exist | older `gb_predict_filter.py` / `06_predict_ml.py` are superseded |
| 15. CNN inference and pair-safe FASTQ filtering | `src/scripts/run_pipeline_cnn.sh` | paired FASTQ, final CNN checkpoint | `.npz`, prediction TSV, filtered FASTQ | default threshold `0.5`; final model `cnn_final_L150_seed42_fixedep25/cnn_final.pt` | `torch`, `seqkit`, gzip tools | Yes | Likely yes if tools exist | older encoder variant `dl_encode_fastq_pairs.py` |
| 16. BiGRU inference and pair-safe FASTQ filtering | `src/scripts/run_pipeline_rnnkmer.sh` | paired FASTQ, final BiGRU checkpoint | seq TSV, prediction TSV, filtered FASTQ | threshold `0.5`; `k=4`, `L_kmers=147`, `embed_dim=64`, `hidden=256` | `torch`, `seqkit` | Yes | Likely yes if tools exist | transformer inference is separate optional branch |
| 17. Assembly validation | `src/scripts/run_spades.sh` and `src/scripts/run_final_all_t0p5.sh` | unfiltered and filtered FASTQ pairs | SPAdes outputs, `reports/final_run/eval_final_all_t0p5.tsv` | threshold `0.5`; SPAdes k list fixed in wrapper | `spades.py`, `seqkit` | Yes | Partially | older evaluation batches and `data/assemblies/*` legacy runs |
| 18. Publication figures and tables | `notebooks/01_eda_pair.ipynb`, `03_compare_tuned_vs_baseline_pair.ipynb`, `04_C4_pair.ipynb`, `cnn_rnn_analysis.ipynb`, `05_spades_metrics_compare.ipynb`, `external_test.ipynb` | report TSV/JSON, models, assembly outputs | final tables, figures, compare TSVs | notebook-specific | Jupyter stack | Yes | Partially | non-pair notebook set is older branch |

## Recommended canonical branches

### Classical model branch

1. `data/features/v1/clean_features_k6.tsv`
2. `data/features/v1/chimera_features_k6.tsv`
3. `data/processed/all_reads.tsv`
4. `data/processed/PAIR_train.tsv` + `PAIR_test.tsv`
5. `data/processed/PAIR_train_noq.tsv` + `PAIR_test_noq.tsv`
6. `src/mitochime/train_all_models.py`
7. `src/mitochime/hyperparam_search_top.py`

### Deep-learning branch

1. pair-safe split IDs from `PAIR_train.tsv` / `PAIR_test.tsv`
2. `src/mitochime/deep_learning/make_seq_tsv.py --L 150`
3. `src/mitochime/deep_learning/make_folds.py`
4. `src/mitochime/deep_learning/train_deep.py --mode cnn`
5. `src/mitochime/deep_learning/train_deep.py --mode rnn_kmer_gru`
6. optional transformer branch only if retained

### Inference and assembly branch

1. `src/scripts/run_pipeline_gb.sh`
2. `src/scripts/run_pipeline_cnn.sh`
3. `src/scripts/run_pipeline_rnnkmer.sh`
4. `src/scripts/run_spades.sh`
5. `src/scripts/run_final_all_t0p5.sh`

## Current blockers and cleanup required before claiming a clean canonical workflow

1. Remove or guard the missing `dl_rnn.py` import in `train_deep.py`.
2. Replace or archive the stub `src/mitochime/cli.py` and update the top-level `Makefile`.
3. Consolidate duplicate tuned-model directories.
4. Decide whether transformer and non-pair notebook branches belong in the release.
5. Document the 15-row pair mismatch between feature tables and deep sequence tables.
