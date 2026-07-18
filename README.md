# Presales Intelligence Platform (PSERS / LMR)

Cost-effective MVP: map RFP language → stable capabilities → Motorola Solutions (MSI) product coverage.

**Product spec (authority for next work):** [SPEC.md](SPEC.md) — Phase 6 Lite complete; next expansion needs SPEC amendment  
**Feature slices:** [specs/](specs/)

## Ontology model

- **Root:** `PSERS` — Public Safety Emergency Response System (of Systems)
- **L1:** Canonical capabilities (solid LMR + CAD/NG911 deepen + Sensors lite; MCX stubs)
- **L2:** Synonyms from 3 allowlisted LMR RFPs (Sprint 2)
- **L3:** MSI product mappings (Sprint 3)

See [docs/psers-root.md](docs/psers-root.md) and [docs/decision-log.md](docs/decision-log.md).

## Repo layout

```
SPEC.md            # Product spec (Phase 4 Lite authority)
specs/             # Feature slices for Cursor SDD
ontology/          # L1 JSON + facets
sql/               # Postgres DDL
data/rfp/          # Allowlisted RFP PDFs only
docs/              # Architecture & decisions
ingest/            # PDF → shall extract (Sprint 2+)
app/               # Match UI (Sprint 3–4)
```

## Sprint status

| Sprint | Status |
|--------|--------|
| S0 Scaffold + PSERS root | **Done** |
| S1 Solid LMR L1 + stubs | **Done** — 192 LMR + 32 stubs; top-50 published (P2-001) |
| S2 L2 synonyms (3 RFPs) | **Done** — 492 synonyms + 42 holdout; see [docs/sprint-s2-done.md](docs/sprint-s2-done.md) |
| S3 MSI L3 + match API | **Done** — 20 MSI products, 123 maps, CLI/API matcher; see [docs/sprint-s3-done.md](docs/sprint-s3-done.md) |
| S4 UI + demo | **Done** — analyst UI at `/`; see [docs/sprint-s4-done.md](docs/sprint-s4-done.md) |
| **Phase 2 (SDD)** | **Done** — slices 001–004 complete; see [SPEC.md](SPEC.md) |
| **Phase 3 Lite** | **Done** — LMR deepen slices 010–013; see [SPEC.md](SPEC.md) |
| **Phase 4 Lite** | **Done** — CAD foundation slices 020–023; see [SPEC.md](SPEC.md) |
| **Phase 5 Lite** | **Done** — Sensors foundation slices 030–032; see [SPEC.md](SPEC.md) |
| **Phase 6 Lite** | **Done** — CAD + NG911 deepen slices 040–042; see [SPEC.md](SPEC.md) |

See [docs/sprint-s0-s1-done.md](docs/sprint-s0-s1-done.md).

## Quick start (ontology only)

```bash
py -3.12 ontology/validate_l1.py
py -3.12 ontology/validate_l2.py
py -3.12 ontology/validate_l3.py
py -3.12 ingest/match_rfp.py ontology/samples/demo_requirements.txt
py -3.12 ontology/eval_match.py
py -3.12 ingest/publish_l2_feedback.py --dry-run
```

Match quality: [docs/sprint-p2-002-done.md](docs/sprint-p2-002-done.md).  
Phase 3 match lift: [docs/sprint-p3-011-done.md](docs/sprint-p3-011-done.md).  
Phase 4 CAD match: [docs/sprint-p4-021-done.md](docs/sprint-p4-021-done.md).  
CAD enrichment: [docs/sprint-p4-cad-enrich.md](docs/sprint-p4-cad-enrich.md).  
NG911 call handling: [docs/sprint-p4-ng911.md](docs/sprint-p4-ng911.md).  
Sensors Phase 5: [docs/sprint-p5-031-done.md](docs/sprint-p5-031-done.md).  
Phase 6 CAD+NG911: [docs/sprint-p6-041-done.md](docs/sprint-p6-041-done.md).  
Feedback loop: [docs/sprint-p2-003-done.md](docs/sprint-p2-003-done.md).  
Optional Postgres: [docs/postgres.md](docs/postgres.md).

## Run analyst UI (Sprint 4)

```bash
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/

## Scope lock (MVP)

- No broad RFP crawl
- L2: ECSO + Erie system + Erie subscriber only
- L3: MSI only
- CAD: Phase 4 Lite; NG911: call-handling; Sensors: Phase 5 Lite; MCX stub until later
