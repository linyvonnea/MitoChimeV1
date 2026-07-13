# Release Checklist

## Git and repository

- [ ] clean working tree
- [x] correct release branch
- [x] intended GitHub remote
- [x] no generated cache files tracked
- [x] large tracked files reviewed
- [x] no personal paths in the canonical release surface
- [x] no secrets in the canonical release surface
- [x] fresh clone tested

## Installation

- [x] base installation
- [x] development installation
- [x] wheel build
- [x] wheel installation
- [x] CLI help
- [x] tests
- [x] example workflow

## Models

- [ ] GB model decision
- [ ] CNN model decision
- [ ] BiGRU model decision
- [x] model manifest
- [x] model checksums
- [ ] model download or release location
- [x] missing-model errors tested

## Data

- [x] data manifest
- [x] reference FASTA validated
- [x] processed dataset policy
- [ ] external FASTQ policy
- [ ] external-test data policy
- [ ] assembly-output policy

## Reproducibility

- [x] pair-integrity reports
- [x] feature-schema validation
- [x] notebook paths normalized
- [x] external tools documented
- [x] model inference tested where possible
- [x] publication metrics traceable
- [x] full NiDS reproduction status accurately stated

## Legal and publication metadata

- [ ] software license decision
- [ ] contributor names verified
- [ ] affiliations verified
- [ ] `CITATION.cff` validated
- [ ] paper URL
- [ ] paper DOI when issued
- [ ] archive DOI when issued
