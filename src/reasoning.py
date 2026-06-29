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
    evidence_text = features.top_evidence[0] if features.top_evidence else "ML systems work"
    second_evidence = features.top_evidence[1] if len(features.top_evidence) > 1 else ""

    if rank <= 10:
        if "search" in evidence_text.lower() or "retrieval" in evidence_text.lower():
            sentence1 = (
                f"{features.title} with {years_text}; search/retrieval proof is {evidence}, "
                f"which lines up well with JD."
            )
        elif "recommend" in evidence_text.lower():
            sentence1 = (
                f"{features.title} with {years_text}; recommendation evidence is {evidence}, "
                f"good fit for ranking-heavy work."
            )
        else:
            sentence1 = (
                f"{features.title} with {years_text}; strongest signal is {evidence}, "
                f"which maps well to Redrob's retrieval and ranking mandate."
            )
    elif rank <= 40:
        if second_evidence:
            sentence1 = (
                f"{features.title} with {years_text}; profile pairs {evidence_text} with {second_evidence}, "
                f"enough applied depth to stay in serious consideration."
            )
        else:
            sentence1 = (
                f"{features.title} with {years_text}; profile shows {evidence} and enough applied ML depth "
                f"to stay in serious consideration."
            )
    else:
        if second_evidence:
            sentence1 = (
                f"{features.title} with {years_text}; relevant signals are {evidence_text} and {second_evidence}, "
                f"but still weaker than higher-ranked retrieval-heavy profiles."
            )
        else:
            sentence1 = (
                f"{features.title} with {years_text}; has some relevant signals through {evidence}, "
                f"but looks weaker than higher-ranked retrieval-heavy profiles."
            )

    if concern:
        concern_map = {
            "title-heavy profile": "Main concern: title looks stronger than supporting evidence.",
            "title-evidence gap": "Main concern: title leads support evidence too much.",
            "not open to work": "Main concern: not open to work.",
            "sub-50% recruiter response": "Main concern: recruiter response is weak.",
            "weak recruiter response": "Main concern: recruiter response is weak.",
            "middling recruiter response": "Main concern: recruiter response is only moderate.",
            "long-day notice": "Main concern: notice period is long.",
        }
        sentence2 = concern_map.get(concern, f"Main concern: {concern}.")
    elif features.open_to_work and features.notice_period_days <= 60:
        sentence2 = "Availability signals are favorable, which matters for a founding-team hire."
    else:
        sentence2 = "Behavioral signals are solid enough to keep the profile viable."
    return f"{sentence1} {sentence2}"
