from pathlib import Path

from mitochime.filtering import filter_pair_fastqs


FASTQ_R1 = """@pairA/1
ACGT
+
IIII
@pairB/1
TGCA
+
IIII
"""

FASTQ_R2 = """@pairA/2
TTTT
+
IIII
@pairB/2
CCCC
+
IIII
"""


def test_filter_pair_fastqs_keeps_mates_consistently(tmp_path: Path):
    r1 = tmp_path / "reads_R1.fastq"
    r2 = tmp_path / "reads_R2.fastq"
    out_r1 = tmp_path / "kept_R1.fastq"
    out_r2 = tmp_path / "kept_R2.fastq"
    r1.write_text(FASTQ_R1)
    r2.write_text(FASTQ_R2)

    summary = filter_pair_fastqs(
        r1_path=r1,
        r2_path=r2,
        kept_ids={"pairB"},
        out_r1_path=out_r1,
        out_r2_path=out_r2,
    )

    assert summary.kept_pairs == 1
    assert "pairB/1" in out_r1.read_text()
    assert "pairA/1" not in out_r1.read_text()
    assert "pairB/2" in out_r2.read_text()
    assert "pairA/2" not in out_r2.read_text()

