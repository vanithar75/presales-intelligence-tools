"""Expand CAD vertical without regenerating L1 (Phase 4 Lite / specs/020).

Promotes existing CAD stubs → draft with aliases, promotes MOBILE_CAD,
and appends additional PLAT.CAD draft capabilities.

Does NOT change LMR published/draft statuses. Does NOT run generate_l1.py.

Usage:
  py -3.12 ontology/expand_cad_l1.py --dry-run
  py -3.12 ontology/expand_cad_l1.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

# Existing stubs to promote → draft + alias
PROMOTE = [
    ("PSERS.PLAT.CAD.INCIDENT_CREATE", "CAD.INCIDENT_CREATE"),
    ("PSERS.PLAT.CAD.UNIT_STATUS", "CAD.UNIT_STATUS"),
    ("PSERS.PLAT.CAD.RECOMMENDATION", "CAD.RECOMMENDATION"),
    ("PSERS.PLAT.CAD.CAD_TO_CAD", "CAD.CAD_TO_CAD"),
    ("PSERS.PLAT.CAD.AVL_DISPLAY", "CAD.AVL_DISPLAY"),
    ("PSERS.APP.FIELD.MOBILE_CAD", "CAD.MOBILE_CLIENT"),
]

# New CAD drafts to append (id suffix → name, definition, missions)
NEW_CAD: list[tuple[str, str, str, list[str]]] = [
    (
        "CALL_TYPE",
        "CAD call / incident types",
        "Configure and select call/incident types and natures for dispatch.",
        ["dispatch", "call_take"],
    ),
    (
        "PRIORITY_SOP",
        "CAD priority and SOP",
        "Apply priority levels and standard operating procedures to incidents.",
        ["dispatch"],
    ),
    (
        "PREMISE_HAZARD",
        "Premise / hazard notes",
        "Store and present premise history, hazards, and officer-safety notes.",
        ["dispatch", "respond"],
    ),
    (
        "CALL_STACK",
        "Call stacking / pending queue",
        "Queue, stack, and prioritize pending calls awaiting assignment.",
        ["dispatch", "call_take"],
    ),
    (
        "UNIT_RECOMMEND_GEO",
        "Geo-aware unit recommendation",
        "Recommend closest/appropriate units using location and resource type.",
        ["dispatch", "locate"],
    ),
    (
        "BOLO_MESSAGE",
        "BOLO / broadcast messaging",
        "Create and distribute BOLOs and broadcast messages to units/agencies.",
        ["dispatch", "inform"],
    ),
    (
        "ROSTER_SCHEDULE",
        "Roster and schedule",
        "Maintain unit/person roster, shifts, and on-duty schedule for dispatch.",
        ["dispatch"],
    ),
    (
        "RMS_INTERFACE",
        "CAD–RMS interface",
        "Interface CAD incidents/units with records management (RMS) systems.",
        ["after_action", "dispatch"],
    ),
    (
        "NG911_TOUCH",
        "CAD–NG911 call intake touchpoint",
        "Receive NG911/PSAP call data into CAD (deep NG911 remains stub vertical).",
        ["call_take", "dispatch"],
    ),
    (
        "AUDIT_LOG",
        "CAD audit logging",
        "Audit trail of CAD actions, status changes, and user activity.",
        ["after_action"],
    ),
    (
        "MAP_LAYERS",
        "CAD map layers",
        "Display GIS/map layers (beats, hydrants, cameras) in the CAD map.",
        ["locate", "dispatch"],
    ),
    (
        "TIMED_ALERT",
        "Timed alerts / rip-and-run",
        "Timed reminders, rip-and-run sheets, and escalation alerts for units.",
        ["dispatch", "respond"],
    ),
    (
        "MULTI_AGENCY",
        "Multi-agency incident",
        "Support multi-agency incidents with shared visibility and roles.",
        ["coordinate", "dispatch"],
    ),
    (
        "RESOURCE_TYPE",
        "Resource typing",
        "Type and filter resources (engine, medic, patrol) for recommendation.",
        ["dispatch"],
    ),
    (
        "SHIFT_BRIEF",
        "Shift briefing",
        "Shift briefing / pass-on notes for dispatch and field supervisors.",
        ["dispatch", "inform"],
    ),
    (
        "PERSON_QUERY",
        "Person / vehicle query",
        "Query person/vehicle databases from CAD and attach results to incidents.",
        ["dispatch", "locate"],
    ),
    (
        "STATUS_MONITOR",
        "Unit status monitor wall",
        "Real-time unit status board / monitor for dispatch supervisors.",
        ["dispatch"],
    ),
    (
        "INCIDENT_HISTORY",
        "Incident history search",
        "Search historical incidents by location, type, unit, or timeframe.",
        ["after_action", "dispatch"],
    ),
    (
        "RADIO_INTEGRATION",
        "CAD–radio integration",
        "Integrate CAD with radio/console events (status, emergency, ANI/ALI).",
        ["dispatch", "respond"],
    ),
    (
        "COMMAND_VIEW",
        "Command / supervisory CAD view",
        "Supervisory command view of active incidents and unit workload.",
        ["coordinate", "dispatch"],
    ),
]

# Wave 2 enrichment (append-only; skipped if ID already exists)
NEW_CAD_WAVE2: list[tuple[str, str, str, list[str]]] = [
    (
        "DUPLICATE_CHECK",
        "Duplicate call detection",
        "Detect and link duplicate or related calls/incidents at intake.",
        ["call_take", "dispatch"],
    ),
    (
        "TOW_IMPOUND",
        "Tow / impound tracking",
        "Track tow requests, impound status, and vehicle release from CAD.",
        ["dispatch", "after_action"],
    ),
    (
        "WARRANT_CHECK",
        "Warrant / wants check",
        "Initiate warrant/wants/NCIC-class queries from CAD and attach results.",
        ["dispatch", "locate"],
    ),
    (
        "MUTUAL_AID_REQ",
        "Mutual aid request workflow",
        "Request and track mutual aid resources across agencies from CAD.",
        ["coordinate", "dispatch"],
    ),
    (
        "FIRE_RUN_CARD",
        "Fire run cards / pre-plans",
        "Present fire run cards, pre-plans, and hydrant info to responding units.",
        ["respond", "dispatch"],
    ),
    (
        "EMS_PROTOCOL",
        "EMS protocol / triage support",
        "Support EMS dispatch protocols and triage guidance in CAD.",
        ["dispatch", "respond"],
    ),
    (
        "HOSPITAL_STATUS",
        "Hospital diversion / bed status",
        "Display hospital diversion and bed/capacity status for EMS routing.",
        ["dispatch", "coordinate"],
    ),
    (
        "TRAFFIC_STOP",
        "Traffic stop workflow",
        "Support traffic stop / citation workflows with location and vehicle data.",
        ["respond", "dispatch"],
    ),
    (
        "PURSUIT",
        "Pursuit / chase tracking",
        "Track pursuits with unit roles, route, and supervisory oversight.",
        ["respond", "coordinate"],
    ),
    (
        "EVIDENCE_NOTE",
        "Evidence / property notes",
        "Capture evidence and property notes linked to CAD incidents.",
        ["after_action", "respond"],
    ),
    (
        "MEDIA_HOLD",
        "Media / PIO hold notes",
        "Flag media holds and PIO notes on sensitive incidents.",
        ["inform", "dispatch"],
    ),
    (
        "TRAINING_MODE",
        "CAD training / simulation mode",
        "Training or simulation mode that does not affect live incident data.",
        ["after_action", "dispatch"],
    ),
    (
        "FAILOVER_DR",
        "CAD failover / DR",
        "Failover and disaster-recovery operation for CAD availability.",
        ["dispatch", "after_action"],
    ),
    (
        "RBAC",
        "CAD role-based access",
        "Role-based access control for CAD functions and data visibility.",
        ["after_action"],
    ),
    (
        "CALLBACK_OT",
        "Overtime / callback roster",
        "Manage overtime and callback rosters for staffing from CAD.",
        ["dispatch"],
    ),
    (
        "VEHICLE_ASSIGN",
        "Unit–vehicle assignment",
        "Assign vehicles/apparatus to units and track current assignment.",
        ["dispatch", "respond"],
    ),
    (
        "ALARM_INTERFACE",
        "Alarm monitoring interface",
        "Receive and process alarm-monitoring events into CAD incidents.",
        ["detect", "dispatch"],
    ),
    (
        "UNIT_CHAT",
        "Unit–dispatch messaging",
        "Secure messaging/chat between dispatch and field units in CAD.",
        ["dispatch", "respond"],
    ),
]

# Wave 3 deepen (Phase 6 Lite; append-only; skipped if ID already exists)
NEW_CAD_WAVE3: list[tuple[str, str, str, list[str]]] = [
    (
        "CIT_FLAG",
        "CIT / mental-health flags",
        "Flag incidents and subjects for CIT / mental-health response protocols.",
        ["dispatch", "respond"],
    ),
    (
        "JUVENILE_FLAG",
        "Juvenile subject flags",
        "Flag juvenile subjects and apply age-sensitive handling notes in CAD.",
        ["dispatch", "respond"],
    ),
    (
        "GEO_FENCE_ALERT",
        "Geo-fence / zone alerts",
        "Alert dispatch when units or incidents enter configured geo-fences or zones.",
        ["locate", "dispatch"],
    ),
    (
        "INCIDENT_CLONE",
        "Incident clone / split",
        "Clone or split incidents while preserving linked history and parties.",
        ["dispatch", "call_take"],
    ),
    (
        "SUPERVISOR_OVERRIDE",
        "Supervisor override",
        "Allow authorized supervisors to override priority, assignment, or SOP locks.",
        ["coordinate", "dispatch"],
    ),
    (
        "JAIL_COURT_IFACE",
        "Jail / court interface touch",
        "Interface CAD bookings and court appearance touchpoints with jail/court systems.",
        ["after_action", "dispatch"],
    ),
    (
        "WEATHER_ROAD",
        "Weather / road closure layers",
        "Display weather and road-closure layers affecting response routing.",
        ["locate", "dispatch"],
    ),
    (
        "SKILL_RECOMMEND",
        "Skill-based unit recommendation",
        "Recommend units by certified skills (e.g. CIT, K9, bilingual) in addition to proximity.",
        ["dispatch"],
    ),
    (
        "SCHEDULED_EVENT",
        "Scheduled / planned events",
        "Create and manage scheduled or planned events with pre-assigned resources.",
        ["dispatch", "coordinate"],
    ),
    (
        "QUARANTINE_HOLD",
        "Quarantine / information hold",
        "Place sensitive incidents on quarantine or information-hold with restricted visibility.",
        ["dispatch", "inform"],
    ),
    (
        "SHIFT_HANDOFF",
        "Dispatcher shift handoff",
        "Structured dispatcher shift handoff of active incidents and pending work.",
        ["dispatch", "inform"],
    ),
    (
        "PERSON_ALERT",
        "Person-of-interest alerts",
        "Alert when a person of interest or watchlist hit attaches to an incident or query.",
        ["dispatch", "locate"],
    ),
]

NEW_CAD = NEW_CAD + NEW_CAD_WAVE2 + NEW_CAD_WAVE3


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
    cad = sum(1 for c in caps if c.get("vertical") == "CAD" or c["id"].startswith("PSERS.PLAT.CAD."))
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
        "cad": cad,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand CAD L1 (append/promote only)")
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
        # Keep MOBILE_CAD vertical as FIELD but ensure it's usable as CAD client
        if cid.endswith("MOBILE_CAD"):
            row["alias"] = alias

    existing_ids = set(by_id)
    added = 0
    new_rows: list[dict] = []
    for code, name, defn, missions in NEW_CAD:
        cid = f"PSERS.PLAT.CAD.{code}"
        if cid in existing_ids:
            continue
        new_rows.append(
            {
                "id": cid,
                "alias": f"CAD.{code}",
                "name": name,
                "definition": defn,
                "stack_class": "PLAT",
                "domain": "CAD",
                "mission_tags": missions,
                "status": "draft",
                "vertical": "CAD",
                "p25_ref": None,
            }
        )
        added += 1

    cad_after = (
        sum(
            1
            for c in caps
            if c.get("vertical") == "CAD" or c["id"].startswith("PSERS.PLAT.CAD.")
        )
        + added
    )
    # MOBILE_CAD counts toward CAD foundation but vertical may stay FIELD
    if by_id.get("PSERS.APP.FIELD.MOBILE_CAD"):
        cad_after += 0  # already counted only if vertical CAD; track separately

    summary = {
        "dry_run": args.dry_run,
        "promoted_stub_to_draft": promoted,
        "aliases_set": alias_set,
        "added": added,
        "cad_plat_after": sum(
            1 for c in caps if c["id"].startswith("PSERS.PLAT.CAD.")
        )
        + added,
        "sample_new": [r["id"] for r in new_rows[:5]],
    }
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("Dry-run only; no files written.", file=sys.stderr)
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
        "last_expand_tool": "ontology/expand_cad_l1.py",
        "expanded_at": date.today().isoformat(),
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }
    if added == 0 and promoted == 0 and alias_set == 0:
        print("Nothing to change.", file=sys.stderr)
        return 0
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {L1_PATH} schema_version={ver} total={counts['total']} "
        f"stubs={counts['stubs']} cad={counts['cad']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
