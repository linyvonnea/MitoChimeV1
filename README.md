# MitoChime

MitoChime is a pair-safe machine-learning workflow for detecting PCR-induced chimeras in mitochondrial Illumina read pairs. This cleaned repository focuses on the NiDS 2026 publication path and preserves older exploratory material under `archive/`.

## Scientific Scope

- Problem: PCR chimeras can distort mitochondrial read sets and downstream assembly quality.
- Main workflow: simulate or collect paired reads, align when required, extract read-level features, build pair-aware datasets, train models, filter both mates consistently, and compare assemblies.
- Canonical publication branch: pair-aware, pair-safe, no-quality-feature workflow.
- Primary model roles:
  - tuned Gradient Boosting: canonical tabular inference model
  - CNN1D: sequence-based comparison and filtering model
  - BiGRU k-mer: strongest sequence-based comparison and filtering model

## Repository Scope

This repository prioritizes:

- canonical source code under `src/mitochime`
- operational shell wrappers under `scripts/`
- publication notebooks under `notebooks/publication/`
- reproducibility and migration documentation under `docs/`
- lightweight publication outputs under `results/`
- example inputs under `data/example/`

Large run outputs, manuscript drafts, defense material, duplicate bundles, and uncertain legacy code have been moved under `archive/`.

## Repository Structure

```text
.
├── src/mitochime/
├── scripts/
├── data/
│   ├── example/
│   ├── processed/
│   ├── refs/
│   └── manifests/
├── models/
│   ├── deep/
│   ├── metadata/
│   └── pair_noq_tuned/
├── results/
├── notebooks/
├── docs/
└── archive/
```

## Installation

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[classical,deep,dev]"
```

Optional dependency groups:

- base package only: `python3 -m pip install .`
- classical comparison panel: `python3 -m pip install ".[classical]"`
- deep-learning commands and inference: `python3 -m pip install ".[deep]"`
- development and tests: `python3 -m pip install -e ".[dev]"`
- full local researcher setup: `python3 -m pip install -e ".[classical,deep,dev]"`

Conda environment manifests remain available in [environment.yml](environment.yml) and [environment.arm.yml](environment.arm.yml).

## External Tools

The base Python installation does not install external bioinformatics tools.

Workflow stages may additionally require:

- `minimap2`
- `samtools`
- `wgsim`
- `seqkit`
- `spades.py`
- `GetOrganelle`

Run `python3 -m mitochime.cli report-environment` after installation to see which Python packages and external tools are currently available. See [docs/reproducibility.md](docs/reproducibility.md) for tool-by-tool notes and current reproduction limits.

## Quick Start

The example data are synthetic smoke-test inputs, not publication data. These commands work from a fresh tracked clone:

```bash
python3 -m mitochime.cli report-environment
python3 -m mitochime.cli validate-models \
  --report-json results/validation/example_model_validation.json
python3 -m mitochime.cli validate-pairs \
  --feature-dataset data/example/example_pair_features.tsv \
  --sequence-dataset data/example/example_pair_seq.tsv \
  --split-dataset data/example/example_pair_split.tsv \
  --report-json results/validation/example_pair_integrity.json
```

## Practical Use After Cloning

1. Clone the repository and install the base package with `python3 -m pip install .`.
2. Run `python3 -m mitochime.cli report-environment` and decide whether you only need the base package or the full `.[classical,deep,dev]` researcher setup.
3. Run `python3 -m mitochime.cli validate-models` to confirm the tracked GB, CNN, and BiGRU artifacts match their recorded SHA-256 checksums and still load.
4. Install external tools and supply external FASTQs only for the workflow stages that need them.

## Canonical Workflow

1. Reference preparation: `scripts/data_prep/make_chimeric_templates.py`
2. Simulation and alignment: `scripts/data_prep/simulation.py`
3. Feature extraction: `scripts/data_prep/extract_features.py`
4. Dataset construction: `python -m mitochime.cli build-dataset`
5. Pair-aware splitting: `python -m mitochime.cli split`
6. Pair-safe no-quality datasets: `python -m mitochime.make_noq_datasets_pair`
7. Classical model training: `python -m mitochime.cli train-classical`
8. Deep sequence preparation: `python -m mitochime.deep_learning.make_seq_tsv`
9. CNN training: `python -m mitochime.cli train-cnn`
10. BiGRU training: `python -m mitochime.cli train-bigru`
11. Pair-safe filtering:
    - GB: `bash scripts/inference/run_pipeline_gb.sh ...`
    - CNN: `bash scripts/inference/run_pipeline_cnn.sh ...`
    - BiGRU: `bash scripts/inference/run_pipeline_rnnkmer.sh ...`
12. Assembly validation: `bash scripts/assembly/run_spades.sh ...`

Immediate clone behavior:

- runnable after base install: CLI help, `report-environment`, pair-integrity validation, schema-aware utilities, smoke-test example data
- requires `.[classical]`: baseline/tuned classical comparison workflows
- requires `.[deep]`: CNN and BiGRU training or inference workflows
- tracked canonical pretrained models included in Git: `gradient_boosting_tuned.joblib`, `cnn_final.pt`, and `rnn_kmer_gru_best.pt`
- requires tracked model artifacts plus optional deps: `mitochime validate-models`
- requires tracked model artifacts plus external tools and FASTQs: `mitochime filter --mode {gb,cnn,bigru}` and the corresponding Bash wrappers
- requires external FASTQs plus bioinformatics tools: end-to-end filtering and assembly comparison workflows

## Decision Thresholds

- canonical filtering threshold in the final assembly comparison: `0.5`
- canonical deep sequence length: `150`
- canonical random seed: `42`

## Data Integrity Note

The publication tabular feature datasets and deep sequence datasets share pair-level split assignments but not perfectly identical mate-row sets. Fifteen pair IDs are missing one mate in the feature-derived tables while the sequence TSVs reconstruct both mates from FASTQ. This is preserved intentionally and documented in:

- [docs/data_integrity.md](docs/data_integrity.md)
- [docs/reproducibility.md](docs/reproducibility.md)
- [results/validation](results/validation)

## Reproducibility Status

- Classical pair-noq training is structurally reproducible from retained code and processed datasets.
- Deep training exposes only verified modes, but reruns still depend on local `torch` and retained sequence datasets.
- Tracked clones now retain the three canonical pretrained inference artifacts plus their checksum manifest and feature schemas.
- External assembly reproduction still depends on non-repo data access and external bioinformatics tools.
- Saved publication tables, metrics, and figures are retained release artifacts; this repository does not claim they were regenerated during this remediation pass.
- The repository is technically smoke-testable, but it does not claim full NiDS publication reproduction.

## Known Limitations

- External FASTQ licensing and hosting decisions remain unresolved.
- The transformer branch is preserved only as review-needed material.
- Several large archived PDFs and legacy datasets are still tracked and should be reviewed before a public GitHub push.
- Licensing and archive DOI remain researcher decisions.

## Citation

Paper title: “MitoChime: A Machine Learning Pipeline for Detecting PCR-Induced Chimeras in Mitochondrial Illumina Reads”

Placeholders:

- Paper URL: pending
- DOI: pending
- Dataset archive: pending
- Software release URL: pending

## Authors

See [AUTHORS.md](AUTHORS.md).
## Docker

MitoChime can be run in a Docker container with its Python and
bioinformatics dependencies pre-installed, including minimap2,
samtools, seqkit, scikit-learn, and CPU-only PyTorch.

### Build the image

```bash
docker build -t mitochime:latest .
## License

See [LICENSE](LICENSE). A final open-source license selection is still pending.
