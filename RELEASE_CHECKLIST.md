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

- [x] GB model decision
- [x] CNN model decision
- [x] BiGRU model decision
- [x] model manifest
- [x] model checksums
- [x] model download or release location
- [x] model integrity validation command
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
