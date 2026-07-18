# 001 — Ontology governance

**Status:** Done  
**SPEC refs:** FR-1, Phase-2 DoD (published top-50)  
**Owner:** SME + engineering  

---

## Context

L1 capabilities shipped in Sprint 1 as `status: draft`. Bid-desk use needs a governed publish path so IDs stay immutable while quality is certified.

## Requirements

1. Provide a machine-readable list of the SPEC top-50 aliases (may live in `ontology/top50_bid_desk.json` generated from SPEC or maintained as JSON sourced by tooling).
2. Provide CLI `ontology/publish_l1.py` (name flexible) that:
   - Resolves aliases → capability IDs
   - Sets `status` to `published` for selected IDs (default: top-50)
   - Refuses to publish `stub` rows
   - Updates catalog metadata (`schema_version` / `sprint` / `published_at` as appropriate)
3. Document SME review checklist in `docs/l1-publish-checklist.md` (definition clarity, P25 ref if any, stack/mission tags sensible).
4. Append a decision-log entry when a publish batch runs.

## Out of scope

- Rewriting capability definitions en masse
- Publishing CAD/NG911/sensor stubs
- Changing ID scheme or PSERS root

## Acceptance tests

- [x] Running publish on top-50 results in ≥50 L1 rows with `status=published` (exact count = successfully resolved aliases)
- [x] `validate_l1.py` still OK after publish
- [x] Attempting to publish a stub ID fails or skips with clear message
- [x] `docs/decision-log.md` has a publish batch entry
- [x] Checklist doc exists

## Implementation notes (files)

- [ontology/l1_capabilities.json](../ontology/l1_capabilities.json)
- [ontology/generate_l1.py](../ontology/generate_l1.py) — regenerate resets status; re-run publish after regenerate
- New: `ontology/publish_l1.py`, `ontology/top50_bid_desk.json`, `docs/l1-publish-checklist.md`
- [docs/decision-log.md](../docs/decision-log.md)

## Status

Done — 2026-07-12. Catalog `schema_version` **1.1**, sprint **P2-001**, **50** published.
