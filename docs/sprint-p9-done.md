# Phase 9 — High-value bid-desk pack (done)

**Date:** 2026-07-19  
**Goal:** Consume remaining Cursor Pro budget on highest ROI items (target ≤90%).

## Delivered

| Item | Result |
|------|--------|
| Mid-doc lift | **0.702 → 0.752** (install boilerplate filtered; RF/site seeds) |
| L3 gap-fill | +41 then +5 maps → **285** mappings; published caps covered |
| GIS / IAM / indoor / WEA | Published (`top_gis_wave1.json`) |
| MCX remainder | All 17 MCX published |
| Full-stack demo | `fullstack_demo` **0.933** |
| Gap report CLI | `ontology/gap_report.py` |
| UI | Gaps-first filter; MCX/full-stack demo loads; vertical maturity table |

## Catalog

- Schema **1.22**, published **223**, stubs **0**, L3 **285**

## Tools

```bash
py -3.12 ontology/eval_match.py --soft
py -3.12 ontology/gap_report.py ontology/samples/demo_fullstack.txt
py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
```
