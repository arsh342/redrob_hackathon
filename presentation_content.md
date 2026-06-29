# Redrob Hackathon PPT Content

Use this text as slide notes or direct copy into PPT. Replace placeholders in first slide.

## Team Name

- **Team Name:** `[fill in]`
- **Problem Statement:** Rank 100,000 candidates against JD for `Senior AI Engineer - Founding Team` and return top 100 with clear reasoning.
- **Team Leader Name:** `[fill in]`

## Solution Overview

Our solution is deterministic CPU-only candidate ranker. It reads candidate JSONL, extracts JD-aligned signals, scores each profile with transparent heuristics, selects top 100 with deterministic tie-breaks, and writes submission CSV with 1–2 sentence reasoning per candidate.

What makes it different from traditional matching systems:

- It does not chase keyword count.
- It weighs real evidence: search, retrieval, ranking, recommendation, Python, evaluation literacy, product-company history, India fit, and availability.
- It penalizes trap patterns: consulting-only profiles, side-project-only GenAI stories, stale profiles, suspicious timelines, and inflated skill claims.
- It explains each ranking using only facts present in profile.

## JD Understanding & Candidate Evaluation

Key JD requirements:

- Strong AI/ML engineering depth
- Search / retrieval / ranking / recommendation experience
- Production mindset, not just theory
- Python and applied ML systems work
- Good availability and recruiter responsiveness
- India-based or willing to relocate

Most important signals:

- Current title and recent career history
- Evidence of search, ranking, retrieval, vector search, recommendations
- Skills like Python, FAISS, Elasticsearch, OpenSearch, Pinecone, Qdrant, Weaviate, NDCG, MRR, MAP, A/B testing
- Product-company background
- Open to work, recent activity, notice period, recruiter response rate

Fit beyond keyword matching:

- Career-history phrases matter more than title alone
- Suspicious profiles get penalized if timeline or skill claims look impossible
- Summary text is used with caution; weak GenAI buzzword-only summaries do not rescue weak profiles
- Behavior signals modify fit but cannot fully rescue bad role fit

## Ranking Methodology

System flow:

1. Parse candidate JSONL.
2. Extract structured features from profile, skills, career history, and redrob signals.
3. Compute:
   - title score
   - career relevance score
   - skills score
   - company score
   - location score
   - evaluation score
   - coding score
   - behavior score
   - risk score
   - suspicious-profile penalty
4. Combine into final score:

```text
final_score = (base_fit_score - risk_score) * behavioral_modifier
```

Algorithms / heuristics used:

- Rule-based scoring
- Deterministic heap-based top-k selection
- Fixed tie-break order
- Reasoning generation from extracted evidence only

Signal combination:

- Positive fit signals raise base score
- Risk signals subtract from score
- Behavioral signals act as multiplier
- Final ranking sorts by score, then career relevance, then lower risk, then recruiter response rate, then shorter notice period, then candidate id

## Explainability & Data Validation

Ranking decisions are explained by:

- strongest matched skills
- strongest career-history evidence
- location / availability signal
- one main concern when profile has a clear weakness

Hallucination prevention:

- Reasoning strings use only extracted facts
- No unsupported skills or claims added
- Candidate-specific evidence is deduplicated and capped
- If no strong evidence exists, reasoning falls back to honest generic ML-systems phrasing

Handling inconsistent or suspicious profiles:

- Penalize experience/title mismatch
- Penalize profile-years mismatch
- Penalize many expert skills with zero duration
- Penalize consulting-heavy and keyword-stuffer patterns
- Penalize stale activity and weak recruiter response

Validation:

- Submission CSV passes `validate_submission.py`
- Ranking is deterministic across reruns
- Output format stays fixed: `candidate_id,rank,score,reasoning`

## End-to-End Workflow

1. Load JD and candidate dataset.
2. Stream each candidate record.
3. Normalize text fields.
4. Extract fit, behavior, and risk features.
5. Score candidate.
6. Keep top candidates in deterministic heap.
7. Generate reasoning only for shortlisted rows.
8. Write final CSV.
9. Validate submission file before portal upload.

## System Architecture

```text
candidate.jsonl
      |
      v
src/io_utils.py  -> stream read
      |
      v
src/features.py  -> extract signals
      |
      v
src/scoring.py   -> deterministic top-k
      |
      v
src/reasoning.py -> short explainability text
      |
      v
rank.py / app.py -> CLI + Streamlit sandbox
      |
      v
submission CSV
```

## Results & Performance

Observed results on current baseline:

- Submission validation: **passed**
- Full ranking runtime: **8.716 seconds**
- Top 100 count: **100**
- Top titles heavily concentrated in:
  - Recommendation Systems Engineer
  - Search Engineer
  - Applied ML Engineer
  - Machine Learning Engineer
  - AI Engineer
  - NLP Engineer
- Top 100 contains **100 India-based candidates**
- Open-to-work in top 100: **100**
- Notice buckets:
  - 0–30 days: **37**
  - 31–60 days: **49**
  - 61–90 days: **14**
  - 91+ days: **0**

After tighter risk tuning, top 100 is cleaner:

- India-based: **100**
- non-India: **0**
- recruiter response < 0.5: **0**
- long notice (> 90 days): **0**

What these results show:

- Ranker surfaces real JD-aligned profiles, not generic AI buzzword profiles
- Availability and location signals help shortlist practical hires
- Deterministic design fits hackathon compute limits

Compute constraints:

- CPU only
- No network during ranking
- Full run finishes in seconds, far under 5-minute limit

## Technologies Used

- **Python**: main ranking pipeline and CLI
- **Streamlit**: sandbox demo for small uploaded samples
- **Standard library**: CSV, JSONL, heap, dataclasses, argparse
- **Markdown**: documentation and PPT content

Why these:

- Fast to run
- Easy to explain
- No heavy infrastructure
- Reproducible and portable

## Submission Assets

- **GitHub Repository:** this repo
- **Demo Video:** `[add link if needed]`
- **Other supporting assets:** `outputs/baseline_submission_v4.csv`, `validate_submission.py`, Streamlit sandbox in `app.py`

## Final Note

Before portal submission, do one last manual review of borderline top-100 candidates and honeypot risk. Packaging is close to submit-ready.
