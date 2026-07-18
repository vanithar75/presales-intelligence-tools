# 022 — CAD publish top-N

**Status:** Done  
**SPEC refs:** Phase 4 Lite FR-P4.3  
**Owner:** engineering  

---

## Context

Governed publish of a CAD bid-desk priority set after ontology + match seeds exist.

## Requirements

1. `ontology/top15_cad.json` with ≥15 CAD aliases.
2. `publish_l1.py --priority-file ontology/top15_cad.json` (sprint P4-022).
3. ≥15 CAD capabilities `published`; LMR published still ≥75.
4. Decision-log entry; `validate_l1.py` OK.

## Out of scope

- Mass-publish all CAD drafts; other stub verticals

## Acceptance tests

- [x] ≥15 CAD published
- [x] LMR published ≥75 (total published **90** = 75 LMR + 15 CAD)
- [x] Validators OK

## Status

Done — 2026-07-18. Catalog `schema_version` **1.4**, sprint **P4-022**, **15** CAD published.
