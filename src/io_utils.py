"""I/O helpers."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Iterator

from .features import CandidateFeatures


def read_candidates(path: str | Path) -> Iterator[dict]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def read_candidates_from_text(text: str) -> Iterator[dict]:
    for line in text.splitlines():
        line = line.strip()
        if line:
            yield json.loads(line)


def ranked_rows(ranked: list[tuple[CandidateFeatures, str]]) -> list[dict[str, str | int]]:
    return [
        {
            "candidate_id": features.candidate_id,
            "rank": rank,
            "score": f"{features.final_score:.6f}",
            "reasoning": reasoning,
        }
        for rank, (features, reasoning) in enumerate(ranked, start=1)
    ]


def submission_csv_text(ranked: list[tuple[CandidateFeatures, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])
    for row in ranked_rows(ranked):
        writer.writerow([row["candidate_id"], row["rank"], row["score"], row["reasoning"]])
    return buffer.getvalue()


def write_submission(path: str | Path, ranked: list[tuple[CandidateFeatures, str]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (features, reasoning) in enumerate(ranked, start=1):
            writer.writerow([features.candidate_id, rank, f"{features.final_score:.6f}", reasoning])
