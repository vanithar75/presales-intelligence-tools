# Sprint 4 completion — Analyst UI + demo

**Date:** 2026-07-12  
**Mode:** Cost-optimized Auto

## Done

- [x] Analyst UI at `/` (upload PDF, paste text, demo fixture)
- [x] Match results table (requirement → L1 → confidence)
- [x] MSI coverage panel for matched capabilities
- [x] Synonym feedback form → `ontology/l2_feedback.jsonl`
- [x] FastAPI serves UI + `/api/*` endpoints
- [x] Demo fixture path via **Load demo fixture**

## Run

```bash
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/

### Demo script (5 minutes)

1. Open UI — confirm health shows `API ok · S4`
2. Click **Paste text** → **Load demo fixture** → **Run match**
3. Expect high map rate; inspect MSI coverage cards
4. Click **Feedback** on a row → **Save accept**
5. Optional: Upload an allowlisted RFP PDF with max pages 15–25 (skip TOC-heavy start if needed)

## Definition of Done (MVP)

| Criterion | Status |
|-----------|--------|
| Solid L1 (~180–200) published as draft | Done (192 + 32 stubs) |
| L2 from 3 RFPs | Done (492 + holdout) |
| MSI L3 mappings | Done (20 products / 123 maps) |
| End-to-end upload → match → MSI view | **Done in UI** |
| Synonym correction loop | **Done (feedback JSONL)** |
| SME publish lock on L1/L2 | Pending human |

## Post-MVP backlog

- Deeper CAD / NG911 / Sensors / MCX ontology
- Multi-vendor competitive matrix
- Stronger MSI datasheet citations
- Persist feedback into main L2 catalog with review queue UI
- Auth / multi-user
