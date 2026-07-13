import pandas as pd
import pytest

from mitochime.feature_schema import CANONICAL_PAIR_NOQ_FEATURE_COLUMNS, prepare_feature_frame


def test_prepare_feature_frame_preserves_canonical_order():
    frame = pd.DataFrame(
        {
            "label": [0, 1],
            "read_id": ["pairA/1", "pairB/1"],
            "strand": ["+", "-"],
            "mapq": [60, 55],
            "read_length": [150, 150],
            "has_sa": [0, 1],
            "sa_count": [0, 1],
            "num_segments": [1, 2],
            "sa_diff_contig": [0, 1],
            "sa_min_delta_pos": [0, 4],
            "sa_max_delta_pos": [0, 10],
            "sa_mean_delta_pos": [0, 7],
            "sa_same_strand_count": [0, 1],
            "sa_opp_strand_count": [0, 0],
            "sa_max_mapq": [60, 50],
            "sa_mean_mapq": [60, 45],
            "sa_min_nm": [0, 1],
            "sa_mean_nm": [0, 1],
            "softclip_left": [0, 4],
            "softclip_right": [0, 6],
            "total_clipped_bases": [0, 10],
            "breakpoint_read_pos": [75, 82],
            "kmer_cosine_diff": [0.0, 0.4],
            "kmer_js_divergence": [0.0, 0.2],
            "microhomology_length": [0, 6],
            "microhomology_gc": [0.0, 0.5],
            "ref_name": ["chrM", "chrM"],
            "cigar": ["150M", "70M10S"],
        }
    )
    prepared = prepare_feature_frame(frame)
    assert prepared.columns.tolist() == CANONICAL_PAIR_NOQ_FEATURE_COLUMNS
    assert prepared["strand"].tolist() == [1.0, 0.0]


def test_prepare_feature_frame_raises_for_missing_columns():
    frame = pd.DataFrame({"label": [0], "read_id": ["pairA/1"]})
    with pytest.raises(ValueError, match="missing canonical features"):
        prepare_feature_frame(frame)

