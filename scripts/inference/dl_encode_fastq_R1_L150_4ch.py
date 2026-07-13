#!/usr/bin/env python3
"""Encode R1 reads as one-hot tensors for CNN inference."""

from __future__ import annotations

import argparse

import numpy as np

from mitochime.utils.fastq import iter_fastq

def onehot_4ch(seq: str, L: int) -> np.ndarray:
    # shape (4, L)
    arr = np.zeros((4, L), dtype=np.float32)
    seq = seq.upper()
    # pad/truncate
    if len(seq) < L:
        seq = seq + ("N" * (L - len(seq)))
    else:
        seq = seq[:L]

    # A,C,G,T mapping
    for i, b in enumerate(seq):
        if b == "A":
            arr[0, i] = 1.0
        elif b == "C":
            arr[1, i] = 1.0
        elif b == "G":
            arr[2, i] = 1.0
        elif b == "T":
            arr[3, i] = 1.0
        # else: N/others remain 0
    return arr

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Encode mate 1 reads into the one-hot representation expected by the CNN."
    )
    ap.add_argument("--r1", required=True)
    ap.add_argument("--out", required=True, help="output .npz")
    ap.add_argument("--out-ids", required=True, help="output ids.txt")
    ap.add_argument("--read-len", type=int, default=150)
    args = ap.parse_args()

    L = args.read_len

    ids = []
    X_list = []

    for record in iter_fastq(args.r1):
        ids.append(record.base_id)
        X_list.append(onehot_4ch(record.sequence.strip(), L))

    if not X_list:
        raise SystemExit("[ERROR] No reads found in R1")

    X = np.stack(X_list, axis=0)  # (N, 4, L)
    np.savez_compressed(args.out, X=X)

    with open(args.out_ids, "wt") as f:
        for rid in ids:
            f.write(rid + "\n")

    print(f"[OK] Encoded {X.shape[0]} reads -> {args.out}  shape={X.shape}")
    print(f"[OK] IDs -> {args.out_ids}")

if __name__ == "__main__":
    main()
