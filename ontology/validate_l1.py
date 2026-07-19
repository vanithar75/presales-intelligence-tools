"""Validate L1 capability catalog invariants."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PATH = Path(__file__).with_name("l1_capabilities.json")
STACKS = {"INFRA", "SENS", "PLAT", "APP", "SVC", "XCUT"}
MISSIONS = {
    "detect",
    "call_take",
    "locate",
    "dispatch",
    "respond",
    "coordinate",
    "inform",
    "after_action",
}


def main() -> int:
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    caps = doc["capabilities"]
    ids = [c["id"] for c in caps]
    errors: list[str] = []

    if len(ids) != len(set(ids)):
        errors.append("duplicate capability ids")

    for c in caps:
        if not c["id"].startswith("PSERS."):
            errors.append(f"bad id prefix: {c['id']}")
        if c["stack_class"] not in STACKS:
            errors.append(f"bad stack: {c['id']}")
        for m in c.get("mission_tags", []):
            if m not in MISSIONS:
                errors.append(f"bad mission {m} on {c['id']}")
        if not c.get("definition"):
            errors.append(f"empty definition: {c['id']}")

    lmr = sum(1 for c in caps if c["status"] != "stub")
    stubs = sum(1 for c in caps if c["status"] == "stub")
    print(f"total={len(caps)} lmr={lmr} stubs={stubs}")
    if lmr < 180:
        errors.append(f"expected >=180 LMR caps, got {lmr}")
    if stubs < 0:
        errors.append(f"expected >=0 stubs, got {stubs}")

    if errors:
        print("FAIL")
        for e in errors[:20]:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
