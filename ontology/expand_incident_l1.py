"""Expand incident-management process L1 without regenerating (Phase 7 Lite / specs/050).

Promotes FIELD/RMS/EOC stubs → draft with aliases and appends field-app,
RMS, and thin EOC capabilities for the respond → after_action path.

Does NOT change LMR/CAD/NG911/Sensors published statuses.
Does NOT run generate_l1.py. Does NOT deepen MCX or re-expand Sensors catalog.

Usage:
  py -3.12 ontology/expand_incident_l1.py --dry-run
  py -3.12 ontology/expand_incident_l1.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.APP.FIELD.MDT", "FIELD.MDT"),
    ("PSERS.PLAT.RMS.INCIDENT_REPORT", "RMS.INCIDENT_REPORT"),
    ("PSERS.APP.EOC.SIT_AWARENESS", "EOC.SIT_AWARENESS"),
]

# (full_id_suffix_path, alias, name, definition, stack, domain, vertical, missions)
# For NEW rows under APP.FIELD / PLAT.RMS / APP.EOC
NEW_FIELD: list[tuple[str, str, str, list[str]]] = [
    (
        "INCIDENT_CAPTURE",
        "Mobile incident capture",
        "Capture and update incident details from a field mobile application.",
        ["respond", "after_action"],
    ),
    (
        "FIELD_FORMS",
        "Field narrative / forms",
        "Complete structured field narratives and electronic forms linked to incidents.",
        ["respond", "after_action"],
    ),
    (
        "OFFLINE_SYNC",
        "Field offline sync",
        "Operate field apps offline and synchronize when connectivity returns.",
        ["respond"],
    ),
    (
        "EVIDENCE_CAPTURE",
        "Field digital evidence capture",
        "Capture photos, video, and files from the field device into the evidence workflow.",
        ["respond", "after_action"],
    ),
    (
        "PERSON_VEHICLE_ID",
        "Field person / vehicle identification",
        "Query and attach person/vehicle identification results from the field app.",
        ["respond", "locate"],
    ),
    (
        "ECITATION",
        "eCitation / electronic citation",
        "Issue electronic citations from the field and link them to the incident/case.",
        ["respond", "after_action"],
    ),
    (
        "SUPERVISOR_APPROVE",
        "Field supervisor approval",
        "Allow field supervisors to review and approve reports or evidence packages.",
        ["respond", "after_action"],
    ),
    (
        "CAD_STATUS_PUSH",
        "Field–CAD status push",
        "Push unit and incident status updates from the field app into CAD.",
        ["respond", "dispatch"],
    ),
    (
        "BWC_UPLOAD_TRIGGER",
        "Field–BWC upload trigger",
        "Trigger or confirm body-worn camera media upload from the field workflow.",
        ["respond", "after_action"],
    ),
]

NEW_RMS: list[tuple[str, str, str, list[str]]] = [
    (
        "CASE_PACKAGE",
        "RMS case / incident packaging",
        "Package case and incident records for prosecution, records, and sharing.",
        ["after_action"],
    ),
    (
        "EVIDENCE_PROPERTY",
        "Evidence / property room link",
        "Link RMS cases to evidence and property-room custody records.",
        ["after_action"],
    ),
    (
        "SUPPLEMENTAL_REPORT",
        "RMS supplemental reports",
        "Create and manage supplemental / follow-up reports on an incident case.",
        ["after_action"],
    ),
    (
        "LEGAL_HOLD",
        "RMS retention / legal hold",
        "Apply retention schedules and legal holds to RMS records and evidence metadata.",
        ["after_action"],
    ),
]

NEW_EOC: list[tuple[str, str, str, list[str]]] = [
    (
        "COMMON_OP_PICTURE",
        "EOC common operating picture",
        "Present a multi-source common operating picture for EOC / C2 coordination.",
        ["coordinate", "inform"],
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
    field = sum(
        1
        for c in caps
        if c.get("vertical") == "FIELD"
        or c["id"].startswith("PSERS.APP.FIELD.")
        or (c.get("alias") or "").startswith("FIELD.")
        or c.get("alias") == "CAD.MOBILE_CLIENT"
    )
    rms = sum(
        1
        for c in caps
        if c.get("vertical") == "RMS"
        or c["id"].startswith("PSERS.PLAT.RMS.")
        or (c.get("alias") or "").startswith("RMS.")
    )
    eoc = sum(
        1
        for c in caps
        if c.get("vertical") == "EOC"
        or c["id"].startswith("PSERS.APP.EOC.")
        or (c.get("alias") or "").startswith("EOC.")
    )
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
        "field": field,
        "rms": rms,
        "eoc": eoc,
    }


def _append_rows(
    *,
    prefix: str,
    alias_prefix: str,
    stack: str,
    domain: str,
    vertical: str,
    items: list[tuple[str, str, str, list[str]]],
    existing_ids: set[str],
) -> list[dict]:
    rows: list[dict] = []
    for code, name, defn, missions in items:
        cid = f"{prefix}.{code}"
        if cid in existing_ids:
            continue
        rows.append(
            {
                "id": cid,
                "alias": f"{alias_prefix}.{code}",
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
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand incident-mgmt L1 (FIELD/RMS/EOC)")
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
    new_rows: list[dict] = []
    new_rows.extend(
        _append_rows(
            prefix="PSERS.APP.FIELD",
            alias_prefix="FIELD",
            stack="APP",
            domain="FIELD",
            vertical="FIELD",
            items=NEW_FIELD,
            existing_ids=existing_ids,
        )
    )
    new_rows.extend(
        _append_rows(
            prefix="PSERS.PLAT.RMS",
            alias_prefix="RMS",
            stack="PLAT",
            domain="RMS",
            vertical="RMS",
            items=NEW_RMS,
            existing_ids=existing_ids,
        )
    )
    new_rows.extend(
        _append_rows(
            prefix="PSERS.APP.EOC",
            alias_prefix="EOC",
            stack="APP",
            domain="EOC",
            vertical="EOC",
            items=NEW_EOC,
            existing_ids=existing_ids,
        )
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
        "sprint": "P7-050",
        "published_at": doc.get("published_at"),
        "last_publish_tool": doc.get("last_publish_tool"),
        "last_priority_file": doc.get("last_priority_file"),
        "last_expand_tool": "ontology/expand_incident_l1.py",
        "expanded_at": date.today().isoformat(),
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {L1_PATH} schema_version={ver} total={counts['total']} "
        f"stubs={counts['stubs']} field={counts['field']} rms={counts['rms']} "
        f"eoc={counts['eoc']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
