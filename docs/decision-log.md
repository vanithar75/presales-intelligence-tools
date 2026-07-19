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

## 2026-07-12 — Spec-driven development adopted

- Added root [SPEC.md](../SPEC.md) as Phase-2 authority (quality hardening of LMR vertical).
- Feature slices: `specs/001-ontology-governance.md` … `specs/004-persistence-lite.md`.
- Implementation of FR-1…FR-4 not started; execute one slice at a time per Cursor agent protocol in SPEC.

## Pending

- SME spot-check of published top-50 L1 definitions (checklist: `docs/l1-publish-checklist.md`)
- SME spot-check of L2 auto_accepted synonyms
- Stronger MSI datasheet citations on L3 rows
- Execute Phase-2 slices 001–004 — **complete**
- Post-MVP verticals (CAD/sensors/MCX depth)

## 2026-07-12 — L1 publish batch (published)

- Catalog `schema_version`: **1.1**
- Promoted to `published`: **50** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top50_bid_desk.json` (SPEC §4)
- Sample IDs: PSERS.INFRA.STD.P25_PHASE1, PSERS.INFRA.STD.P25_PHASE2, PSERS.INFRA.STD.DUAL_MODE_FDMA_TDMA, PSERS.INFRA.STD.TRUNKED_OPS, PSERS.INFRA.STD.CONVENTIONAL_OPS, PSERS.INFRA.STD.P25_CAP, PSERS.INFRA.CORE.GEO_REDUNDANT_CORE, PSERS.INFRA.CORE.NO_SPOF (+42 more)

## 2026-07-12 — Phase 2 slice 002 match quality

- Added `ontology/eval_match.py` (demo + mid-doc + holdout).
- Hardened TOC/header/admin filters; expanded deterministic seeds; slight L2 Jaccard loosen.
- Eval: demo map_rate **1.00**; Erie mid-doc pp21–40 **0.545** (target ≥0.50).
- Details: [docs/sprint-p2-002-done.md](sprint-p2-002-done.md).

## 2026-07-12 — Phase 2 slice 003 feedback loop

- Accept/correct upsert `ontology/l2_review_queue.json`; reject stays audit-only for merge.
- CLI `ingest/publish_l2_feedback.py` merges with dedupe → `analyst_accepted` / `match_method: feedback`.
- Verified 492→493 synonyms; second publish no-op; reject excluded.
- Details: [docs/sprint-p2-003-done.md](sprint-p2-003-done.md).

## 2026-07-12 — Phase 2 slice 004 persistence lite

- CLI `ingest/load_postgres.py` upserts L1/L2/L3 into Postgres (`DATABASE_URL`); schema apply optional.
- Added `uq_synonym_cap_phrase` for idempotent synonym upserts; docs in [docs/postgres.md](postgres.md).
- Verified on Docker Postgres 16: 224 caps / 493 syn / 20 products / 123 maps; second import clean.
- Matcher/API remain JSON-backed.

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.2**
- Sprint: **P3-010**
- Promoted to `published`: **25** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top50_wave2.json`
- Sample IDs: PSERS.INFRA.STD.ANALOG_INTEROP, PSERS.INFRA.STD.DMR_TIER2, PSERS.INFRA.STD.DMR_TIER3, PSERS.INFRA.STD.TIA102_SUITE, PSERS.INFRA.STD.COMMON_CHANNEL_OPS, PSERS.INFRA.STD.MIXED_FLEET, PSERS.INFRA.RF.BAND_VHF, PSERS.INFRA.RF.BAND_UHF (+17 more)

## 2026-07-18 — Phase 3 Lite freeze (LMR deepen)

- **Published L1:** **75** (top-50 + wave2 25); catalog `schema_version` **1.2**
- **Match:** demo **1.00**; mid-doc Erie pp21–40 **0.702** (target ≥0.60); see [docs/sprint-p3-011-done.md](sprint-p3-011-done.md)
- **Review queue UI:** `GET /api/review-queue`, `POST /api/review-queue/publish`; panel on analyst UI
- Slices **010–013** Done; deferred: CAD/NG911/Sensors/MCX deep trees, multi-vendor L3, broader RFP crawl, proposal gen
- **Stop here** — next expansion requires amending `SPEC.md`

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.4**
- Sprint: **P4-022**
- Promoted to `published`: **15** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top15_cad.json`
- Sample IDs: PSERS.PLAT.CAD.INCIDENT_CREATE, PSERS.PLAT.CAD.UNIT_STATUS, PSERS.PLAT.CAD.RECOMMENDATION, PSERS.PLAT.CAD.CAD_TO_CAD, PSERS.PLAT.CAD.AVL_DISPLAY, PSERS.APP.FIELD.MOBILE_CAD, PSERS.PLAT.CAD.CALL_TYPE, PSERS.PLAT.CAD.PRIORITY_SOP (+7 more)

## 2026-07-18 — Phase 4 Lite freeze (CAD foundation)

- **CAD ontology:** **25** PLAT.CAD caps (5 stubs promoted + 20 appended); `MOBILE_CAD` promoted; catalog path via `expand_cad_l1.py` (no `generate_l1`)
- **Published:** **90** total (**75** LMR + **15** CAD); schema **1.4**
- **Match:** LMR demo **1.00**; mid-doc **0.702**; cad_demo **1.00**; see [docs/sprint-p4-021-done.md](sprint-p4-021-done.md)
- Slices **020–023** Done; deferred: NG911 / Sensors / MCX deep trees, multi-vendor L3, broader RFP crawl, proposal gen
- **Stop here** — next expansion requires amending `SPEC.md`

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.6**
- Sprint: **P4-CAD-enrich**
- Promoted to `published`: **20** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top_cad_wave2.json`
- Sample IDs: PSERS.PLAT.CAD.AUDIT_LOG, PSERS.PLAT.CAD.INCIDENT_HISTORY, PSERS.PLAT.CAD.MAP_LAYERS, PSERS.PLAT.CAD.NG911_TOUCH, PSERS.PLAT.CAD.PERSON_QUERY, PSERS.PLAT.CAD.RESOURCE_TYPE, PSERS.PLAT.CAD.RMS_INTERFACE, PSERS.PLAT.CAD.ROSTER_SCHEDULE (+12 more)

## 2026-07-18 — CAD enrichment wave 2

- Appended **18** CAD draft capabilities; published **+20** CAD (`top_cad_wave2.json`)
- **CAD published:** **35**; total published **110**; schema **1.6**
- cad_demo **1.00** (20/20); LMR mid-doc still **0.702**
- L3: +20 CommandCentral → CAD maps (143 mappings)
- Details: [docs/sprint-p4-cad-enrich.md](sprint-p4-cad-enrich.md)

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.8**
- Sprint: **P4-NG911**
- Promoted to `published`: **20** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top20_ng911.json`
- Sample IDs: PSERS.PLAT.NG911.CALL_HANDLING, PSERS.PLAT.NG911.EIDO_EXCHANGE, PSERS.PLAT.NG911.TEXT_TO_911, PSERS.PLAT.NG911.MULTIMEDIA, PSERS.PLAT.NG911.ALI_AML, PSERS.PLAT.NG911.SIP_CALL_CONTROL, PSERS.PLAT.NG911.ESRP_ROUTING, PSERS.PLAT.NG911.ECRF_LVF (+12 more)

## 2026-07-18 — NG911 emergency call handling foundation

- Promoted 5 NG911 stubs → draft; appended **20** call-handling caps (`expand_ng911_l1.py`)
- **NG911:** **25** caps, **20** published; total published **130**; schema **1.8**
- ng911_demo **1.00** (18/18); LMR/CAD evals still pass
- L3: +15 CommandCentral → NG911 maps (158 mappings)
- Details: [docs/sprint-p4-ng911.md](sprint-p4-ng911.md)

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.10**
- Sprint: **P5-032**
- Promoted to `published`: **15** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top15_sensors.json`
- Sample IDs: PSERS.SENS.VIDEO.FIXED_CCTV, PSERS.SENS.VIDEO.LIVE_SHARE, PSERS.SENS.VIDEO.BODYWORN, PSERS.PLAT.VMS.VIDEO_MANAGEMENT, PSERS.SENS.VIDEO.VMS_SEARCH, PSERS.SENS.VIDEO.PSAP_LIVESTREAM, PSERS.SENS.VIDEO.BODYWORN_EVIDENCE, PSERS.SENS.IOT.ALPR (+7 more)

## 2026-07-18 — Phase 5 Lite freeze (Sensors foundation)

- Promoted 8 VIDEO/IOT/UAS/VMS stubs → draft; appended **15** sensor caps (`expand_sensors_l1.py`)
- **Sensors:** **23** caps, **15** published; total published **145**; schema **1.10**; stubs **13** (floor ≥10)
- sensors_demo **0.95**; LMR/CAD/NG911 still pass
- L3: +15 CommandCentral sensor maps (173 mappings)
- Slices **030–032** Done; **MCX** still deferred
- Details: [docs/sprint-p5-031-done.md](sprint-p5-031-done.md)
- **Stop here** — next expansion requires amending `SPEC.md`

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.13**
- Sprint: **P6-042**
- Promoted to `published`: **21** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top_cad_wave3.json`
- Sample IDs: PSERS.PLAT.CAD.TOW_IMPOUND, PSERS.PLAT.CAD.TRAFFIC_STOP, PSERS.PLAT.CAD.PURSUIT, PSERS.PLAT.CAD.EVIDENCE_NOTE, PSERS.PLAT.CAD.MEDIA_HOLD, PSERS.PLAT.CAD.TRAINING_MODE, PSERS.PLAT.CAD.RBAC, PSERS.PLAT.CAD.CALLBACK_OT (+13 more)

## 2026-07-18 — L1 publish batch (published)

- Catalog `schema_version`: **1.14**
- Sprint: **P6-042**
- Promoted to `published`: **15** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top_ng911_wave2.json`
- Sample IDs: PSERS.PLAT.NG911.LANGUAGE_INTERP, PSERS.PLAT.NG911.BCF_BORDER, PSERS.PLAT.NG911.I3_LOGGING, PSERS.PLAT.NG911.MISDIAL_FILTER, PSERS.PLAT.NG911.MULTI_LINE, PSERS.PLAT.NG911.LOCATION_DISCREP, PSERS.PLAT.NG911.SILENT_CALL_PROTO, PSERS.PLAT.NG911.RTT_TRANSFER (+7 more)

## 2026-07-18 — Phase 6 Lite freeze (CAD + NG911 deepen)

- Appended **12** CAD + **10** NG911 drafts (`expand_cad_l1.py` / `expand_ng911_l1.py`)
- **CAD:** **56** caps, **56** published; **NG911:** **35** caps, **35** published
- Total published **181**; schema **1.14**; stubs **13** (floor ≥10)
- cad_demo / ng911_demo / psap_loop all **1.0**; LMR mid-doc **0.702**; sensors still pass
- L3: +36 CommandCentral CAD/NG911 maps (**209** mappings)
- Slices **040–042** Done; **MCX** still deferred
- Details: [docs/sprint-p6-041-done.md](sprint-p6-041-done.md)
- **Stop here** — next expansion requires amending `SPEC.md`

## 2026-07-19 — L1 publish batch (published)

- Catalog `schema_version`: **1.16**
- Sprint: **P7-052**
- Promoted to `published`: **14** capabilities
- Stub refusals: **0**
- Tool: `ontology/publish_l1.py`
- Priority source: `ontology/top_incident_wave1.json`
- Sample IDs: PSERS.APP.FIELD.MDT, PSERS.APP.FIELD.INCIDENT_CAPTURE, PSERS.APP.FIELD.FIELD_FORMS, PSERS.APP.FIELD.OFFLINE_SYNC, PSERS.APP.FIELD.EVIDENCE_CAPTURE, PSERS.APP.FIELD.CAD_STATUS_PUSH, PSERS.APP.FIELD.BWC_UPLOAD_TRIGGER, PSERS.PLAT.RMS.INCIDENT_REPORT (+6 more)

## 2026-07-19 — Phase 7 Lite freeze (Incident management process)

- Promoted MDT / RMS incident report / EOC sit-awareness; appended **14** FIELD/RMS/EOC drafts (`expand_incident_l1.py`)
- **FIELD:** **11** caps, **8** published; **RMS:** **5** / **5**; **EOC:** **2** / **2**
- Total published **195**; schema **1.16**; stubs **10** (floor ≥10)
- incident_mgmt **0.929**; prior suites still pass; C2/C4I = L2 crosswalk only
- L3: +14 CommandCentral field/RMS/EOC maps (**223** mappings)
- Slices **050–052** Done; military peer L1 / **MCX** still deferred
- Details: [docs/sprint-p7-051-done.md](sprint-p7-051-done.md), [docs/c2-c4i-crosswalk.md](c2-c4i-crosswalk.md)
- **Stop here** — next expansion requires amending `SPEC.md`

## 2026-07-19 — Slice 060 stakeholder visualization

- Added [docs/ontology-stakeholder-guide.md](ontology-stakeholder-guide.md): business swimlane, L2→L1→L3 bridge, stack/status legend, 10-min demo script
- Analyst UI: Ontology explainer section; `GET /api/ontology/summary`; incident-mgmt demo load
- Spec [specs/060-stakeholder-viz.md](../specs/060-stakeholder-viz.md) Done
- No L1 regenerate; no graph DB; C2/C4I remains crosswalk-only

