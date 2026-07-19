# AGENTS.md

## Cursor Cloud specific instructions

Python-only project (Python 3.12). A virtualenv is created at `.venv` by the update
script; activate/use it via `.venv/bin/python`. There is no JS/Node app.

### What this is
Presales Intelligence Platform (PSERS/LMR): maps RFP requirement language → canonical
capabilities (L1) → Motorola (MSI) product coverage (L3). A single FastAPI service
(`app/match_api.py`) serves both the JSON API and the analyst UI at `/`.

### Run the dev server
`.venv/bin/python -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000 --reload`
then open http://127.0.0.1:8000/ . Health check: `GET /health`.

### Lint / tests
There is no pytest suite. The de facto checks are the ontology validators and the
match-quality eval:
- `.venv/bin/python ontology/validate_l1.py` (also `validate_l2.py`, `validate_l3.py`)
- `.venv/bin/python ontology/eval_match.py` (exits non-zero if a hard suite fails;
  `--soft` always exits 0)

### Non-obvious: RFP PDFs are not committed
`data/rfp/*.pdf` are git-ignored (allowlisted corpus only). Without them the
`mid_doc` suite of `eval_match.py` FAILs with "RFP PDF missing" and `overall_pass`
is `False` — every text-fixture suite still passes. To get a full pass, download the
3 allowlisted PDFs first (requires network): `.venv/bin/python ingest/download_rfps.py`.
This download is intentionally NOT in the startup update script (keeps startup fast
and offline-safe); run it manually when you need PDF-based eval/matching.

### Postgres is optional
Everything runs off JSON files under `ontology/`. Postgres (`ingest/load_postgres.py`,
`sql/schema.sql`) is optional — see `docs/postgres.md`. Not needed to run/test the app.
