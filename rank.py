#!/usr/bin/env python3
"""Rank Redrob candidates for the challenge JD."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.io_utils import read_candidates, write_submission
from src.pipeline import rank_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--top-n", type=int, default=100, help="Rows to emit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ranked = rank_candidates(read_candidates(args.candidates), top_n=args.top_n)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    write_submission(args.out, ranked)


if __name__ == "__main__":
    main()
