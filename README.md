# Presales Intelligence Platform (PSERS / LMR)

Cost-effective MVP: map RFP language → stable capabilities → Motorola Solutions (MSI) product coverage.

## Ontology model

- **Root:** `PSERS` — Public Safety Emergency Response System (of Systems)
- **L1:** Canonical capabilities (solid LMR + stubs for CAD/NG911/Sensors/MCX)
- **L2:** Synonyms from 3 allowlisted LMR RFPs (Sprint 2)
- **L3:** MSI product mappings (Sprint 3)

See [docs/psers-root.md](docs/psers-root.md) and [docs/decision-log.md](docs/decision-log.md).

## Repo layout

```
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
| S1 Solid LMR L1 + stubs | **Done (draft)** — 192 LMR + 32 stubs; SME publish lock pending |
| S2 L2 synonyms (3 RFPs) | Deferred |
| S3 MSI L3 + match API | Deferred |
| S4 UI + demo | Deferred |

See [docs/sprint-s0-s1-done.md](docs/sprint-s0-s1-done.md).

## Quick start (ontology only)

```bash
python ontology/validate_l1.py
python -c "import json; d=json.load(open('ontology/l1_capabilities.json',encoding='utf-8')); print(d['counts'])"
```

## Scope lock (MVP)

- No broad RFP crawl
- L2: ECSO + Erie system + Erie subscriber only
- L3: MSI only
- CAD/Sensors/MCX: stub IDs only until later verticals
