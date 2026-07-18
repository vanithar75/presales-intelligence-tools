# 002 — Match quality

**Status:** Done  
**SPEC refs:** FR-2, NFR-1, NFR-4  
**Owner:** engineering  

---

## Context

Deterministic matching works well on the demo fixture but underperforms on early/TOC-heavy PDF pages. Phase 2 needs measurable eval and stronger filtering so real RFP windows meet SPEC targets.

## Requirements

1. Add `ontology/eval_match.py` (or `ingest/eval_match.py`) that reports:
   - Demo fixture map rate (`ontology/samples/demo_requirements.txt`)
   - Holdout synonym self-check (optional lightweight): phrases in holdout resolve to expected `capability_id` at some recall threshold
   - Mid-doc PDF window map rate (pages 21–40 of Erie trunked primary)
2. Harden harvest filters in [ingest/extract_l2_synonyms.py](../ingest/extract_l2_synonyms.py) / shared helpers used by [ingest/matcher.py](../ingest/matcher.py):
   - Skip TOC leader-dot lines
   - Skip pure heading/TOC patterns
   - Skip page headers/footers where detectable
3. Tune seed/name matching only as needed to hit targets **without** LLM by default.
4. Document how to run eval in README or `docs/sprint` note; exit non-zero if below targets (or support `--soft` to report only).

## Out of scope

- Enabling LLM matching by default
- Expanding RFP corpus beyond allowlist
- UI redesign

## Acceptance tests

- [x] `eval_match.py` runs and prints JSON or clear text summary with both suite scores
- [x] Demo suite ≥ 0.80
- [x] Mid-doc suite ≥ 0.50 **or** decision-log records a tracked gap with next actions (SPEC allows documenting gap if filed)
- [x] `validate_l1|l2|l3` still OK
- [x] Matcher still returns MSI coverage for mapped hits

## Implementation notes (files)

- [ingest/matcher.py](../ingest/matcher.py)
- [ingest/extract_l2_synonyms.py](../ingest/extract_l2_synonyms.py)
- [ingest/match_rfp.py](../ingest/match_rfp.py)
- New: `ontology/eval_match.py`
- [ontology/samples/demo_requirements.txt](../ontology/samples/demo_requirements.txt)
- [data/rfp/](../data/rfp/) (local PDFs required for mid-doc eval)
- Write-up: [docs/sprint-p2-002-done.md](../docs/sprint-p2-002-done.md)

## Status

Done — 2026-07-12. Demo **1.00**, mid-doc **0.545**.
