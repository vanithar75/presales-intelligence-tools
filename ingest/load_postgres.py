"""Load L1/L2/L3 JSON ontology into Postgres (Phase-2 / specs/004).

Runtime matcher/API continue to use JSON files. This CLI is optional persistence.

Env:
  DATABASE_URL=postgresql://USER:PASS@HOST:PORT/DB

Usage:
  py -3.12 ingest/load_postgres.py --apply-schema
  py -3.12 ingest/load_postgres.py
  py -3.12 ingest/load_postgres.py --database-url postgresql://...

Never prints the full connection URL (password redacted).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
L1_PATH = ROOT / "ontology" / "l1_capabilities.json"
L2_PATH = ROOT / "ontology" / "l2_synonyms.json"
L3P_PATH = ROOT / "ontology" / "l3_msi_products.json"
L3M_PATH = ROOT / "ontology" / "l3_product_capabilities.json"

# Allowlisted RFP metadata (matches data/rfp/README.md)
DOC_META = [
    {
        "id": "ecso-jackson-2019",
        "title": "ECSO Jackson County P25 Functional Specification",
        "source_url": "https://ecso911.com/wp-content/uploads/2019/11/ECSO-P25-Ph2-Functional-Specification-FINAL-20191118.pdf",
        "doc_type": "rfp",
        "notes": "MVP L2 allowlist",
    },
    {
        "id": "erie-trunked-2026",
        "title": "Erie County Trunked Radio System RFP 2026-018",
        "source_url": "https://www3.erie.gov/purchasing/sites/www3.erie.gov.purchasing/files/2026-02/erie-county-trunked-radio-system-rfp-2026-018vf.pdf",
        "doc_type": "rfp",
        "notes": "MVP L2 allowlist",
    },
    {
        "id": "erie-subscriber-2026",
        "title": "Erie County Radio Subscriber RFP 2026-019",
        "source_url": "https://www3.erie.gov/purchasing/sites/www3.erie.gov.purchasing/files/2026-02/erie-county-radio-subscriber-rfp-2026-019vf.pdf",
        "doc_type": "rfp",
        "notes": "MVP L2 allowlist",
    },
    {
        "id": "analyst_ui",
        "title": "Analyst UI feedback",
        "source_url": None,
        "doc_type": "other",
        "notes": "Phrases accepted via synonym feedback publish",
    },
]


def redact_url(url: str) -> str:
    """Hide password in postgresql://user:pass@host/db for logs."""
    return re.sub(r"(://[^:/@]+:)([^@/]+)(@)", r"\1***\3", url)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def connect(database_url: str):
    try:
        import psycopg
    except ImportError as e:
        print(
            "Missing dependency: install with `py -3.12 -m pip install 'psycopg[binary]'`",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
    return psycopg.connect(database_url)


def apply_schema(conn) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def upsert_vendor(cur, vendor_id: str, name: str) -> None:
    cur.execute(
        """
        INSERT INTO vendor (id, name) VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
        """,
        (vendor_id, name),
    )


def upsert_documents(cur) -> int:
    n = 0
    for d in DOC_META:
        cur.execute(
            """
            INSERT INTO document (id, title, source_url, doc_type, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
              title = EXCLUDED.title,
              source_url = EXCLUDED.source_url,
              doc_type = EXCLUDED.doc_type,
              notes = EXCLUDED.notes
            """,
            (d["id"], d["title"], d["source_url"], d["doc_type"], d["notes"]),
        )
        n += 1
    return n


def upsert_capabilities(cur, caps: list[dict]) -> int:
    for c in caps:
        cur.execute(
            """
            INSERT INTO capability (
              id, alias, name, definition, stack_class, domain,
              mission_tags, status, p25_ref, vertical, updated_at
            ) VALUES (
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
            )
            ON CONFLICT (id) DO UPDATE SET
              alias = EXCLUDED.alias,
              name = EXCLUDED.name,
              definition = EXCLUDED.definition,
              stack_class = EXCLUDED.stack_class,
              domain = EXCLUDED.domain,
              mission_tags = EXCLUDED.mission_tags,
              status = EXCLUDED.status,
              p25_ref = EXCLUDED.p25_ref,
              vertical = EXCLUDED.vertical,
              updated_at = now()
            """,
            (
                c["id"],
                c.get("alias"),
                c["name"],
                c["definition"],
                c["stack_class"],
                c["domain"],
                c.get("mission_tags") or [],
                c.get("status") or "draft",
                c.get("p25_ref"),
                c.get("vertical") or "LMR",
            ),
        )
    return len(caps)


def upsert_synonyms(cur, synonyms: list[dict]) -> int:
    n = 0
    for s in synonyms:
        page = s.get("page")
        page_ref = None if page is None else str(page)
        src = s.get("source_doc_id")
        cur.execute(
            """
            INSERT INTO synonym (phrase, capability_id, confidence, source_doc_id, page_ref)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (capability_id, phrase) DO UPDATE SET
              confidence = EXCLUDED.confidence,
              source_doc_id = EXCLUDED.source_doc_id,
              page_ref = EXCLUDED.page_ref
            """,
            (
                s["phrase"],
                s["capability_id"],
                float(s.get("confidence") or 1.0),
                src,
                page_ref,
            ),
        )
        n += 1
    return n


def upsert_products(cur, products: list[dict], vendor_id: str) -> int:
    for p in products:
        cur.execute(
            """
            INSERT INTO product (id, vendor_id, family, sku_or_name, form_factor, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
              vendor_id = EXCLUDED.vendor_id,
              family = EXCLUDED.family,
              sku_or_name = EXCLUDED.sku_or_name,
              form_factor = EXCLUDED.form_factor,
              notes = EXCLUDED.notes
            """,
            (
                p["id"],
                p.get("vendor_id") or vendor_id,
                p["family"],
                p["sku_or_name"],
                p.get("form_factor"),
                p.get("notes") or "",
            ),
        )
    return len(products)


def upsert_mappings(cur, mappings: list[dict]) -> int:
    for m in mappings:
        cur.execute(
            """
            INSERT INTO product_capability (
              product_id, capability_id, support_level, notes, source_url
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id, capability_id) DO UPDATE SET
              support_level = EXCLUDED.support_level,
              notes = EXCLUDED.notes,
              source_url = EXCLUDED.source_url
            """,
            (
                m["product_id"],
                m["capability_id"],
                m.get("support_level") or "unknown",
                m.get("notes") or "",
                m.get("source_url"),
            ),
        )
    return len(mappings)


def count_rows(cur) -> dict[str, int]:
    out = {}
    for table in (
        "vendor",
        "document",
        "capability",
        "synonym",
        "product",
        "product_capability",
    ):
        cur.execute(f"SELECT count(*) FROM {table}")
        out[table] = int(cur.fetchone()[0])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Import PSERS ontology JSON → Postgres")
    ap.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", ""),
        help="Postgres URL (default: DATABASE_URL env). Password never logged.",
    )
    ap.add_argument(
        "--apply-schema",
        action="store_true",
        help=f"Apply {SCHEMA_PATH.relative_to(ROOT)} before import",
    )
    ap.add_argument(
        "--schema-only",
        action="store_true",
        help="Only apply schema; do not import JSON",
    )
    args = ap.parse_args()

    url = (args.database_url or "").strip()
    if not url:
        print(
            "DATABASE_URL not set. Example:\n"
            "  set DATABASE_URL=postgresql://postgres:***@127.0.0.1:5432/psers\n"
            "  py -3.12 ingest/load_postgres.py --apply-schema\n"
            "See docs/postgres.md",
            file=sys.stderr,
        )
        return 2

    print(f"Connecting to {redact_url(url)}", file=sys.stderr)
    conn = connect(url)
    try:
        if args.apply_schema or args.schema_only:
            apply_schema(conn)
            print(f"Applied schema {SCHEMA_PATH.name}", file=sys.stderr)
            if args.schema_only:
                return 0

        l1 = load_json(L1_PATH)
        l2 = load_json(L2_PATH)
        l3p = load_json(L3P_PATH)
        l3m = load_json(L3M_PATH)
        vendor_id = l3p.get("vendor_id") or "MSI"
        vendor_name = l3p.get("vendor_name") or "Motorola Solutions"

        with conn.cursor() as cur:
            upsert_vendor(cur, vendor_id, vendor_name)
            n_docs = upsert_documents(cur)
            n_caps = upsert_capabilities(cur, l1["capabilities"])
            n_syn = upsert_synonyms(cur, l2["synonyms"])
            n_prod = upsert_products(cur, l3p["products"], vendor_id)
            n_map = upsert_mappings(cur, l3m["mappings"])
            counts = count_rows(cur)
        conn.commit()

        summary = {
            "imported": {
                "documents": n_docs,
                "capabilities": n_caps,
                "synonyms": n_syn,
                "products": n_prod,
                "mappings": n_map,
            },
            "table_counts": counts,
        }
        print(json.dumps(summary, indent=2))

        # Soft acceptance checks (warn, don't fail hard on small drift)
        ok = (
            counts["capability"] >= 200
            and counts["product"] >= 20
            and counts["product_capability"] >= 100
            and counts["synonym"] >= 400
        )
        if not ok:
            print("WARNING: table counts below expected floors", file=sys.stderr)
            return 1
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
