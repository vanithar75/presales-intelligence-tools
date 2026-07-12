"""Validate L3 MSI products and mappings."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = json.loads((ROOT / "ontology" / "l1_capabilities.json").read_text(encoding="utf-8"))
PROD = json.loads((ROOT / "ontology" / "l3_msi_products.json").read_text(encoding="utf-8"))
MAP = json.loads((ROOT / "ontology" / "l3_product_capabilities.json").read_text(encoding="utf-8"))

LEVELS = {"native", "option", "partner", "not_applicable", "unknown"}


def main() -> int:
    l1_ids = {c["id"] for c in L1["capabilities"]}
    pids = {p["id"] for p in PROD["products"]}
    errors = []
    for m in MAP["mappings"]:
        if m["capability_id"] not in l1_ids:
            errors.append(f"bad capability {m['capability_id']}")
        if m["product_id"] not in pids:
            errors.append(f"bad product {m['product_id']}")
        if m["support_level"] not in LEVELS:
            errors.append(f"bad level {m['support_level']}")

    n_prod = len(PROD["products"])
    n_map = len(MAP["mappings"])
    n_caps = len({m["capability_id"] for m in MAP["mappings"]})
    print(f"products={n_prod} mappings={n_map} capabilities_mapped={n_caps}")
    if n_prod < 15:
        errors.append("expected >=15 products")
    if n_map < 40:
        errors.append("expected >=40 mappings")
    if n_caps < 40:
        errors.append("expected >=40 capabilities mapped")
    if errors:
        print("FAIL")
        for e in errors[:20]:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
