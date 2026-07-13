# Reproducibility

Current status:

- pair-safe classical training is structurally reproducible from retained processed datasets
- deep training is limited to verified modes (`cnn`, `rnn_kmer_gru`, optional `transformer`)
- external assembly reproduction still depends on local tool installation and unresolved external FASTQ availability

Important caveats:

- the repository preserves original publication outputs and does not silently regenerate them
- example data are only for smoke testing
- exact licensing and hosting for external evaluation datasets are still unresolved

Use `mitochime report-environment` to inspect local tool availability.

