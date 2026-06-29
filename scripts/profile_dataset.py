#!/usr/bin/env python3
"""Quick dataset profiler for tuning heuristics."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features import extract_features


def main() -> None:
    path = Path("candidates.jsonl")
    title_counter = Counter()
    positive_counter = Counter()
    concern_counter = Counter()
    top_samples = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            candidate = json.loads(line)
            features = extract_features(candidate)
            title_counter[features.title] += 1
            for evidence in features.top_evidence:
                positive_counter[evidence] += 1
            for concern in features.concerns:
                concern_counter[concern] += 1
            top_samples.append(features)

    top_samples.sort(key=lambda item: item.final_score, reverse=True)
    print("Top titles:", title_counter.most_common(20))
    print("Top evidence:", positive_counter.most_common(20))
    print("Top concerns:", concern_counter.most_common(20))
    print("Top candidates:")
    for features in top_samples[:20]:
        print(
            features.candidate_id,
            round(features.final_score, 2),
            features.title,
            features.current_company,
            features.top_evidence,
            features.concerns,
        )


if __name__ == "__main__":
    main()
