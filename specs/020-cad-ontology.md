# 020 — CAD ontology expand

**Status:** Done  
**SPEC refs:** Phase 4 Lite FR-P4.1  
**Owner:** engineering  

---

## Context

CAD existed as five `stub` rows without aliases. Phase 4 Lite promotes them to `draft`, adds aliases, and appends CAD capabilities for bid-desk coverage — without regenerating L1 or touching LMR publish.

## Requirements

1. CLI `ontology/expand_cad_l1.py` (append/promote only; never rewrite LMR statuses).
2. Promote 5 `PLAT.CAD.*` stubs → `draft` with `CAD.*` aliases; promote `APP.FIELD.MOBILE_CAD` → draft with alias.
3. Append enough new `PSERS.PLAT.CAD.*` drafts that CAD-vertical count ≥ **25**.
4. Keep non-CAD stubs so `validate_l1.py` still has stubs ≥ 20.
5. LMR `published` count remains ≥ 75.

## Out of scope

- `generate_l1.py` regenerate; NG911/Sensors/MCX trees; publishing CAD (slice 022)

## Acceptance tests

- [x] ≥25 capabilities with `vertical=CAD` (or CAD plat IDs) at draft/published
- [x] `validate_l1.py` OK
- [x] LMR published ≥ 75 unchanged

## Implementation notes

- `ontology/expand_cad_l1.py`, `ontology/l1_capabilities.json` — schema **1.3**, sprint **P4-020**, **25** CAD, **26** stubs remaining, **75** published

## Status

Done — 2026-07-18.
