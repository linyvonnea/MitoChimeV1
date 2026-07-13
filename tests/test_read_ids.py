from mitochime.utils.read_ids import (
    infer_mate_from_header,
    mate_specific_read_id,
    normalize_base_read_id,
    normalize_read_token,
    split_read_id,
)


def test_normalize_read_token_handles_fastq_header_metadata():
    assert normalize_read_token("@M01234:1:000000000-ABC/1 1:N:0:1") == "M01234:1:000000000-ABC/1"


def test_normalize_base_read_id_strips_mate_suffix():
    value = "NC_039553.1_1231_1737_9:0:0_5:0:0_9bd/2"
    assert normalize_base_read_id(value) == "NC_039553.1_1231_1737_9:0:0_5:0:0_9bd"


def test_split_read_id_handles_headers_without_mate_suffix():
    parts = split_read_id("@SIMULATED_READ 2:N:0:1")
    assert parts.base_id == "SIMULATED_READ"
    assert parts.mate is None


def test_mate_specific_read_id_forces_repository_style_suffix():
    assert mate_specific_read_id("foo/1", "2") == "foo/2"


def test_infer_mate_from_header_returns_none_for_orphans():
    assert infer_mate_from_header("@ILLUMINA:READ 1:N:0:1") is None

