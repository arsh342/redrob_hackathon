#!/usr/bin/env python3
"""Small-sample Streamlit sandbox for Redrob ranker."""

from __future__ import annotations

import json
import time

import streamlit as st

from src.io_utils import ranked_rows, read_candidates_from_text, submission_csv_text
from src.pipeline import rank_candidates

MAX_CANDIDATES = 100


def count_non_empty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def main() -> None:
    st.set_page_config(page_title="Redrob Ranker Sandbox", page_icon=":mag:", layout="wide")
    st.title("Redrob Ranker Sandbox")
    st.write(
        "Upload a small `.jsonl` candidate sample, run the same local ranker used for submission, "
        "preview the ranked output, and download a CSV."
    )

    top_n = st.number_input("Top N rows", min_value=1, max_value=100, value=25, step=1)
    uploaded = st.file_uploader("Candidate sample (`.jsonl`, max 100 rows)", type=["jsonl"])

    if uploaded is None:
        st.info("Upload a `.jsonl` sample to run the sandbox.")
        return

    raw_text = uploaded.getvalue().decode("utf-8")
    row_count = count_non_empty_lines(raw_text)
    st.write(f"Detected `{row_count}` candidate rows.")

    if row_count == 0:
        st.error("Uploaded file is empty.")
        return
    if row_count > MAX_CANDIDATES:
        st.error(f"Sandbox only accepts up to {MAX_CANDIDATES} candidates.")
        return
    if top_n > row_count:
        st.warning(f"`Top N` reduced from {top_n} to `{row_count}` because upload has fewer rows.")
        top_n = row_count

    if not st.button("Run ranker", type="primary"):
        return

    start = time.perf_counter()
    try:
        candidates = list(read_candidates_from_text(raw_text))
        ranked = rank_candidates(candidates, top_n=int(top_n))
        rows = ranked_rows(ranked)
        csv_text = submission_csv_text(ranked)
        duration = time.perf_counter() - start
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSONL: {exc}")
        return
    except Exception as exc:  # pragma: no cover - UI safety
        st.error(f"Ranking failed: {exc}")
        return

    st.success(f"Ranked {row_count} candidates in {duration:.2f}s.")
    st.dataframe(rows, use_container_width=True)
    st.download_button(
        "Download ranked CSV",
        data=csv_text,
        file_name="sandbox_submission.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
