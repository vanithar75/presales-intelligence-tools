"""Expand MCX Lite without regenerating L1 (Phase 8 / specs/070).

Promotes existing MCX stubs (+ LMR–MCX IWF) → draft with aliases and appends
MCPTT/MCVideo/MCData draft capabilities. Does NOT run generate_l1.py.

Usage:
  py -3.12 ontology/expand_mcx_l1.py --dry-run
  py -3.12 ontology/expand_mcx_l1.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.INFRA.MCX.MCPTT", "MCX.MCPTT"),
    ("PSERS.INFRA.MCX.MCVIDEO", "MCX.MCVIDEO"),
    ("PSERS.INFRA.MCX.MCDATA", "MCX.MCDATA"),
    ("PSERS.INFRA.MCX.MCPTT_EMERG", "MCX.MCPTT_EMERG"),
    ("PSERS.XCUT.IOP.LMR_MCX_IWF", "MCX.LMR_IWF"),
]

NEW_MCX: list[tuple[str, str, str, list[str]]] = [
    (
        "AFFILIATION",
        "MCX affiliation / group management",
        "Affiliate users/devices to MCX groups and manage membership.",
        ["coordinate", "respond"],
    ),
    (
        "PRIVATE_CALL",
        "MCPTT private call",
        "Support MCPTT private (one-to-one) calls between authorized users.",
        ["respond"],
    ),
    (
        "FLOOR_CONTROL",
        "MCPTT floor control",
        "Floor control / talker arbitration for MCPTT group calls.",
        ["respond", "coordinate"],
    ),
    (
        "LOCATION",
        "MCX location reporting",
        "Report and display MCX user/device location to authorized consumers.",
        ["locate", "respond"],
    ),
    (
        "SDS",
        "MCData short data / SDS",
        "Send and receive MCData short data service (SDS) messages.",
        ["respond", "inform"],
    ),
    (
        "FILE_DIST",
        "MCData file distribution",
        "Distribute files over MCData to groups or individuals.",
        ["respond", "inform"],
    ),
    (
        "VIDEO_PULL",
        "MCVideo pull / remote view",
        "Pull or remotely view MCVideo streams for authorized supervisors.",
        ["coordinate", "respond"],
    ),
    (
        "PRIORITY",
        "MCX priority / preemption",
        "Apply MCX priority levels and preemption policies for critical traffic.",
        ["respond", "coordinate"],
    ),
    (
        "OFF_NETWORK",
        "MCX off-network / ProSe touch",
        "Support off-network / proximity services touchpoints where specified.",
        ["respond"],
    ),
    (
        "USER_AUTH",
        "MCX user authentication",
        "Authenticate MCX users and bind identities to agency directories.",
        ["respond", "after_action"],
    ),
    (
        "RECORDER",
        "MCX call recording",
        "Record MCPTT/MCVideo sessions with retention controls.",
        ["after_action"],
    ),
    (
        "MULTI_AGENCY",
        "MCX multi-agency talkgroups",
        "Support multi-agency MCX talkgroups and inter-agency affiliation.",
        ["coordinate", "respond"],
    ),
]


def bump_schema_version(ver: str) -> str:
    parts = ver.split(".")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}.{int(parts[1]) + 1}"
    return f"{ver}+1"


def recount(caps: list[dict]) -> dict[str, int]:
    stubs = sum(1 for c in caps if c["status"] == "stub")
    published = sum(1 for c in caps if c["status"] == "published")
    deprecated = sum(1 for c in caps if c["status"] == "deprecated")
    draft = sum(1 for c in caps if c["status"] == "draft")
    mcx = sum(
        1
        for c in caps
        if c.get("vertical") == "MCX"
        or c["id"].startswith("PSERS.INFRA.MCX.")
        or (c.get("alias") or "").startswith("MCX.")
    )
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
        "mcx": mcx,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand MCX L1 (append/promote only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = json.loads(L1_PATH.read_text(encoding="utf-8"))
    caps: list[dict] = doc["capabilities"]
    by_id = {c["id"]: c for c in caps}

    promoted = 0
    alias_set = 0
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
        if cid.endswith("LMR_MCX_IWF"):
            row["vertical"] = "MCX"

    existing_ids = set(by_id)
    new_rows: list[dict] = []
    for code, name, defn, missions in NEW_MCX:
        cid = f"PSERS.INFRA.MCX.{code}"
        if cid in existing_ids:
            continue
        new_rows.append(
            {
                "id": cid,
                "alias": f"MCX.{code}",
                "name": name,
                "definition": defn,
                "stack_class": "INFRA",
                "domain": "MCX",
                "mission_tags": missions,
                "status": "draft",
                "vertical": "MCX",
                "p25_ref": None,
            }
        )
    added = len(new_rows)

    summary = {
        "dry_run": args.dry_run,
        "promoted_stub_to_draft": promoted,
        "aliases_set": alias_set,
        "added": added,
        "sample_new": [r["id"] for r in new_rows[:5]],
    }
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("Dry-run only; no files written.", file=sys.stderr)
        return 0
    if added == 0 and promoted == 0 and alias_set == 0:
        print("Nothing to change.", file=sys.stderr)
        return 0

    caps.extend(new_rows)
    ver = bump_schema_version(str(doc.get("schema_version", "1.0")))
    counts = recount(caps)
    out = {
        "schema_version": ver,
        "root": doc.get("root", "PSERS"),
        "sprint": "P8-070",
        "published_at": doc.get("published_at"),
        "last_publish_tool": doc.get("last_publish_tool"),
        "last_priority_file": doc.get("last_priority_file"),
        "last_expand_tool": "ontology/expand_mcx_l1.py",
        "expanded_at": date.today().isoformat(),
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {L1_PATH} schema_version={ver} total={counts['total']} "
        f"stubs={counts['stubs']} mcx={counts['mcx']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
