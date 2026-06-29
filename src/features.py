"""Feature extraction for candidate scoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any

from .jd_profile import (
    CAREER_POSITIVE_PHRASES,
    EVAL_TERMS,
    NEGATIVE_TITLES,
    POSITIVE_SKILLS,
    POSITIVE_TITLE_WEIGHTS,
    PRODUCT_COMPANIES,
    RESEARCH_NEGATIVE_PHRASES,
    SERVICE_COMPANIES,
    SUMMARY_NEGATIVE_PHRASES,
    TARGET_CITIES,
    TITLE_KEYWORD_WEIGHTS,
)

REFERENCE_DATE = date(2026, 6, 20)
YEARS_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*years")


@dataclass(slots=True)
class CandidateFeatures:
    candidate_id: str
    candidate_num: int
    title: str
    years: float
    country: str
    location: str
    current_company: str
    title_score: float
    career_score: float
    skills_score: float
    company_score: float
    location_score: float
    evaluation_score: float
    coding_score: float
    behavior_score: float
    behavior_multiplier: float
    risk_score: float
    suspicious_score: float
    final_score: float
    recruiter_response_rate: float
    notice_period_days: int
    open_to_work: bool
    top_evidence: list[str]
    concerns: list[str]


def norm(text: str) -> str:
    return " ".join((text or "").lower().replace("/", " ").replace("-", " ").split())


def safe_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def exact_or_keyword_title_score(title_norm: str) -> float:
    score = POSITIVE_TITLE_WEIGHTS.get(title_norm, 0.0)
    for keyword, weight in TITLE_KEYWORD_WEIGHTS.items():
        if keyword in title_norm:
            score += weight
    score -= NEGATIVE_TITLES.get(title_norm, 0.0)
    return score


def count_phrase_score(text: str, weights: dict[str, float]) -> tuple[float, list[str]]:
    score = 0.0
    hits: list[str] = []
    for phrase, weight in weights.items():
        if phrase in text:
            score += weight
            hits.append(phrase)
    return score, hits


def extract_summary_years(summary: str) -> float | None:
    match = YEARS_PATTERN.search(summary)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def company_signal(candidate: dict[str, Any]) -> tuple[float, bool, bool]:
    companies = []
    companies.append(norm(candidate["profile"].get("current_company", "")))
    companies.extend(norm(item.get("company", "")) for item in candidate.get("career_history", []))

    has_product = any(any(name in company for name in PRODUCT_COMPANIES) for company in companies)
    service_hits = sum(1 for company in companies if any(name in company for name in SERVICE_COMPANIES))
    unique_non_empty = sum(1 for company in set(companies) if company)
    consulting_only = service_hits > 0 and service_hits >= max(1, unique_non_empty)

    score = 0.0
    if has_product:
        score += 7.0
    if consulting_only:
        score -= 7.0
    industry = norm(candidate["profile"].get("current_industry", ""))
    if industry in {"software", "saas", "ai ml", "fintech", "e commerce", "food delivery", "adtech"}:
        score += 3.0
    if industry == "it services":
        score -= 2.0
    return score, has_product, consulting_only


def location_signal(candidate: dict[str, Any]) -> tuple[float, list[str]]:
    profile = candidate["profile"]
    location_norm = norm(profile.get("location", ""))
    country = norm(profile.get("country", ""))
    willing = candidate["redrob_signals"].get("willing_to_relocate", False)
    score = 0.0
    evidence: list[str] = []

    if country == "india":
        score += 6.0
        evidence.append("india-based")
    else:
        score -= 20.0
    if any(city in location_norm for city in TARGET_CITIES):
        score += 4.0
        evidence.append(profile.get("location", ""))
    if willing:
        score += 3.0
        evidence.append("willing to relocate")
    elif country != "india":
        score -= 15.0
    return score, evidence


def skill_signal(candidate: dict[str, Any]) -> tuple[float, list[str], int, int]:
    score = 0.0
    evidence: list[str] = []
    matched = set()
    expert_count = 0
    zero_duration_expert_count = 0
    for skill in candidate.get("skills", []):
        name = norm(skill.get("name", ""))
        if skill.get("proficiency") == "expert":
            expert_count += 1
            if (skill.get("duration_months") or 0) == 0:
                zero_duration_expert_count += 1
        if name in matched or name not in POSITIVE_SKILLS:
            continue
        matched.add(name)
        base = POSITIVE_SKILLS[name]
        duration = skill.get("duration_months") or 0
        endorsements = skill.get("endorsements") or 0
        trust = 1.0
        if duration >= 24:
            trust += 0.2
        if endorsements >= 10:
            trust += 0.15
        score += base * trust
        evidence.append(skill.get("name", ""))
    priority = {
        "learning to rank": 100,
        "information retrieval": 95,
        "semantic search": 90,
        "vector search": 88,
        "embeddings": 86,
        "bm25": 84,
        "sentence transformers": 82,
        "faiss": 80,
        "pinecone": 78,
        "qdrant": 78,
        "weaviate": 78,
        "milvus": 78,
        "elasticsearch": 76,
        "opensearch": 76,
        "recommendation systems": 75,
        "recommender systems": 75,
        "pgvector": 74,
        "python": 72,
        "mlflow": 50,
        "qlora": 20,
        "lora": 20,
        "peft": 20,
        "rag": 18,
        "retrieval augmented generation": 18,
    }
    evidence.sort(key=lambda item: priority.get(norm(item), 10), reverse=True)
    return score, evidence[:5], expert_count, zero_duration_expert_count


def behavior_signal(candidate: dict[str, Any]) -> tuple[float, float, list[str], list[str]]:
    sig = candidate["redrob_signals"]
    score = 0.0
    multiplier = 1.0
    evidence: list[str] = []
    concerns: list[str] = []

    if sig.get("open_to_work_flag"):
        score += 4.0
        multiplier += 0.06
        evidence.append("open to work")
    else:
        score -= 30.0
        multiplier -= 0.30
        concerns.append("not open to work")

    last_active = safe_date(sig.get("last_active_date"))
    if last_active:
        days = (REFERENCE_DATE - last_active).days
        if days <= 21:
            score += 4.0
            multiplier += 0.06
            evidence.append("recently active")
        elif days <= 60:
            score += 2.0
        elif days > 150:
            score -= 6.0
            multiplier -= 0.10
            concerns.append("stale activity")

    response_rate = float(sig.get("recruiter_response_rate") or 0.0)
    if response_rate < 0.5:
        score -= 12.0
        multiplier -= 0.15
        concerns.append("sub-50% recruiter response")
    if response_rate >= 0.75:
        score += 5.0
        multiplier += 0.08
        evidence.append(f"{response_rate:.0%} recruiter response")
    elif response_rate >= 0.45:
        score += 2.0
    elif response_rate >= 0.30:
        score -= 12.0
        multiplier -= 0.15
        concerns.append("middling recruiter response")
    elif response_rate < 0.15:
        score -= 14.0
        multiplier -= 0.18
        concerns.append("weak recruiter response")
    else:
        score -= 10.0
        multiplier -= 0.14
        concerns.append("weak recruiter response")

    notice = int(sig.get("notice_period_days") or 0)
    if notice <= 30:
        score += 5.0
        multiplier += 0.08
        evidence.append(f"{notice}-day notice")
    elif notice <= 60:
        score += 2.0
    elif notice <= 90:
        score -= 14.0
        multiplier -= 0.16
        concerns.append(f"{notice}-day notice")
    elif notice >= 120:
        score -= 24.0
        multiplier -= 0.28
        concerns.append(f"{notice}-day notice")
    else:
        score -= 7.0
        multiplier -= 0.10
        concerns.append(f"{notice}-day notice")

    github_score = float(sig.get("github_activity_score") or -1)
    if github_score >= 40:
        score += 2.0
        evidence.append("strong GitHub activity")
    elif github_score == -1:
        score -= 2.0
        concerns.append("no linked GitHub")

    saved = int(sig.get("saved_by_recruiters_30d") or 0)
    search = int(sig.get("search_appearance_30d") or 0)
    if saved >= 10:
        score += 2.0
        evidence.append("saved by recruiters")
    if search >= 500:
        score += 1.5

    interview_rate = float(sig.get("interview_completion_rate") or 0.0)
    if interview_rate >= 0.9:
        score += 2.0
    elif 0.0 <= interview_rate < 0.5:
        score -= 2.0
        concerns.append("weak interview completion")

    if not sig.get("open_to_work_flag") and notice > 60:
        score -= 3.0
        multiplier -= 0.05
        concerns.append("hard-to-close profile")

    multiplier = max(0.70, min(1.30, multiplier))
    return score, multiplier, evidence[:4], concerns


def suspicious_penalty(
    candidate: dict[str, Any],
    years: float,
    summary_years: float | None,
    expert_count: int,
    zero_duration_expert_count: int,
    title_norm: str,
    title_score: float,
    career_score: float,
    skills_score: float,
) -> tuple[float, list[str]]:
    score = 0.0
    concerns: list[str] = []
    if years < 3.0 and any(token in title_norm for token in ("senior", "staff", "lead")):
        score += 10.0
        concerns.append("seniority/experience mismatch")
    if summary_years is not None and abs(summary_years - years) >= 2.0:
        score += 22.0
        concerns.append("profile years mismatch")
    if expert_count >= 8 and zero_duration_expert_count >= 4:
        score += 8.0
        concerns.append("inflated expert skill profile")
    if career_score < 5.0 and skills_score >= 20.0 and NEGATIVE_TITLES.get(title_norm, 0.0) > 0:
        score += 10.0
        concerns.append("keyword-stuffer pattern")

    history_months = sum((item.get("duration_months") or 0) for item in candidate.get("career_history", []))
    if history_months and years * 12 - history_months > 48:
        score += 3.0
        concerns.append("experience/history mismatch")
    if years > 12.0 and "founding" not in title_norm and "principal" not in title_norm and "staff" not in title_norm and "senior" not in title_norm:
        score += 12.0
        concerns.append("outside JD experience band")
    if title_score >= 30.0 and career_score < 35.0 and skills_score < 25.0:
        score += 14.0
        concerns.append("title-heavy profile")
    elif title_score >= 35.0 and career_score + skills_score < 90.0:
        score += 8.0
        concerns.append("title-evidence gap")
    return score, concerns


def extract_features(candidate: dict[str, Any]) -> CandidateFeatures:
    profile = candidate["profile"]
    title = profile.get("current_title", "").strip()
    title_norm = norm(title)
    years = float(profile.get("years_of_experience") or 0.0)
    headline = norm(profile.get("headline", ""))
    summary = norm(profile.get("summary", ""))
    summary_years = extract_summary_years(profile.get("summary", ""))

    title_score = exact_or_keyword_title_score(title_norm)
    if 5.0 <= years <= 9.0:
        title_score += 5.0
    elif 4.0 <= years < 5.0 or 9.0 < years <= 11.0:
        title_score -= 1.0
    elif years < 4.0 or years > 12.0:
        title_score -= 8.0

    combined_history = " ".join(
        norm(
            " ".join(
                [
                    item.get("title", ""),
                    item.get("description", ""),
                    item.get("industry", ""),
                    item.get("company", ""),
                ]
            )
        )
        for item in candidate.get("career_history", [])
    )
    career_score, career_hits = count_phrase_score(combined_history, CAREER_POSITIVE_PHRASES)
    summary_score, summary_hits = count_phrase_score(f"{headline} {summary}", CAREER_POSITIVE_PHRASES)
    career_score += summary_score * 0.7

    research_penalty, _ = count_phrase_score(f"{headline} {summary}", RESEARCH_NEGATIVE_PHRASES)
    side_project_penalty, side_hits = count_phrase_score(summary, SUMMARY_NEGATIVE_PHRASES)

    skills_score, skill_hits, expert_count, zero_duration_expert_count = skill_signal(candidate)
    company_score, has_product, consulting_only = company_signal(candidate)
    location_score, location_hits = location_signal(candidate)
    behavior_score, behavior_multiplier, behavior_hits, behavior_concerns = behavior_signal(candidate)

    evaluation_score = 6.0 if contains_any(combined_history, EVAL_TERMS) else 0.0
    coding_score = 3.0 if "python" in summary or "python" in headline else 0.0
    if any("python" == norm(skill.get("name", "")) for skill in candidate.get("skills", [])):
        coding_score += 3.0

    risk_score = side_project_penalty + research_penalty
    concerns: list[str] = []
    if consulting_only:
        risk_score += 7.0
        concerns.append("consulting-heavy background")
    if not has_product:
        risk_score += 2.0
    if research_penalty:
        concerns.append("research-leaning profile")
    if side_project_penalty:
        concerns.append("side-project-heavy AI story")

    suspicious_score, suspicious_concerns = suspicious_penalty(
        candidate,
        years,
        summary_years,
        expert_count,
        zero_duration_expert_count,
        title_norm,
        title_score,
        career_score,
        skills_score,
    )
    risk_score += suspicious_score
    concerns.extend(suspicious_concerns)
    concerns.extend(behavior_concerns)

    base_fit = (
        title_score
        + career_score
        + skills_score
        + company_score
        + location_score
        + evaluation_score
        + coding_score
        + behavior_score
    )
    final_score = (base_fit - risk_score) * behavior_multiplier

    top_evidence = []
    top_evidence.extend(skill_hits[:3])
    top_evidence.extend(hit for hit in career_hits if hit not in {"search", "ranking", "retrieval"})
    top_evidence.extend(location_hits[:1])
    top_evidence.extend(behavior_hits[:2])
    if has_product:
        top_evidence.append("product-company experience")
    if not top_evidence:
        top_evidence.extend(career_hits[:2])
    evidence_seen = set()
    deduped = []
    for item in top_evidence:
        key = norm(item)
        if key and key not in evidence_seen:
            evidence_seen.add(key)
            deduped.append(item)
    top_evidence = deduped

    candidate_id = candidate["candidate_id"]
    return CandidateFeatures(
        candidate_id=candidate_id,
        candidate_num=int(candidate_id.split("_")[1]),
        title=title,
        years=years,
        country=profile.get("country", ""),
        location=profile.get("location", ""),
        current_company=profile.get("current_company", ""),
        title_score=title_score,
        career_score=career_score,
        skills_score=skills_score,
        company_score=company_score,
        location_score=location_score,
        evaluation_score=evaluation_score,
        coding_score=coding_score,
        behavior_score=behavior_score,
        behavior_multiplier=behavior_multiplier,
        risk_score=risk_score,
        suspicious_score=suspicious_score,
        final_score=final_score,
        recruiter_response_rate=float(candidate["redrob_signals"].get("recruiter_response_rate") or 0.0),
        notice_period_days=int(candidate["redrob_signals"].get("notice_period_days") or 0),
        open_to_work=bool(candidate["redrob_signals"].get("open_to_work_flag")),
        top_evidence=top_evidence[:5],
        concerns=list(dict.fromkeys([item for item in concerns if item]))[:4],
    )
