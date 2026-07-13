# Data Layout

- `refs/`: small reference FASTA assets used by the canonical workflow
- `processed/`: publication tabular and sequence datasets retained from the original work
- `example/`: synthetic smoke-test data only
- `manifests/`: checksums, inventory files, and integrity reports

Large run outputs and unresolved external datasets are archived outside the main data tree.

Reference note:

- `data/refs/mt_ref.fasta` is the portable canonical mitochondrial reference alias retained for the workflow.
- Accession: `NC_039553.1`
- Sequence length: `16,616 bp`
- File size: `16,917 bytes`
- SHA-256: `16b98fa60f7e8ffdddf9f012575dfc82231d672dbbb7d5a594748a5fdb619d8d`
- Source description: `Sardinella lemuru mitochondrion, complete genome`
- Redistribution status: researcher review still required before claiming public redistribution rights.
- Detailed availability, checksums, and regeneration notes are recorded in `data/manifests/DATA_ARTIFACT_MANIFEST.tsv`.
