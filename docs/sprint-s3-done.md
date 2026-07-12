# Sprint 3 completion — MSI L3 + Match API

**Date:** 2026-07-12  
**Mode:** Cost-optimized Auto (deterministic matcher; no LLM)

## Done

- [x] MSI product catalog (`ontology/l3_msi_products.json`) — **20** products
- [x] L1↔MSI mappings (`ontology/l3_product_capabilities.json`) — **123** mappings across **116** capabilities
- [x] Matcher library `ingest/matcher.py` (seeds + L2 overlap + name match → MSI coverage)
- [x] CLI `ingest/match_rfp.py`
- [x] FastAPI `app/match_api.py` (`/health`, `/match/text`, `/match/pdf`)
- [x] Validators `ontology/validate_l3.py`
- [x] Demo artifacts under `ontology/samples/`

## Counts

| Artifact | Count |
|----------|-------|
| MSI products | 20 |
| Product↔capability mappings | 123 |
| Capabilities with MSI map | 116 |

## How to run

```bash
# Validate L3
py -3.12 ontology/validate_l3.py

# CLI match (PDF)
py -3.12 ingest/match_rfp.py data/rfp/erie-trunked-radio-system-2026-018.pdf --max-pages 20

# CLI match (clean text fixture)
py -3.12 ingest/match_rfp.py ontology/samples/demo_requirements.txt

# API
py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
```

## Notes

- Early PDF pages (TOC) inflate unmapped rate; use `--max-pages` starting mid-doc or the demo text fixture for demos.
- Mappings are `draft` family-level claims from public MSI portfolio knowledge — refine with datasheet citations in a later pass.
