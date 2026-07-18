# Phase 2 / 002 — Match quality (done)

**Date:** 2026-07-12  
**Spec:** [specs/002-match-quality.md](../specs/002-match-quality.md)

## Results

| Suite | Target | Result |
|-------|--------|--------|
| Demo fixture | ≥ 0.80 | **1.00** (10/10) |
| Mid-doc Erie pp 21–40 | ≥ 0.50 | **0.545** (205/376) |
| Holdout recall (info) | — | 0.976 (41/42) |

## How to run

```bash
py -3.12 ontology/eval_match.py
py -3.12 ontology/eval_match.py --json
py -3.12 ontology/eval_match.py --soft   # report only, always exit 0
```

Requires allowlisted PDFs under `data/rfp/` (see `ingest/download_rfps.py`).

## What changed

- TOC / header / admin boilerplate filters in `ingest/extract_l2_synonyms.py` (`is_boilerplate_phrase`, `strip_page_chrome`)
- Additional deterministic seeds for mid-doc themes (antenna, fault tolerance, docs, NMS, etc.)
- Slightly looser L2 Jaccard threshold in `ingest/matcher.py`
- `match_pdf(..., start_page=, end_page=)` for windowed eval
- New harness: `ontology/eval_match.py`
