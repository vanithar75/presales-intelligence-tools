# 004 — Persistence lite

**Status:** Planned  
**SPEC refs:** FR-4, NFR-3  
**Owner:** engineering  

---

## Context

[sql/schema.sql](../sql/schema.sql) defines Postgres tables but runtime still reads JSON. Phase 2 adds an optional, idempotent import path without forcing the API onto the DB.

## Requirements

1. CLI `ingest/load_postgres.py` that:
   - Reads `DATABASE_URL` (or `--database-url`)
   - Applies schema if needed (or documents `psql -f sql/schema.sql` prerequisite)
   - Upserts vendor `MSI`, documents (allowlist metadata), capabilities, synonyms, products, product_capability rows
2. Idempotent: second run does not duplicate primary keys.
3. API continues to load ontology from JSON by default ([ingest/matcher.py](../ingest/matcher.py) `_load_ontology`).
4. README or `docs/postgres.md` documents setup (local Postgres, env var, import command).
5. Never log or commit passwords.

## Out of scope

- Switching matcher/API to SQL-backed reads
- Migrations framework (Alembic, etc.)
- Cloud-hosted DB provisioning

## Acceptance tests

- [ ] With a local Postgres and `DATABASE_URL`, import completes exit 0
- [ ] Row counts roughly match JSON (`capabilities` ≈ 224, products = 20, mappings ≥ 100, synonyms ≥ 400)
- [ ] Second import exits 0 without unique-constraint failures
- [ ] App match still works with JSON when DB is down
- [ ] Docs describe the flow

## Implementation notes (files)

- [sql/schema.sql](../sql/schema.sql) — extend only if import needs columns (prefer fit existing)
- New: `ingest/load_postgres.py`, `docs/postgres.md`
- [requirements.txt](../requirements.txt) — add `psycopg[binary]` or `psycopg2-binary` if used
- [ontology/l1_capabilities.json](../ontology/l1_capabilities.json), L2/L3 JSON inputs

## Status

Planned — not started.
