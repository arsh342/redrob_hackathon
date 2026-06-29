"""Top-k ranking utilities."""

from __future__ import annotations

import heapq
from typing import Iterable

from .features import CandidateFeatures


def rank_key(features: CandidateFeatures) -> tuple[float, float, float, float, int, int]:
    return (
        features.final_score,
        features.career_score,
        -features.risk_score,
        features.recruiter_response_rate,
        -features.notice_period_days,
        -features.candidate_num,
    )


def select_top(features_iter: Iterable[CandidateFeatures], top_n: int = 100, buffer_n: int = 250) -> list[CandidateFeatures]:
    heap: list[tuple[tuple[float, float, float, float, int, int], CandidateFeatures]] = []
    limit = max(top_n, buffer_n)
    for features in features_iter:
        if (
            features.country.lower() != "india"
            or not features.open_to_work
            or features.recruiter_response_rate < 0.5
            or features.notice_period_days > 90
            or (features.years > 12 and not any(token in features.title.lower() for token in ("senior", "lead", "staff", "principal", "founding")))
        ):
            continue
        item = (rank_key(features), features)
        if len(heap) < limit:
            heapq.heappush(heap, item)
        else:
            heapq.heappushpop(heap, item)
    selected = [item[1] for item in heap]
    selected.sort(key=rank_key, reverse=True)
    return selected[:top_n]
