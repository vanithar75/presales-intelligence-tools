# Phase 3 Lite / 011 — Match quality lift (done)

**Date:** 2026-07-18  
**Spec:** [specs/011-match-lift.md](../specs/011-match-lift.md)

## Results

| Suite | Target | Result |
|-------|--------|--------|
| Demo fixture | ≥ 0.80 | **1.00** (10/10) |
| Mid-doc Erie pp 21–40 | ≥ 0.60 | **0.702** (264/376) |
| Holdout recall (info) | — | 0.976 (41/42) |

Baseline before lift: mid-doc **0.545** (205/376).

## How to run

```bash
py -3.12 ontology/eval_match.py
py -3.12 ontology/eval_match.py --json
```

## What changed

- Phase-3 deterministic seeds in `ingest/extract_l2_synonyms.py` for generator/UPS/HVAC, racks, NTP/IP plan, multi-couplers/feed lines, remote config, installation compliance, etc.
- `ontology/eval_match.py` mid-doc target raised to **0.60**.
