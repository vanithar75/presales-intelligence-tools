# Phase 4 Lite / 021 — CAD match seeds + demo eval (done)

**Date:** 2026-07-18  
**Spec:** [specs/021-cad-match.md](../specs/021-cad-match.md)

## Results

| Suite | Target | Result |
|-------|--------|--------|
| LMR demo | ≥ 0.80 | **1.00** |
| Mid-doc Erie | ≥ 0.60 | **0.702** |
| CAD demo | ≥ 0.80 | **1.00** (10/10) |

## How to run

```bash
py -3.12 ontology/eval_match.py
py -3.12 ontology/eval_match.py --json
```

## What changed

- CAD `SEED_PHRASES` in `ingest/extract_l2_synonyms.py`
- `ontology/samples/demo_cad_requirements.txt`
- `cad_demo` suite in `ontology/eval_match.py`
