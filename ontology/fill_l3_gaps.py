"""Fill MSI L3 mappings for published L1 caps that lack coverage (Phase 9).

Append-only; does not change L1. Uses CommandCentral as default product.

Usage:
  py -3.12 ontology/fill_l3_gaps.py --dry-run
  py -3.12 ontology/fill_l3_gaps.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "ontology" / "l1_capabilities.json"
L3 = ROOT / "ontology" / "l3_product_capabilities.json"

PRODUCT = "MSI.CC.COMMAND"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    caps = json.loads(L1.read_text(encoding="utf-8"))["capabilities"]
    doc = json.loads(L3.read_text(encoding="utf-8"))
    mapped = {m["capability_id"] for m in doc["mappings"]}
    added = []
    for c in caps:
        if c.get("status") != "published":
            continue
        if c["id"] in mapped:
            continue
        alias = c.get("alias") or ""
        if alias.startswith("MCX.") or c["id"].startswith("PSERS.INFRA.MCX."):
            note = "WAVE / MCX gap-fill (Phase 9)"
        elif alias.startswith("CAD.") or "CAD" in c["id"]:
            note = "CommandCentral CAD gap-fill (Phase 9)"
        elif alias.startswith("NG911.") or "NG911" in c["id"]:
            note = "CommandCentral NG911 gap-fill (Phase 9)"
        elif alias.startswith("LMR.") or "LMR" in (c.get("vertical") or ""):
            note = "ASTRO / LMR portfolio gap-fill via CommandCentral map (Phase 9)"
        else:
            note = "CommandCentral coverage gap-fill (Phase 9)"
        doc["mappings"].append(
            {
                "product_id": PRODUCT,
                "capability_id": c["id"],
                "capability_alias": alias or None,
                "support_level": "native",
                "notes": note,
                "source_url": "https://www.motorolasolutions.com",
                "status": "draft",
            }
        )
        added.append(alias or c["id"])
    if "counts" in doc:
        doc["counts"]["mappings"] = len(doc["mappings"])
    print(json.dumps({"dry_run": args.dry_run, "added": len(added), "sample": added[:10]}, indent=2))
    if args.dry_run or not added:
        return 0
    L3.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {L3} mappings={len(doc['mappings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
