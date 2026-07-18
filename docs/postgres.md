# Postgres persistence (optional)

Phase-2 slice **004** adds an idempotent JSON → Postgres import.  
The match API and matcher **still read JSON files by default** — Postgres is optional.

## Prerequisites

- Postgres 14+ (local install or Docker)
- Python dep: `psycopg[binary]` (in `requirements.txt`)

```bash
py -3.12 -m pip install "psycopg[binary]"
```

## Connection

Set `DATABASE_URL` (never commit credentials):

```bash
# PowerShell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/psers"

# bash
export DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/psers
```

Or pass `--database-url` (still not logged with password visible — CLI redacts it).

## Docker quick start

```bash
docker run -d --name psers-pg `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=psers `
  -e POSTGRES_DB=psers `
  -p 5433:5432 postgres:16

$env:DATABASE_URL = "postgresql://postgres:psers@127.0.0.1:5433/psers"
```

## Import

```bash
# Apply sql/schema.sql then load L1/L2/L3 JSON
py -3.12 ingest/load_postgres.py --apply-schema

# Re-run anytime (upsert / idempotent)
py -3.12 ingest/load_postgres.py
```

Manual schema only:

```bash
psql "$DATABASE_URL" -f sql/schema.sql
# or
py -3.12 ingest/load_postgres.py --apply-schema --schema-only
```

## Expected counts (approx)

| Table | Floor |
|-------|-------|
| capability | ~224 |
| synonym | ≥400 |
| product | 20 |
| product_capability | ≥100 |

## Runtime note

`ingest/matcher.py` `_load_ontology()` continues to load from `ontology/*.json`.  
Bringing the API onto SQL is **out of scope** for 004.
