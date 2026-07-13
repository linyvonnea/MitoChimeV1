.PHONY: help report-environment validate-pairs train-classical train-cnn train-bigru filter-gb filter-cnn filter-bigru

PYTHON ?= python3
TRAIN ?= data/processed/PAIR_train_noq.tsv
TEST ?= data/processed/PAIR_test_noq.tsv
TRAIN_SEQ ?= data/processed/PAIR_train_seq_L150.tsv
TEST_SEQ ?= data/processed/PAIR_test_seq_L150.tsv
GB_MODELS ?= models/pair_noq_tuned
GB_REPORTS ?= results/metrics/classical/baseline_pair_noq
CNN_MODELS ?= models/deep/cnn_final_L150_seed42_fixedep25
CNN_REPORTS ?= results/metrics/deep/cnn_final_L150_seed42_fixedep25
BIGRU_MODELS ?= models/deep/rnnkmer_bigru_final_L150_seed42
BIGRU_REPORTS ?= results/metrics/deep/rnnkmer_bigru_final_L150_seed42
FEATURE_DATASET ?= data/processed/PAIR_train.tsv
SEQUENCE_DATASET ?= data/processed/PAIR_train_seq_L150.tsv
INTEGRITY_REPORT ?= results/validation/pair_integrity_train.json

help:
	@echo "Targets:"
	@echo "  report-environment  Report Python and external tool availability"
	@echo "  validate-pairs      Write the pair-integrity audit report"
	@echo "  train-classical     Train the baseline classical comparison panel"
	@echo "  train-cnn           Train the canonical CNN1D model"
	@echo "  train-bigru         Train the canonical BiGRU k-mer model"
	@echo "  filter-gb           Run the pair-safe GB inference/filtering pipeline"
	@echo "  filter-cnn          Run the pair-safe CNN inference/filtering pipeline"
	@echo "  filter-bigru        Run the pair-safe BiGRU inference/filtering pipeline"

report-environment:
	$(PYTHON) -m mitochime.cli report-environment

validate-pairs:
	$(PYTHON) -m mitochime.cli validate-pairs --feature-dataset $(FEATURE_DATASET) --sequence-dataset $(SEQUENCE_DATASET) --report-json $(INTEGRITY_REPORT)

train-classical:
	$(PYTHON) -m mitochime.cli train-classical --train $(TRAIN) --test $(TEST) --models-dir $(GB_MODELS) --reports-dir $(GB_REPORTS)

train-cnn:
	$(PYTHON) -m mitochime.cli train-cnn --train-tsv $(TRAIN_SEQ) --test-tsv $(TEST_SEQ) --out-dir $(CNN_MODELS) --reports-dir $(CNN_REPORTS)

train-bigru:
	$(PYTHON) -m mitochime.cli train-bigru --train-tsv $(TRAIN_SEQ) --test-tsv $(TEST_SEQ) --out-dir $(BIGRU_MODELS) --reports-dir $(BIGRU_REPORTS)

filter-gb:
	@echo "Use: bash scripts/inference/run_pipeline_gb.sh <R1> <R2> <RUN_NAME> <THRESH> [THREADS] [REF]"

filter-cnn:
	@echo "Use: bash scripts/inference/run_pipeline_cnn.sh <R1> <R2> <RUN_NAME> [THRESH]"

filter-bigru:
	@echo "Use: bash scripts/inference/run_pipeline_rnnkmer.sh <R1> <R2> <RUN_NAME> [THRESH]"

