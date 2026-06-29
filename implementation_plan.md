# Implementation Plan

## Goal

Build a reproducible candidate-ranking system for Redrob Hackathon that:

- reads `candidates.jsonl`
- ranks top 100 candidates for `Senior AI Engineer - Founding Team`
- writes valid submission CSV
- runs within:
  - `<= 5 min` wall clock
  - `<= 16 GB` RAM
  - CPU only
  - no network
- survives Stage 3, 4, and 5 review

## Success Criteria

- `validate_submission.py` passes with zero errors
- top 100 has low obvious false-positive rate
- top 100 has low honeypot risk
- ranking logic is explainable and defendable
- reasoning strings are specific, honest, non-hallucinated, and rank-consistent
- repo contains one-command reproduction path

## Hard Constraints

## Submission Format

- output file must be CSV
- header must be exactly:

```text
candidate_id,rank,score,reasoning
```

- exactly 100 data rows
- ranks `1..100` exactly once each
- each `candidate_id` unique
- scores must be non-increasing by rank
- equal-score tie-break must be deterministic

## Compute Constraints

- no hosted LLM/API calls during ranking
- no GPU during ranking
- no oversized intermediate artifacts
- final ranking path must run end-to-end on local CPU machine

## Review Constraints

### Stage 3

- code must reproduce result
- ranking logic must fit compute budget
- top 100 honeypot rate must stay `<= 10%`

### Stage 4

- reasonings sampled manually
- hallucinations, templated text, empty text, weak JD linkage get penalized
- methodology must look like real engineering, not keyword spam

### Stage 5

- architecture must be explainable live
- every feature and tradeoff must be defendable

## Project Reality

This bundle is not app codebase. It is challenge input bundle:

- docs
- schema
- sample data
- full candidate dataset
- CSV validator

Need build ranking pipeline from scratch.

## Core Ranking Thesis

Do **not** optimize for AI keyword count.

Optimize for evidence of:

- shipped retrieval/search/ranking/recommendation systems
- applied ML in production
- product-engineering judgment
- strong Python / ML systems depth
- evaluation literacy
- candidate availability / recruiter responsiveness

Down-rank:

- obvious keyword stuffers
- adjacent non-target roles with side-project GenAI only
- consulting-only careers without product evidence
- inactive or hard-to-close candidates
- profiles with impossible or suspicious combinations

## Candidate Evaluation Framework

Final score should combine:

```text
final_score =
base_fit_score
+ evidence_bonus
- risk_penalty

then multiplied by behavioral_modifier
```

Where:

- `base_fit_score` = title + career + skills + summary/JD alignment
- `evidence_bonus` = strong proof of shipped search/ranking/retrieval systems
- `risk_penalty` = false-positive patterns, consulting-only patterns, side-project-only patterns, suspicious profile patterns
- `behavioral_modifier` = availability, recency, response rate, notice period, recruiter interest

## Workstreams

## 1. Contract Lock

### Output

- exact CSV writer
- deterministic sorting and tie-break logic
- submission validator wrapper

### Tasks

- mirror `validate_submission.py` rules in internal checks
- define score formatting strategy
- define reasoning length and style guardrails

## 2. Dataset Profiling

### Goal

Map real field distributions before freezing feature logic.

### Questions

- how many candidates look directly relevant by title?
- how many have retrieval/search/ranking signals only in career text?
- how common are consulting-only backgrounds?
- how strong are India location / relocation / notice signals?
- what patterns correlate with obvious trap candidates?

### Profiling Outputs

- title frequency tables
- company/industry frequency tables
- skill frequency tables
- behavioral signal distributions
- location and notice-period distributions
- shortlist of suspicious-profile heuristics

## 3. Feature Design

### A. Positive Features

#### Direct role alignment

- current title or recent titles like:
  - `Recommendation Systems Engineer`
  - `Search Engineer`
  - `Machine Learning Engineer`
  - `Applied ML Engineer`
  - `NLP Engineer`
  - `Data Scientist` with strong ranking/retrieval evidence
  - `Senior Software Engineer (ML)`
  - `AI Engineer` only when backed by real production evidence

#### Career-history evidence

- shipped search, ranking, retrieval, recommendation, matching systems
- vector search / hybrid retrieval / embeddings / ANN / semantic search
- production deployment, monitoring, index refresh, quality regression handling
- marketplace / HR-tech / adtech / ecommerce / feed/recs/search relevance
- strong recency of relevant work

#### Skill evidence

- `FAISS`, `Elasticsearch`, `OpenSearch`, `Pinecone`, `Qdrant`, `Weaviate`, `Milvus`
- `Embeddings`, `Information Retrieval`, `Semantic Search`
- `NDCG`, `MRR`, `MAP`, `A/B testing`, `ranking evaluation`
- `Python`, `MLflow`, model serving / MLOps stack

#### Company-type evidence

- product companies > pure IT services
- known scale/search/recommendation-heavy companies get bonus
- startup / product ownership may get bonus when role evidence is strong

#### Availability / logistics

- India preferred
- Pune / Noida / Hyderabad / Bangalore / Mumbai / Delhi NCR positive
- willing to relocate positive
- shorter notice positive
- open to work positive

### B. Negative Features

#### Strong false-positive patterns

- non-target roles with inflated AI skill lists:
  - `Marketing Manager`
  - `Graphic Designer`
  - `Content Writer`
  - `HR Manager`
  - `Sales Executive`
  - similar

- summary says:
  - "recently exploring GenAI"
  - "online courses on RAG"
  - "side projects with LangChain/OpenAI API"
  - but no production evidence in career history

#### JD disqualifier patterns

- pure research without production deployment
- senior/staff/architect profile with little recent coding evidence
- consulting-only career with no product-company history
- CV/speech/robotics-heavy profile without NLP/IR evidence

#### Risk patterns

- long notice period
- inactive for long time
- poor recruiter response rate
- weak interview completion
- no relocation and wrong geography

### C. Honeypot / Suspicion Features

Need heuristic penalties for:

- impossible experience timelines
- too many expert skills with tiny durations
- very high claim density with weak career support
- profile text inconsistent with structured history
- career chronology anomalies

These should be penalties, not brittle hard filters.

## 4. Scoring Model Design

## Model Shape

Phase 1 should use transparent weighted scoring.

Why:

- fast
- reproducible
- explainable in interview
- easy to tune
- low infra risk

### Proposed score blocks

```text
fit_score =
  title_score
+ career_relevance_score
+ skills_score
+ summary_signal_score
+ company_signal_score
+ location_score
+ recency_score
+ coding_signal_score
+ eval_signal_score

risk_score =
  keyword_stuffer_penalty
+ side_project_only_penalty
+ consulting_only_penalty
+ suspicious_profile_penalty
+ notice_penalty
+ inactivity_penalty

behavioral_modifier =
  f(open_to_work, last_active_date, recruiter_response_rate,
    avg_response_time_hours, saved_by_recruiters_30d,
    search_appearance_30d, interview_completion_rate,
    github_activity_score)

final_score = (fit_score - risk_score) * behavioral_modifier
```

### Tie-break Order

1. higher `final_score`
2. higher `career_relevance_score`
3. lower `risk_score`
4. better `recruiter_response_rate`
5. shorter `notice_period_days`
6. ascending `candidate_id`

## 5. Pipeline Architecture

## Files To Build

- `rank.py`
- `src/` package for scoring and parsing
- `tests/` or lightweight validation scripts
- `README.md`
- `submission_metadata.yaml`

### Likely module split

- `src/jd_profile.py`
  - encoded JD priorities and negatives
- `src/features.py`
  - candidate feature extraction
- `src/scoring.py`
  - weighted scoring logic
- `src/reasoning.py`
  - reasoning generation from feature summary
- `src/io.py`
  - JSONL stream reader and CSV writer
- `src/validators.py`
  - internal sanity checks

## Runtime Strategy

- stream JSONL line by line
- avoid loading all 100k full profiles if not needed
- keep min-heap or sorted shortlist for top candidates
- store compact per-candidate feature summaries
- generate final reasonings only for shortlisted top candidates

## 6. Reasoning Generation Plan

Reasoning must be:

- 1-2 sentences
- specific
- JD-connected
- honest about tradeoffs
- different across candidates

### Reasoning Inputs

- years of experience
- current/recent title
- strongest retrieval/ranking/search evidence
- strongest company/product signal
- location / relocation fit
- availability / notice / response signal
- one concern if needed

### Reasoning Rules

- never mention skill not present in profile
- never praise weak candidate like top-5 if ranked low
- include concern when candidate has one:
  - long notice
  - consulting-heavy background
  - adjacent title
  - weak recent activity

## 7. Validation Plan

## Functional Validation

- run `validate_submission.py`
- ensure stable deterministic output across reruns
- check top 100 all exist in source data

## Ranking Validation

- inspect top 20 manually
- inspect bottom 20 of top 100 manually
- inspect candidates just below cutoff
- count obvious false positives
- sample suspicious profiles for honeypot-like traits

## Reasoning Validation

- sample 10 reasonings like Stage 4
- verify:
  - specific facts present
  - JD linkage present
  - no hallucinations
  - varied wording
  - tone matches rank

## Performance Validation

- benchmark end-to-end runtime on full `candidates.jsonl`
- inspect RAM usage
- confirm no network dependency

## 8. Packaging Plan

## Repo Contents

- reproducible code
- dependency file
- README with one-command run
- final CSV output
- `submission_metadata.yaml`

## README Must Cover

- setup
- exact reproduce command
- expected runtime
- precomputation note if any
- sandbox/demo usage
- methodology summary

## Sandbox Plan

Need small-sample hosted demo:

- likely Streamlit or Colab
- upload/sample input of <=100 candidates
- run same scoring pipeline
- emit ranked CSV

Use same scoring codepath when possible.

## 9. Tuning Strategy

Tune in this order:

1. eliminate obvious false positives
2. promote real retrieval/ranking/search builders
3. calibrate activity/availability modifier
4. tighten suspicious-profile penalties
5. improve reasoning specificity

Do **not** overfit to pretty titles alone.
Career evidence beats title.
Behavior modifies fit; should not fully rescue bad-fit profiles.

## 10. Risks

## Technical Risks

- too much reliance on skill-list keywords
- score rules too brittle for varied candidate text
- runtime blowup from expensive text processing
- non-deterministic sorting / tie handling

## Evaluation Risks

- top 100 contains adjacent-role keyword stuffers
- real strong candidates missed because titles are generic
- honeypots leak into shortlist
- reasoning sounds templated or hallucinates

## Process Risks

- weak README / reproduction story
- no sandbox by submission time
- code not defendable in interview

## 11. Execution Order

## Phase 1

- profile dataset
- define JD-aligned lexicons
- implement transparent feature extractor

## Phase 2

- implement weighted ranker
- produce first valid CSV
- inspect top/bottom candidates

## Phase 3

- tighten penalties
- improve behavioral modifier
- add suspicion heuristics

## Phase 4

- implement reasoning generator
- validate Stage 4 criteria

## Phase 5

- benchmark full run
- package README + metadata + sandbox

## 12. Definition of Done

Done when all true:

- ranking runs on full dataset within budget
- output CSV passes validator
- top candidates look like real JD fits
- obvious trap candidates mostly excluded
- reasoning is specific and non-hallucinated
- repo ready for organizer reproduction
- methodology defendable without hand-waving
