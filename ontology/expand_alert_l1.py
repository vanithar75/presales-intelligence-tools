"""Thin ALERT expand for Phase 8 Lite (slice 073) — promote stubs only + 2 drafts.

Does not regenerate L1. Does not deepen GIS.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.APP.ALERT.MASS_NOTIFY", "ALERT.MASS_NOTIFY"),
    ("PSERS.APP.ALERT.IPAWS", "ALERT.IPAWS"),
]

NEW_ALERT = [
    (
        "PSERS.APP.ALERT.TARGETED_GEO",
        "ALERT.TARGETED_GEO",
        "Geo-targeted public alerts",
        "Originate geo-targeted public warning alerts to selected areas.",
        ["inform", "coordinate"],
    ),
    (
        "PSERS.APP.ALERT.CAP_RELAY",
        "ALERT.CAP_RELAY",
        "CAP alert relay",
        "Relay Common Alerting Protocol (CAP) messages to downstream channels.",
        ["inform"],
    ),
]


def bump_schema_version(ver: str) -> str:
    parts = ver.split(".")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}.{int(parts[1]) + 1}"
    return f"{ver}+1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    doc = json.loads(L1_PATH.read_text(encoding="utf-8"))
    caps = doc["capabilities"]
    by_id = {c["id"]: c for c in caps}
    promoted = alias_set = 0
    for cid, alias in PROMOTE:
        row = by_id.get(cid)
        if row is None:
            print(f"ERROR: missing {cid}", file=sys.stderr)
            return 1
        if row["status"] == "stub":
            row["status"] = "draft"
            promoted += 1
        if not row.get("alias"):
            row["alias"] = alias
            alias_set += 1
    existing = set(by_id)
    new_rows = []
    for cid, alias, name, defn, missions in NEW_ALERT:
        if cid in existing:
            continue
        new_rows.append(
            {
                "id": cid,
                "alias": alias,
                "name": name,
                "definition": defn,
                "stack_class": "APP",
                "domain": "ALERT",
                "mission_tags": missions,
                "status": "draft",
                "vertical": "ALERT",
                "p25_ref": None,
            }
        )
    print(json.dumps({"promoted": promoted, "aliases": alias_set, "added": len(new_rows)}))
    if args.dry_run or (not new_rows and not promoted and not alias_set):
        return 0
    caps.extend(new_rows)
    ver = bump_schema_version(str(doc.get("schema_version", "1.0")))
    stubs = sum(1 for c in caps if c["status"] == "stub")
    published = sum(1 for c in caps if c["status"] == "published")
    draft = sum(1 for c in caps if c["status"] == "draft")
    deprecated = sum(1 for c in caps if c["status"] == "deprecated")
    out = {
        **{k: doc.get(k) for k in ("root", "published_at", "last_publish_tool", "last_priority_file", "generated_by")},
        "schema_version": ver,
        "sprint": "P8-073",
        "last_expand_tool": "ontology/expand_alert_l1.py",
        "expanded_at": date.today().isoformat(),
        "counts": {
            "total": len(caps),
            "draft": draft,
            "published": published,
            "deprecated": deprecated,
            "stubs": stubs,
            "lmr_draft": draft + published + deprecated,
        },
        "capabilities": caps,
    }
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote schema={ver} stubs={stubs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
