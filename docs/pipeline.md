# Pipeline

The canonical publication path is:

1. `scripts/data_prep/make_chimeric_templates.py`
2. `scripts/data_prep/simulation.py`
3. `scripts/data_prep/extract_features.py`
4. `python -m mitochime.cli build-dataset`
5. `python -m mitochime.cli split`
6. `python -m mitochime.make_noq_datasets_pair`
7. `python -m mitochime.cli train-classical`
8. `python -m mitochime.deep_learning.make_seq_tsv`
9. `python -m mitochime.cli train-cnn`
10. `python -m mitochime.cli train-bigru`
11. `bash scripts/inference/run_pipeline_gb.sh ...`
12. `bash scripts/inference/run_pipeline_cnn.sh ...`
13. `bash scripts/inference/run_pipeline_rnnkmer.sh ...`
14. `bash scripts/assembly/run_spades.sh ...`

