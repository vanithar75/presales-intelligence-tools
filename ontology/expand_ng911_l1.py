"""Expand NG911 vertical without regenerating L1.

Promotes existing NG911 stubs → draft with aliases and appends call-handling
capabilities. Does NOT change LMR/CAD published statuses. Does NOT run generate_l1.py.

Usage:
  py -3.12 ontology/expand_ng911_l1.py --dry-run
  py -3.12 ontology/expand_ng911_l1.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.PLAT.NG911.CALL_HANDLING", "NG911.CALL_HANDLING"),
    ("PSERS.PLAT.NG911.EIDO_EXCHANGE", "NG911.EIDO_EXCHANGE"),
    ("PSERS.PLAT.NG911.TEXT_TO_911", "NG911.TEXT_TO_911"),
    ("PSERS.PLAT.NG911.MULTIMEDIA", "NG911.MULTIMEDIA"),
    ("PSERS.PLAT.NG911.ALI_AML", "NG911.ALI_AML"),
]

NEW_NG911: list[tuple[str, str, str, list[str]]] = [
    (
        "SIP_CALL_CONTROL",
        "NG911 SIP call control",
        "Handle emergency SIP sessions (invite, hold, transfer) in an i3 NG911 environment.",
        ["call_take"],
    ),
    (
        "ESRP_ROUTING",
        "Emergency call routing (ESRP)",
        "Route emergency calls via Emergency Services Routing Proxy per policy and location.",
        ["call_take", "locate"],
    ),
    (
        "ECRF_LVF",
        "ECRF / LVF location validation",
        "Query ECRF and validate civic/geodetic location via LVF for routing.",
        ["locate", "call_take"],
    ),
    (
        "POLICY_ROUTING",
        "NG911 policy routing",
        "Apply agency policy rules for call routing, overflow, and special handling.",
        ["call_take", "coordinate"],
    ),
    (
        "CALLBACK",
        "911 callback",
        "Callback abandoned or disconnected emergency callers with retained ANI/location.",
        ["call_take"],
    ),
    (
        "ABANDONED_CALL",
        "Abandoned / silent call handling",
        "Detect and process abandoned, silent, or incomplete 911 calls.",
        ["call_take", "dispatch"],
    ),
    (
        "TTY_RTT",
        "TTY / RTT accessibility",
        "Support TTY and real-time text (RTT) for accessible emergency calling.",
        ["call_take"],
    ),
    (
        "LANGUAGE_INTERP",
        "Language interpretation",
        "Conference language interpretation for non-English emergency callers.",
        ["call_take", "coordinate"],
    ),
    (
        "TRANSFER_CONF",
        "Call transfer / conference",
        "Transfer and conference emergency calls to secondary PSAPs or agencies.",
        ["call_take", "coordinate"],
    ),
    (
        "QUEUE_ACD",
        "911 call queue / ACD",
        "Queue and distribute emergency calls across call-takers (ACD).",
        ["call_take"],
    ),
    (
        "CALL_RECORDING",
        "911 call recording",
        "Record emergency call audio/media with retention and retrieval controls.",
        ["after_action", "call_take"],
    ),
    (
        "WIRELESS_PHASE2",
        "Wireless Phase II location",
        "Acquire wireless Phase II / handset location for mobile 911 callers.",
        ["locate", "call_take"],
    ),
    (
        "ADDITIONAL_DATA",
        "Additional data (ADR)",
        "Receive and display Additional Data Repository / caller additional data.",
        ["call_take", "locate"],
    ),
    (
        "BCF_BORDER",
        "Border control function",
        "Border Control Function for ingress/egress of NG911 SIP traffic.",
        ["call_take"],
    ),
    (
        "I3_LOGGING",
        "i3 event logging",
        "Log NG911 i3 functional-element events for audit and troubleshooting.",
        ["after_action"],
    ),
    (
        "PSAP_FAILOVER",
        "PSAP failover / overflow",
        "Failover and overflow of emergency calls to alternate PSAPs.",
        ["call_take", "coordinate"],
    ),
    (
        "MISDIAL_FILTER",
        "Misdial / non-emergency filter",
        "Filter or redirect obvious misdials and non-emergency contacts where policy allows.",
        ["call_take"],
    ),
    (
        "TELEM_911",
        "Telematics / ACN to 911",
        "Receive automatic crash notification / vehicle telematics into the PSAP.",
        ["call_take", "detect"],
    ),
    (
        "CAD_HANDOFF",
        "NG911–CAD call handoff",
        "Hand off NG911 call/incident data into CAD (deep CAD remains separate vertical).",
        ["call_take", "dispatch"],
    ),
    (
        "MULTI_LINE",
        "Multi-line / multi-agency answer",
        "Support multi-line answering and multi-agency call taking positions.",
        ["call_take", "coordinate"],
    ),
]

# Wave 2 deepen (Phase 6 Lite; append-only; skipped if ID already exists)
NEW_NG911_WAVE2: list[tuple[str, str, str, list[str]]] = [
    (
        "LOCATION_DISCREP",
        "Location discrepancy handling",
        "Detect and resolve discrepancies between reported, ALI/AML, and verified locations.",
        ["locate", "call_take"],
    ),
    (
        "SILENT_CALL_PROTO",
        "Silent-call protocol",
        "Apply silent/open-line call protocols including staged verification steps.",
        ["call_take", "dispatch"],
    ),
    (
        "RTT_TRANSFER",
        "RTT / text transfer",
        "Transfer real-time text (RTT) and text sessions between PSAPs without dropping media.",
        ["call_take", "coordinate"],
    ),
    (
        "MEDIA_RETENTION",
        "Multimedia retention policy",
        "Retain NG911 multimedia (image/video) per agency retention and legal hold policy.",
        ["after_action", "call_take"],
    ),
    (
        "ESRP_CONGESTION",
        "ESRP congestion / alternate route",
        "Handle ESRP congestion with alternate routing and overflow policies.",
        ["call_take", "coordinate"],
    ),
    (
        "LEGACY_SR_BRIDGE",
        "Legacy selective-router bridge",
        "Bridge legacy selective-router / E911 trunks into the NG911 i3 call path.",
        ["call_take"],
    ),
    (
        "ORPHAN_CALL",
        "Orphan / stranded call recovery",
        "Recover orphaned or stranded emergency sessions after network or FE failure.",
        ["call_take", "after_action"],
    ),
    (
        "POISON_TRANSFER",
        "Poison control / specialty transfer",
        "Transfer emergency callers to poison control or other specialty advice lines with location retained.",
        ["call_take", "coordinate"],
    ),
    (
        "BCF_TLS_SRTP",
        "BCF TLS / SRTP media security",
        "Enforce TLS signaling and SRTP media security at the Border Control Function.",
        ["call_take"],
    ),
    (
        "ABANDONED_CB_POLICY",
        "Abandoned-call callback policy",
        "Apply configurable abandoned-call callback policy (attempts, timers, disposition).",
        ["call_take", "dispatch"],
    ),
]

NEW_NG911 = NEW_NG911 + NEW_NG911_WAVE2


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
    ng911 = sum(1 for c in caps if c.get("vertical") == "NG911")
    cad = sum(1 for c in caps if c.get("vertical") == "CAD" or c["id"].startswith("PSERS.PLAT.CAD."))
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
        "cad": cad,
        "ng911": ng911,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand NG911 L1 (append/promote only)")
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

    existing_ids = set(by_id)
    added = 0
    new_rows: list[dict] = []
    for code, name, defn, missions in NEW_NG911:
        cid = f"PSERS.PLAT.NG911.{code}"
        if cid in existing_ids:
            continue
        new_rows.append(
            {
                "id": cid,
                "alias": f"NG911.{code}",
                "name": name,
                "definition": defn,
                "stack_class": "PLAT",
                "domain": "NG911",
                "mission_tags": missions,
                "status": "draft",
                "vertical": "NG911",
                "p25_ref": None,
            }
        )
        added += 1

    summary = {
        "dry_run": args.dry_run,
        "promoted_stub_to_draft": promoted,
        "aliases_set": alias_set,
        "added": added,
        "ng911_after": sum(1 for c in caps if c.get("vertical") == "NG911") + added,
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
        "sprint": "P6-040",
        "published_at": doc.get("published_at"),
        "last_publish_tool": doc.get("last_publish_tool"),
        "last_priority_file": doc.get("last_priority_file"),
        "last_expand_tool": "ontology/expand_ng911_l1.py",
        "expanded_at": date.today().isoformat(),
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {L1_PATH} schema_version={ver} total={counts['total']} "
        f"stubs={counts['stubs']} ng911={counts['ng911']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
