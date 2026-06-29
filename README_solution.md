# Baseline Ranker

## What this is

Transparent CPU-only baseline ranker for Redrob candidate-ranking challenge.

Design goals:

- deterministic output
- no network
- no GPU
- fast full-dataset run
- explainable scoring

## Files

- `rank.py` - main entrypoint
- `src/features.py` - feature extraction and penalties
- `src/scoring.py` - top-k selection and tie-breaks
- `src/reasoning.py` - CSV reasoning strings
- `scripts/profile_dataset.py` - tuning/profiling helper
- `scripts/audit_submission.py` - submission quality audit helper
- `outputs/baseline_submission_v4.csv` - latest valid baseline output

## Run

```bash
python3 rank.py --candidates candidates.jsonl --out outputs/submission.csv
```

## Sandbox Run

```bash
streamlit run app.py
```

## Validate

```bash
python3 validate_submission.py outputs/submission.csv
```

## Profiling

```bash
python3 scripts/profile_dataset.py
```

## Current approach

Weighted heuristic ranker with:

- positive signals for search / retrieval / recommendation / ranking evidence
- positive signals for product-company experience, Python, evaluation literacy, India fit, and good recruiter-side behavior
- negative signals for keyword-stuffer patterns, side-project-only AI stories, consulting-only backgrounds, inactivity, and long notice periods
- extra penalties for not-open candidates, profile-years mismatch, and non-India/no-relocation profiles

## Notes

- CLI ranker uses standard library only.
- Sandbox adds `streamlit` for hosted demo deployment.
- Full run currently completes in a few seconds on local machine.
- Current output passes CSV validation.
- Still needs final manual review for honeypots/borderline candidates before portal submission.

## Free Sandbox Deploy

Recommended: Streamlit Cloud.

1. Push repo to GitHub.
2. Go to `https://share.streamlit.io/`.
3. Create new app from repo.
4. Set main file to `app.py`.
5. Deploy and copy generated `https://...streamlit.app` link into `submission_metadata.yaml`.
