import pandas as pd

from mitochime.build_pair_splits import build_pair_split_frame
from mitochime.utils.read_ids import normalize_base_read_id


def test_pair_split_keeps_mates_together_and_is_deterministic():
    frame = pd.DataFrame(
        {
            "read_id": [
                "pairA/1",
                "pairA/2",
                "pairB/1",
                "pairB/2",
                "pairC/1",
                "pairC/2",
                "pairD/1",
                "pairD/2",
            ],
            "label": [0, 0, 0, 0, 1, 1, 1, 1],
            "read_length": [150] * 8,
        }
    )
    train_a, test_a = build_pair_split_frame(frame, test_size=0.5, random_state=42)
    train_b, test_b = build_pair_split_frame(frame, test_size=0.5, random_state=42)

    assert train_a["read_id"].tolist() == train_b["read_id"].tolist()
    assert test_a["read_id"].tolist() == test_b["read_id"].tolist()

    train_ids = set(train_a["read_id"].map(normalize_base_read_id))
    test_ids = set(test_a["read_id"].map(normalize_base_read_id))
    assert train_ids.isdisjoint(test_ids)
    assert all(train_a.groupby(train_a["read_id"].map(normalize_base_read_id)).size() == 2)
    assert all(test_a.groupby(test_a["read_id"].map(normalize_base_read_id)).size() == 2)

