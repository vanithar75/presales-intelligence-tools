# Decision log

## 2026-07-12 — Sprint 0 kickoff

- **Root:** `PSERS` (not LMR, not Technology, not Incident/EIDO).
- **MVP vertical:** LMR deep; CAD/NG911/Sensors/MCX stubbed.
- **L2 corpus (fixed):** ECSO Jackson County Functional Spec; Erie Trunked System RFP 2026; Erie Subscriber RFP 2026.
- **L3:** Motorola Solutions only for MVP.
- **Stack:** Postgres DDL prepared; runtime DB optional until Sprint 3.
- **Cursor:** Auto/Composer preferred; on-demand spending disabled by user.

## 2026-07-12 — Sprint 0 + Sprint 1 completed (draft)

- Repo scaffolded; RFPs downloaded to `data/rfp/`.
- L1 catalog generated: **192** LMR draft capabilities + **32** stubs = **224** total in `ontology/l1_capabilities.json`.
- Human SME review still required before marking L1 `published`.

## 2026-07-12 — Sprint 2 completed (L2 synonyms)

- Deterministic PDF harvest + seed/name matching (no LLM) via `ingest/extract_l2_synonyms.py`.
- **492** main synonyms, **42** holdout, **58** L1 capabilities covered; top-15 alias coverage **13/15**.
- Status `auto_accepted` pending SME spot-check.

## 2026-07-12 — Sprint 3 completed (MSI L3 + match API)

- 20 MSI products; 123 product↔capability mappings (116 L1 caps).
- Deterministic matcher CLI + FastAPI (`app/match_api.py`).
- Sample outputs in `ontology/samples/`.

## 2026-07-12 — Sprint 4 completed (analyst UI)

- FastAPI UI at `/` with PDF upload, paste/demo fixture, MSI coverage, synonym feedback JSONL.
- MVP end-to-end demo path complete for LMR vertical.

## Pending

- SME review of L1 definitions after Sprint 1 draft
- SME spot-check of L2 auto_accepted synonyms
- Stronger MSI datasheet citations on L3 rows
- Post-MVP verticals (CAD/sensors/MCX depth)
