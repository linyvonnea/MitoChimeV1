# Features

The canonical raw feature table contains 30 columns. The pair-safe no-quality publication model uses the 24-feature order recorded in `feature_cols_24.json`.

Retained canonical feature families:

- alignment context: `strand`, `mapq`, `num_segments`
- supplementary alignment structure: `has_sa`, `sa_count`, `sa_*`
- clipping and breakpoint features: `softclip_*`, `total_clipped_bases`, `breakpoint_read_pos`
- composition and junction features: `kmer_cosine_diff`, `kmer_js_divergence`, `microhomology_*`

Excluded from the canonical no-quality branch:

- `mean_base_quality`
- `ref_start_1based`

