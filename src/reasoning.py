"""Reasoning generation for final CSV."""

from __future__ import annotations

from .features import CandidateFeatures


def join_evidence(parts: list[str]) -> str:
    clean = [part for part in parts if part]
    if not clean:
        return "relevant ML systems background"
    return ", ".join(clean[:3])


def generate_reasoning(features: CandidateFeatures, rank: int) -> str:
    years_text = f"{features.years:.1f} years"
    evidence = join_evidence(features.top_evidence)
    concern = features.concerns[0] if features.concerns else ""

    if rank <= 10:
        sentence1 = (
            f"{features.title} with {years_text}; strongest evidence is {evidence}, "
            f"which maps well to Redrob's retrieval and ranking mandate."
        )
    elif rank <= 40:
        sentence1 = (
            f"{features.title} with {years_text}; profile shows {evidence} and enough applied ML depth "
            f"to stay in serious consideration."
        )
    else:
        sentence1 = (
            f"{features.title} with {years_text}; has some relevant signals through {evidence}, "
            f"but looks weaker than higher-ranked retrieval-heavy profiles."
        )

    if concern:
        sentence2 = f"Main concern: {concern}."
    elif features.open_to_work and features.notice_period_days <= 60:
        sentence2 = "Availability signals are favorable, which matters for a founding-team hire."
    else:
        sentence2 = "Behavioral signals are solid enough to keep the profile viable."
    return f"{sentence1} {sentence2}"
