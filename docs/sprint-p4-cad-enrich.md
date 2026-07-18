# CAD enrichment wave 2 (post Phase 4 Lite)

**Date:** 2026-07-18

## What changed

- Appended **18** CAD capabilities via `ontology/expand_cad_l1.py` (wave 2): duplicate check, tow/impound, warrants, mutual aid, fire run cards, EMS protocol, hospital status, traffic stop, pursuit, evidence notes, media hold, training mode, failover, RBAC, callback, vehicle assign, alarm interface, unit chat.
- Published **20** more CAD caps (`ontology/top_cad_wave2.json`) → **35** CAD published total.
- Expanded `demo_cad_requirements.txt` to 20 lines; cad_demo map rate **1.00**.
- CAD-scoped seed preference in `ingest/matcher.py` (0.95 when phrase contains `cad`).
- Mapped **20** CAD capabilities to `MSI.CC.COMMAND` in L3 (143 mappings total).

## Counts

| Metric | Value |
|--------|-------|
| CAD plat caps | 43 (+ mobile client) |
| CAD published | 35 |
| Total L1 published | 110 |
| Catalog schema | 1.6 |
| cad_demo | 1.00 |
| LMR mid-doc | 0.702 (unchanged) |
