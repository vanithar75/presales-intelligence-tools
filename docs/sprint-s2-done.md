# Sprint 2 completion — L2 synonyms

**Date:** 2026-07-12  
**Mode:** Cost-optimized Auto (deterministic extract/match — no LLM API calls)

## Done

- [x] PDF shall-statement harvest from 3 allowlisted RFPs (`ingest/extract_l2_synonyms.py`)
- [x] Map phrases → L1 via curated seed regex + capability name match
- [x] Near-duplicate collapse
- [x] Holdout set (~10% by phrase hash)
- [x] Validator `ontology/validate_l2.py`

## Counts

| Metric | Value |
|--------|-------|
| Main synonyms | **492** |
| Holdout | **42** |
| Capabilities with ≥1 synonym | **58** |
| Top-15 bid-desk alias coverage | **13 / 15** |
| Unmapped shall-like phrases (raw) | 3640 (sample in `l2_unmapped.json`) |

## Outputs

- `ontology/l2_synonyms.json`
- `ontology/l2_synonyms_holdout.json` (do not tune on)
- `ontology/l2_unmapped.json`

## Verify

```bash
py -3.12 ontology/validate_l2.py
```

## Notes / follow-ups

- Synonyms are `auto_accepted` — SME spot-check recommended before Sprint 3 matching eval.
- Coverage skewed toward frequently mentioned RFP themes (console, NMS, training, backhaul, simulcast).
- Expanding seeds can raise caps_covered in a later pass without new RFPs.
