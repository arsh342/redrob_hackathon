#!/usr/bin/env python3
"""Audit a submission CSV against source candidate profiles."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load_submission_ids(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [row["candidate_id"] for row in csv.DictReader(handle)]


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/audit_submission.py <submission.csv> <candidates.jsonl>")
        raise SystemExit(1)

    submission_path = Path(sys.argv[1])
    candidates_path = Path(sys.argv[2])
    wanted = load_submission_ids(submission_path)
    wanted_set = set(wanted)

    title_counter = Counter()
    company_counter = Counter()
    concern_counter = Counter()
    country_counter = Counter()
    open_count = 0
    notice_buckets = Counter()
    github_missing = 0
    response_lt_05 = 0
    rows = []

    with candidates_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            candidate = json.loads(line)
            cid = candidate["candidate_id"]
            if cid not in wanted_set:
                continue
            profile = candidate["profile"]
            signals = candidate["redrob_signals"]
            title = profile["current_title"]
            title_counter[title] += 1
            company_counter[profile["current_company"]] += 1
            country_counter[profile["country"]] += 1

            if signals["open_to_work_flag"]:
                open_count += 1
            else:
                concern_counter["not_open_to_work"] += 1

            notice = int(signals["notice_period_days"])
            if notice <= 30:
                notice_buckets["0_30"] += 1
            elif notice <= 60:
                notice_buckets["31_60"] += 1
            elif notice <= 90:
                notice_buckets["61_90"] += 1
            else:
                notice_buckets["91_plus"] += 1

            if float(signals["github_activity_score"]) == -1:
                github_missing += 1
                concern_counter["github_missing"] += 1
            if float(signals["recruiter_response_rate"]) < 0.5:
                response_lt_05 += 1
                concern_counter["response_lt_0_5"] += 1

            rows.append(
                (
                    cid,
                    title,
                    profile["current_company"],
                    profile["location"],
                    profile["years_of_experience"],
                    signals["open_to_work_flag"],
                    notice,
                    signals["recruiter_response_rate"],
                    signals["github_activity_score"],
                )
            )

    order = {cid: idx for idx, cid in enumerate(wanted)}
    rows.sort(key=lambda item: order[item[0]])

    print("summary")
    print(" top_100_count:", len(rows))
    print(" open_to_work:", open_count)
    print(" github_missing:", github_missing)
    print(" recruiter_response_lt_0.5:", response_lt_05)
    print(" countries:", country_counter.most_common())
    print(" notice_buckets:", dict(notice_buckets))
    print(" top_titles:", title_counter.most_common(15))
    print(" top_companies:", company_counter.most_common(15))
    print(" concerns:", concern_counter.most_common())
    print()
    print("top_20")
    for idx, row in enumerate(rows[:20], start=1):
        print(idx, row)


if __name__ == "__main__":
    main()
