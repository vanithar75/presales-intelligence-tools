"""L1 coverage / quality audit (Phase 10 Lite) — deterministic, no LLM.

Reports:
  - published caps missing alias, mission, or description
  - draft backlog by domain
  - optional phrase hit-rate on a text fixture

Usage:
  python3 ontology/l1_coverage_audit.py
  python3 ontology/l1_coverage_audit.py --fixture ontology/samples/demo_requirements.txt
  python3 ontology/l1_coverage_audit.py --fail-on-quality
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = Path(__file__).with_name("l1_capabilities.json")


def domain_of(cap: dict) -> str:
    alias = cap.get("alias") or ""
    if "." in alias:
        return alias.split(".")[0]
    cid = cap.get("id") or ""
    parts = cid.split(".")
    return parts[2] if len(parts) >= 3 else "?"


def audit(caps: list[dict]) -> dict:
    published = [c for c in caps if c.get("status") == "published"]
    draft = [c for c in caps if c.get("status") == "draft"]
    quality_issues = []
    for c in published:
        issues = []
        if not c.get("alias"):
            issues.append("missing_alias")
        tags = c.get("mission_tags") or c.get("missions") or c.get("mission")
        if not tags:
            issues.append("missing_mission_tags")
        desc = (c.get("definition") or c.get("description") or "").strip()
        if len(desc) < 12:
            issues.append("thin_definition")
        if issues:
            quality_issues.append(
                {"id": c.get("id"), "alias": c.get("alias"), "issues": issues}
            )
    draft_by = Counter(domain_of(c) for c in draft)
    pub_by = Counter(domain_of(c) for c in published)
    return {
        "counts": {
            "total": len(caps),
            "published": len(published),
            "draft": len(draft),
            "stub": sum(1 for c in caps if c.get("status") == "stub"),
            "quality_issues": len(quality_issues),
        },
        "published_by_domain": dict(sorted(pub_by.items(), key=lambda x: -x[1])),
        "draft_by_domain": dict(sorted(draft_by.items(), key=lambda x: -x[1])),
        "quality_issues_sample": quality_issues[:25],
    }


def fixture_hit_rate(path: Path) -> dict:
    sys.path.insert(0, str(ROOT))
    from ingest.matcher import match_text

    text = path.read_text(encoding="utf-8")
    rows = match_text(text, top_k=3)
    mapped = sum(1 for r in rows if not r.get("unmapped"))
    return {
        "fixture": str(path),
        "requirements": len(rows),
        "mapped": mapped,
        "unmapped": len(rows) - mapped,
        "map_rate": round(mapped / len(rows), 3) if rows else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="L1 coverage / quality audit")
    ap.add_argument("--fixture", type=Path, default=None)
    ap.add_argument("--fail-on-quality", action="store_true")
    ap.add_argument("--max-issues", type=int, default=0, help="Fail if quality issues > N")
    args = ap.parse_args()
    caps = json.loads(L1.read_text(encoding="utf-8"))["capabilities"]
    report = audit(caps)
    if args.fixture:
        report["fixture"] = fixture_hit_rate(args.fixture)
    print(json.dumps(report, indent=2))
    if args.fail_on_quality and report["counts"]["quality_issues"] > args.max_issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
