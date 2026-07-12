# Sprint 0 + Sprint 1 completion

**Date:** 2026-07-12  
**Mode:** Cost-optimized Auto (on-demand spending disabled by user)

## Sprint 0 — Done

- [x] Repo scaffold (`ontology/`, `ingest/`, `app/`, `data/rfp/`, `docs/`, `sql/`)
- [x] PSERS root + facets frozen (`docs/psers-root.md`, `ontology/facets.json`)
- [x] Postgres DDL with `stack_class` + `mission_tags` (`sql/schema.sql`)
- [x] Decision log (`docs/decision-log.md`)
- [x] Allowlisted RFP download script + 3 PDFs in `data/rfp/`
- [x] README + `.gitignore` + git init

## Sprint 1 — Done (draft)

- [x] LMR L1 capabilities: **192** (`status=draft`)
- [x] PSERS stubs (CAD/NG911/Sensors/MCX/XCUT): **32** (`status=stub`)
- [x] Catalog file: `ontology/l1_capabilities.json` (total **224**)
- [x] Generator + validator: `ontology/generate_l1.py`, `ontology/validate_l1.py`
- [ ] SME review / publish lock (human) — next gate before Sprint 2

## Verify locally

```bash
python ontology/validate_l1.py
python -c "import json; print(json.load(open('ontology/l1_capabilities.json',encoding='utf-8'))['counts'])"
```

## Not in S0/S1

- L2 synonym harvest (Sprint 2) — **completed separately; see sprint-s2-done.md**
- MSI L3 mappings (Sprint 3)
- Match UI (Sprint 4)
