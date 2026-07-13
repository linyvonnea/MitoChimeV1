# Reproducibility

Current status:

- pair-safe classical training is structurally reproducible from retained processed datasets
- deep training is limited to verified modes (`cnn`, `rnn_kmer_gru`, optional `transformer`)
- external assembly reproduction still depends on local tool installation and unresolved external FASTQ availability

Workflow boundary summary:

- base install only: CLI help, environment reporting, pair-integrity validation, schema-aware utilities, example smoke-test data
- `.[classical]`: baseline and tuned classical comparison workflows
- `.[deep]`: CNN and BiGRU training or inference workflows
- tracked canonical pretrained models: GB, CNN, and BiGRU checkpoints are included directly in the repository
- `mitochime validate-models`: requires the tracked checkpoints plus the corresponding optional Python dependencies
- external FASTQs required: publication-scale filtering and assembly comparison runs

External tool boundaries:

- `wgsim`: simulated read generation
- `minimap2` and `samtools`: alignment and BAM creation for tabular GB feature extraction
- `seqkit`: post-filter read counting checks in CNN and BiGRU wrappers
- `spades.py`: assembly comparison workflow
- `GetOrganelle`: optional organelle assembly workflow support

Saved publication metrics and tables are retained in `results/`, but this remediation pass does not claim that the NiDS paper results were regenerated from scratch.

Important caveats:

- the repository preserves original publication outputs and does not silently regenerate them
- example data are only for smoke testing
- exact licensing and hosting for external evaluation datasets are still unresolved

Use `mitochime report-environment` to inspect local tool availability.
Use `mitochime validate-models` to confirm that the tracked canonical checkpoints still match their recorded checksums and load successfully.
