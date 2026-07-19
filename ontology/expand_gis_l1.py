"""Promote GIS + cross-cut stubs and append thin GIS drafts (Phase 9)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.PLAT.GIS.COMMON_MAP", "GIS.COMMON_MAP"),
    ("PSERS.XCUT.SEC.ENTERPRISE_IAM", "SEC.ENTERPRISE_IAM"),
    ("PSERS.XCUT.LOC.INDOOR_LOCATION", "LOC.INDOOR_LOCATION"),
]

NEW_GIS = [
    (
        "PSERS.PLAT.GIS.LAYER_MGR",
        "GIS.LAYER_MGR",
        "GIS layer management",
        "Manage and toggle operational GIS layers for dispatch and EOC maps.",
        ["locate", "coordinate"],
        "GIS",
        "PLAT",
        "GIS",
    ),
    (
        "PSERS.PLAT.GIS.GEOCODE",
        "GIS.GEOCODE",
        "Geocode / reverse geocode",
        "Geocode addresses and reverse-geocode coordinates for incident location.",
        ["locate", "call_take"],
        "GIS",
        "PLAT",
        "GIS",
    ),
    (
        "PSERS.PLAT.GIS.ROUTING",
        "GIS.ROUTING",
        "Response routing / ETA",
        "Compute response routes and ETA using GIS network data.",
        ["locate", "dispatch"],
        "GIS",
        "PLAT",
        "GIS",
    ),
    (
        "PSERS.APP.ALERT.WEA_TOUCH",
        "ALERT.WEA_TOUCH",
        "WEA / wireless emergency alert touch",
        "Touchpoint to originate or relay Wireless Emergency Alerts (WEA).",
        ["inform"],
        "ALERT",
        "APP",
        "ALERT",
    ),
]


def bump(ver: str) -> str:
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
        if not row:
            print(f"missing {cid}", file=sys.stderr)
            return 1
        if row["status"] == "stub":
            row["status"] = "draft"
            promoted += 1
        if not row.get("alias"):
            row["alias"] = alias
            alias_set += 1
    existing = set(by_id)
    new_rows = []
    for cid, alias, name, defn, missions, vertical, stack, domain in NEW_GIS:
        if cid in existing:
            continue
        new_rows.append(
            {
                "id": cid,
                "alias": alias,
                "name": name,
                "definition": defn,
                "stack_class": stack,
                "domain": domain,
                "mission_tags": missions,
                "status": "draft",
                "vertical": vertical,
                "p25_ref": None,
            }
        )
    print(json.dumps({"promoted": promoted, "aliases": alias_set, "added": len(new_rows)}))
    if args.dry_run or (not new_rows and not promoted and not alias_set):
        return 0
    caps.extend(new_rows)
    ver = bump(str(doc.get("schema_version", "1.0")))
    stubs = sum(1 for c in caps if c["status"] == "stub")
    published = sum(1 for c in caps if c["status"] == "published")
    draft = sum(1 for c in caps if c["status"] == "draft")
    deprecated = sum(1 for c in caps if c["status"] == "deprecated")
    out = {
        **{k: doc.get(k) for k in ("root", "published_at", "last_publish_tool", "last_priority_file", "generated_by")},
        "schema_version": ver,
        "sprint": "P9-080",
        "last_expand_tool": "ontology/expand_gis_l1.py",
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
    print(f"Wrote schema={ver} stubs={stubs} total={len(caps)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
