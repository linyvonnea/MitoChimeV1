# Methodology

The retained publication workflow combines read-level alignment features and sequence-based deep models to detect PCR-induced mitochondrial chimeras.

- Tabular branch: align reads, extract 30 raw features, remove quality-inclusive fields for the canonical no-quality branch, then train classical comparison models.
- Deep branch: keep the pair-aware split, rebuild mate-level sequence TSVs from FASTQ, then train CNN1D and BiGRU k-mer classifiers.
- Filtering branch: apply model predictions pair-safely so both mates are retained or removed together.
- Assembly branch: compare filtered and unfiltered FASTQ pairs with SPAdes-derived assembly metrics.

