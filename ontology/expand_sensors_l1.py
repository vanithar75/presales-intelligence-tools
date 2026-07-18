"""Expand Sensors vertical (VIDEO/IOT/UAS) without regenerating L1 (Phase 5 Lite).

Promotes existing sensor stubs → draft with aliases and appends bid-desk sensor caps.
Does NOT change LMR/CAD/NG911 published statuses. Does NOT run generate_l1.py.

Usage:
  py -3.12 ontology/expand_sensors_l1.py --dry-run
  py -3.12 ontology/expand_sensors_l1.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

L1_PATH = Path(__file__).with_name("l1_capabilities.json")

PROMOTE = [
    ("PSERS.SENS.VIDEO.FIXED_CCTV", "VIDEO.FIXED_CCTV"),
    ("PSERS.SENS.VIDEO.LIVE_SHARE", "VIDEO.LIVE_SHARE"),
    ("PSERS.SENS.VIDEO.BODYWORN", "VIDEO.BODYWORN"),
    ("PSERS.SENS.UAS.DISPATCHABLE_AIRCRAFT", "UAS.DISPATCHABLE_AIRCRAFT"),
    ("PSERS.SENS.IOT.GUNSHOT", "IOT.GUNSHOT"),
    ("PSERS.SENS.IOT.ALPR", "IOT.ALPR"),
    ("PSERS.SENS.IOT.ENVIRONMENTAL", "IOT.ENVIRONMENTAL"),
    ("PSERS.PLAT.VMS.VIDEO_MANAGEMENT", "VIDEO.VMS"),
]

# (stack, domain, code, name, definition, missions, vertical, alias)
NEW_SENSORS: list[tuple[str, str, str, str, str, list[str], str, str]] = [
    (
        "SENS",
        "VIDEO",
        "VMS_SEARCH",
        "VMS search / retrieve",
        "Search and retrieve recorded video by time, camera, and incident.",
        ["after_action", "locate"],
        "VIDEO",
        "VIDEO.VMS_SEARCH",
    ),
    (
        "SENS",
        "VIDEO",
        "VMS_RETENTION",
        "Video retention policy",
        "Enforce retention, hold, and purge policies for agency video evidence.",
        ["after_action"],
        "VIDEO",
        "VIDEO.VMS_RETENTION",
    ),
    (
        "SENS",
        "VIDEO",
        "CCTV_PTZ",
        "PTZ camera control",
        "Pan-tilt-zoom control of fixed CCTV cameras from ops workstations.",
        ["detect", "coordinate"],
        "VIDEO",
        "VIDEO.CCTV_PTZ",
    ),
    (
        "SENS",
        "VIDEO",
        "VIDEO_WALL",
        "Video wall / ops display",
        "Display multi-camera layouts on ops/EOC video walls.",
        ["coordinate", "detect"],
        "VIDEO",
        "VIDEO.VIDEO_WALL",
    ),
    (
        "SENS",
        "VIDEO",
        "BODYWORN_EVIDENCE",
        "Body-worn evidence workflow",
        "Upload, classify, and chain-of-custody body-worn camera evidence.",
        ["after_action", "respond"],
        "VIDEO",
        "VIDEO.BODYWORN_EVIDENCE",
    ),
    (
        "SENS",
        "VIDEO",
        "PSAP_LIVESTREAM",
        "Livestream to PSAP / CAD",
        "Stream live video into PSAP/CAD/EOC for situational awareness.",
        ["coordinate", "call_take"],
        "VIDEO",
        "VIDEO.PSAP_LIVESTREAM",
    ),
    (
        "SENS",
        "IOT",
        "ALPR_HOTLIST",
        "ALPR hotlist matching",
        "Match ALPR reads against hotlists and alert ops in near real time.",
        ["detect", "locate"],
        "IOT",
        "IOT.ALPR_HOTLIST",
    ),
    (
        "SENS",
        "IOT",
        "GUNSHOT_CAD",
        "Gunshot → CAD incident",
        "Create or enrich CAD incidents from gunshot detection alerts.",
        ["detect", "dispatch"],
        "IOT",
        "IOT.GUNSHOT_CAD",
    ),
    (
        "SENS",
        "IOT",
        "SENSOR_ALERT_ROUTE",
        "Sensor alert routing",
        "Route IoT/sensor alerts to the correct PSAP/ops queue by policy.",
        ["detect", "dispatch"],
        "IOT",
        "IOT.SENSOR_ALERT_ROUTE",
    ),
    (
        "SENS",
        "IOT",
        "TRAFFIC_SENSOR",
        "Traffic / roadway sensors",
        "Ingest traffic and roadway sensors for incident awareness.",
        ["detect", "locate"],
        "IOT",
        "IOT.TRAFFIC_SENSOR",
    ),
    (
        "SENS",
        "UAS",
        "DRONE_DOWNLINK",
        "UAS video downlink",
        "Receive and display drone video downlink in ops/CAD workflows.",
        ["detect", "coordinate"],
        "UAS",
        "UAS.DRONE_DOWNLINK",
    ),
    (
        "SENS",
        "UAS",
        "DRONE_GEO_FENCE",
        "UAS geo-fence / airspace",
        "Enforce geo-fence and airspace constraints for dispatched UAS.",
        ["respond", "coordinate"],
        "UAS",
        "UAS.DRONE_GEO_FENCE",
    ),
    (
        "SENS",
        "VIDEO",
        "ANALYTICS_DETECT",
        "Video analytics detection",
        "Video analytics for object/person/vehicle detection feeding alerts.",
        ["detect"],
        "VIDEO",
        "VIDEO.ANALYTICS_DETECT",
    ),
    (
        "SENS",
        "IOT",
        "SENSOR_FUSION",
        "Multi-sensor fusion",
        "Correlate multi-sensor events (video, ALPR, gunshot) into one picture.",
        ["detect", "coordinate"],
        "IOT",
        "IOT.SENSOR_FUSION",
    ),
    (
        "SENS",
        "VIDEO",
        "EXPORT_REDAC",
        "Video export / redaction",
        "Export and redact video for discovery, FOIA, and court packages.",
        ["after_action"],
        "VIDEO",
        "VIDEO.EXPORT_REDAC",
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
    sensors = sum(
        1
        for c in caps
        if c.get("vertical") in ("VIDEO", "IOT", "UAS")
        or c["id"].startswith("PSERS.SENS.")
        or c["id"].startswith("PSERS.PLAT.VMS.")
    )
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
        "sensors": sensors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand Sensors L1 (append/promote only)")
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
    for stack, domain, code, name, defn, missions, vertical, alias in NEW_SENSORS:
        cid = f"PSERS.{stack}.{domain}.{code}"
        if cid in existing_ids:
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
        added += 1

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
        "sprint": "P5-030",
        "published_at": doc.get("published_at"),
        "last_publish_tool": doc.get("last_publish_tool"),
        "last_priority_file": doc.get("last_priority_file"),
        "last_expand_tool": "ontology/expand_sensors_l1.py",
        "expanded_at": date.today().isoformat(),
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }
    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {L1_PATH} schema_version={ver} total={counts['total']} "
        f"stubs={counts['stubs']} sensors={counts['sensors']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
