# 021 — CAD match seeds + demo eval

**Status:** Done  
**SPEC refs:** Phase 4 Lite FR-P4.2  
**Owner:** engineering  

---

## Context

CAD capabilities need deterministic phrase matching and a small eval fixture without weakening LMR mid-doc regression.

## Requirements

1. Add CAD `SEED_PHRASES` in `ingest/extract_l2_synonyms.py`.
2. Add `ontology/samples/demo_cad_requirements.txt` (~10 shall-lines).
3. Extend `ontology/eval_match.py` with `cad_demo` suite (target ≥ 0.80); LMR demo ≥ 0.80 and mid-doc ≥ 0.60 unchanged.
4. Write-up `docs/sprint-p4-021-done.md`.

## Out of scope

- New PDFs, LLM, broad L2 harvest

## Acceptance tests

- [x] cad_demo map_rate ≥ 0.80
- [x] LMR demo + mid_doc still pass
- [x] Write-up exists

## Status

Done — 2026-07-18. cad_demo **1.00**; LMR mid-doc **0.702**.
