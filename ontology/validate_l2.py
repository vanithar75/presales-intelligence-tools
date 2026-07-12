"""Validate L2 synonym catalog against L1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "ontology" / "l1_capabilities.json"
L2 = ROOT / "ontology" / "l2_synonyms.json"
HOLD = ROOT / "ontology" / "l2_synonyms_holdout.json"


def main() -> int:
    l1_ids = {c["id"] for c in json.loads(L1.read_text(encoding="utf-8"))["capabilities"]}
    doc = json.loads(L2.read_text(encoding="utf-8"))
    hold = json.loads(HOLD.read_text(encoding="utf-8"))
    rows = doc["synonyms"]
    errors: list[str] = []

    for r in rows:
        if r["capability_id"] not in l1_ids:
            errors.append(f"unknown capability {r['capability_id']}")
        if not r.get("phrase") or not r.get("source_doc_id"):
            errors.append("missing phrase/source")

    n = len(rows)
    caps = len({r["capability_id"] for r in rows})
    print(f"synonyms={n} holdout={len(hold['synonyms'])} caps_covered={caps}")
    print(f"counts_field={doc.get('counts')}")

    if n < 400:
        errors.append(f"expected >=400 synonyms, got {n}")
    if n > 5000:
        errors.append(f"unexpectedly large set {n}")
    if caps < 40:
        errors.append(f"expected >=40 capabilities covered, got {caps}")

    if errors:
        print("FAIL")
        for e in errors[:15]:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
