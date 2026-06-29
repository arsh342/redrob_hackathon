"""Shared ranking pipeline for CLI and sandbox app."""

from __future__ import annotations

from collections.abc import Iterable

from .features import CandidateFeatures, extract_features
from .reasoning import generate_reasoning
from .scoring import select_top


def rank_candidates(candidates: Iterable[dict], top_n: int = 100) -> list[tuple[CandidateFeatures, str]]:
    features_iter = (extract_features(candidate) for candidate in candidates)
    selected = select_top(features_iter, top_n=top_n, buffer_n=max(250, top_n * 3))
    return [(features, generate_reasoning(features, rank)) for rank, features in enumerate(selected, start=1)]
