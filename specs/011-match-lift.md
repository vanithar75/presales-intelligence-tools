# 011 — Match quality lift

**Status:** Done  
**SPEC refs:** Phase 3 Lite FR-P3.2  
**Owner:** engineering  

---

## Context

Phase 2 mid-doc Erie map rate is ~0.545 (target was ≥0.50). Phase 3 Lite raises the bar to ≥0.60 using deterministic seeds only.

## Requirements

1. Run `ontology/eval_match.py --json`; bucket unmapped mid-doc themes.
2. Add deterministic `SEED_PHRASES` in `ingest/extract_l2_synonyms.py` (matcher already imports them).
3. If still short of 0.60, add a small curated L2 synonym set (same allowlisted PDFs only — no crawl, no LLM).
4. Update eval mid-doc target to **0.60**; demo remains ≥0.80.
5. Document results in `docs/sprint-p3-011-done.md`.

## Out of scope

- `--llm` matching, new RFP PDFs, threshold thrashing that hurts precision

## Acceptance tests

- [x] Demo map_rate ≥ 0.80
- [x] Mid-doc Erie pp21–40 map_rate ≥ 0.60
- [x] `eval_match.py` exits 0 (without `--soft`)
- [x] Write-up exists

## Implementation notes (files)

- `ingest/extract_l2_synonyms.py` — Phase-3 seed block
- `ontology/eval_match.py` — mid-doc target 0.60
- `docs/sprint-p3-011-done.md`

## Status

Done — 2026-07-18. Mid-doc **0.702**; demo **1.00**.
