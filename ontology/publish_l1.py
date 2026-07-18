"""Promote L1 capabilities draft → published (Phase-2 FR-1 / Phase 3 Lite FR-P3.1).

Default selection: ontology/top50_bid_desk.json aliases.
Wave 2: --priority-file ontology/top50_wave2.json
Refuses to publish stub rows. Does not rewrite definitions or IDs.

Usage:
  py -3.12 ontology/publish_l1.py --dry-run
  py -3.12 ontology/publish_l1.py
  py -3.12 ontology/publish_l1.py --priority-file ontology/top50_wave2.json
  py -3.12 ontology/publish_l1.py --alias LMR.STD.P25_PHASE1
  py -3.12 ontology/publish_l1.py --id PSERS.PLAT.CAD.SOME_STUB --fail-on-stub
  py -3.12 ontology/publish_l1.py --deprecate --alias LMR.STD.P25_PHASE1

Note: ontology/generate_l1.py regenerates from scratch and resets status to draft.
Re-run this publish CLI after regenerate (see docs/l1-publish-checklist.md).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1_PATH = Path(__file__).with_name("l1_capabilities.json")
TOP50_PATH = Path(__file__).with_name("top50_bid_desk.json")
DECISION_LOG = ROOT / "docs" / "decision-log.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_caps(caps: list[dict]) -> tuple[dict[str, dict], dict[str, dict]]:
    by_id = {c["id"]: c for c in caps}
    by_alias = {c["alias"]: c for c in caps if c.get("alias")}
    return by_id, by_alias


def resolve_targets(
    aliases: list[str],
    ids: list[str],
    by_id: dict[str, dict],
    by_alias: dict[str, dict],
) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    seen: set[str] = set()
    resolved: list[dict] = []

    for alias in aliases:
        row = by_alias.get(alias)
        if row is None:
            errors.append(f"unresolved alias: {alias}")
            continue
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        resolved.append(row)

    for cid in ids:
        row = by_id.get(cid)
        if row is None:
            errors.append(f"unresolved id: {cid}")
            continue
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        resolved.append(row)

    return resolved, errors


def recount(caps: list[dict]) -> dict[str, int]:
    stubs = sum(1 for c in caps if c["status"] == "stub")
    published = sum(1 for c in caps if c["status"] == "published")
    deprecated = sum(1 for c in caps if c["status"] == "deprecated")
    draft = sum(1 for c in caps if c["status"] == "draft")
    # lmr_draft key = non-stub inventory (legacy validator / generate_l1 naming)
    return {
        "total": len(caps),
        "draft": draft,
        "published": published,
        "deprecated": deprecated,
        "stubs": stubs,
        "lmr_draft": draft + published + deprecated,
    }


def bump_schema_version(ver: str) -> str:
    parts = ver.split(".")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}.{int(parts[1]) + 1}"
    if len(parts) >= 3 and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    return f"{ver}+1"


def append_decision_log(
    *,
    action: str,
    published_ids: list[str],
    skipped_stubs: list[str],
    catalog_version: str,
    priority_source: str,
    sprint: str,
) -> None:
    today = date.today().isoformat()
    lines = [
        "",
        f"## {today} — L1 publish batch ({action})",
        "",
        f"- Catalog `schema_version`: **{catalog_version}**",
        f"- Sprint: **{sprint}**",
        f"- Promoted to `{action}`: **{len(published_ids)}** capabilities",
        f"- Stub refusals: **{len(skipped_stubs)}**",
        f"- Tool: `ontology/publish_l1.py`",
        f"- Priority source: `{priority_source}`",
    ]
    if published_ids:
        preview = ", ".join(published_ids[:8])
        more = f" (+{len(published_ids) - 8} more)" if len(published_ids) > 8 else ""
        lines.append(f"- Sample IDs: {preview}{more}")
    if skipped_stubs:
        lines.append(f"- Skipped stubs: {', '.join(skipped_stubs)}")
    lines.append("")
    DECISION_LOG.write_text(
        DECISION_LOG.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish (or deprecate) L1 capabilities")
    parser.add_argument(
        "--top50",
        type=Path,
        default=TOP50_PATH,
        help="JSON with aliases list (default: top50_bid_desk.json); alias for --priority-file",
    )
    parser.add_argument(
        "--priority-file",
        type=Path,
        default=None,
        help="JSON with aliases list (overrides --top50). Use ontology/top50_wave2.json for wave 2.",
    )
    parser.add_argument(
        "--sprint",
        default=None,
        help="Catalog sprint label (default: P2-001, or P3-010 when priority file is wave2)",
    )
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        help="Publish this alias (repeatable). If any --alias/--id given, priority-file default is off.",
    )
    parser.add_argument(
        "--id",
        dest="ids",
        action="append",
        default=[],
        help="Publish this capability id (repeatable)",
    )
    parser.add_argument(
        "--deprecate",
        action="store_true",
        help="Set status to deprecated instead of published",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve and report without writing files",
    )
    parser.add_argument(
        "--no-decision-log",
        action="store_true",
        help="Skip appending docs/decision-log.md",
    )
    parser.add_argument(
        "--fail-on-stub",
        action="store_true",
        help="Exit non-zero if any selected target is a stub",
    )
    args = parser.parse_args()

    doc = load_json(L1_PATH)
    caps: list[dict] = doc["capabilities"]
    by_id, by_alias = index_caps(caps)

    priority_path = args.priority_file or args.top50
    if not priority_path.is_absolute():
        rooted = ROOT / priority_path
        priority_path = rooted if rooted.exists() else Path(priority_path).resolve()
    else:
        priority_path = priority_path.resolve()

    if args.alias or args.ids:
        aliases = list(args.alias)
        ids = list(args.ids)
        priority_label = "cli --alias/--id"
    else:
        priority_doc = load_json(priority_path)
        aliases = list(priority_doc["aliases"])
        ids = []
        try:
            priority_label = str(priority_path.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            priority_label = str(priority_path)

    sprint = args.sprint
    if sprint is None:
        sprint = "P3-010" if "wave2" in priority_path.name.lower() else "P2-001"

    resolved, errors = resolve_targets(aliases, ids, by_id, by_alias)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    new_status = "deprecated" if args.deprecate else "published"
    skipped_stubs: list[str] = []
    to_change: list[dict] = []
    already: list[str] = []

    for row in resolved:
        if row["status"] == "stub":
            print(
                f"SKIP: refusing stub: {row['id']} (alias={row.get('alias')})",
                file=sys.stderr,
            )
            skipped_stubs.append(row["id"])
            continue
        if row["status"] == new_status:
            already.append(row["id"])
            continue
        to_change.append(row)

    if skipped_stubs and args.fail_on_stub:
        print(f"FAIL: {len(skipped_stubs)} stub(s) in selection", file=sys.stderr)
        return 1

    summary = {
        "dry_run": args.dry_run,
        "action": new_status,
        "sprint": sprint,
        "priority_file": priority_label,
        "resolved": len(resolved),
        "would_change": len(to_change),
        "already": len(already),
        "skipped_stubs": skipped_stubs,
        "sample_ids": [r["id"] for r in to_change[:5]],
    }
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("Dry-run only; no files written.", file=sys.stderr)
        return 0

    if not to_change:
        print("Nothing to change.", file=sys.stderr)
        return 0

    changed_ids: list[str] = []
    for row in to_change:
        row["status"] = new_status
        changed_ids.append(row["id"])

    ver = bump_schema_version(str(doc.get("schema_version", "1.0")))
    today = date.today().isoformat()
    counts = recount(caps)
    out = {
        "schema_version": ver,
        "root": doc.get("root", "PSERS"),
        "sprint": sprint,
        "published_at": today,
        "last_publish_tool": "ontology/publish_l1.py",
        "last_priority_file": priority_label,
        "generated_by": doc.get("generated_by"),
        "counts": counts,
        "capabilities": caps,
    }

    L1_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {L1_PATH} schema_version={ver} changed={len(changed_ids)}", file=sys.stderr)

    if not args.no_decision_log:
        append_decision_log(
            action=new_status,
            published_ids=changed_ids,
            skipped_stubs=skipped_stubs,
            catalog_version=ver,
            priority_source=priority_label,
            sprint=sprint,
        )
        print(f"Appended {DECISION_LOG}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
