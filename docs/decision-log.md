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

## Pending

- SME review of L1 definitions after Sprint 1 draft
- Confirm RFP PDF download licenses (public procurement docs)
- Sprint 2: synonym harvest from the 3 RFPs
