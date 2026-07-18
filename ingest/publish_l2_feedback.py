"""Publish staged analyst feedback from l2_review_queue.json into l2_synonyms.json.

Only action=accept|correct with status!=published are merged.
Rejects are never merged. Dedupes on normalized phrase + capability_id.

Usage:
  py -3.12 ingest/publish_l2_feedback.py --dry-run
  py -3.12 ingest/publish_l2_feedback.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.extract_l2_synonyms import normalize_key  # noqa: E402

QUEUE_PATH = ROOT / "ontology" / "l2_review_queue.json"
L2_PATH = ROOT / "ontology" / "l2_synonyms.json"
L1_PATH = ROOT / "ontology" / "l1_capabilities.json"

PUBLISHABLE = {"accept", "correct"}


def phrase_id(phrase: str, capability_id: str) -> str:
    return hashlib.sha1(f"analyst_ui|{capability_id}|{phrase}".encode("utf-8")).hexdigest()[:12]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_keys(synonyms: list[dict]) -> set[tuple[str, str]]:
    return {(normalize_key(s["phrase"]), s["capability_id"]) for s in synonyms}


def load_review_queue(queue_path: Path = QUEUE_PATH) -> dict:
    if not queue_path.exists():
        return {"schema_version": "1.0", "items": [], "updated_at": None}
    return load_json(queue_path)


def publish_review_queue(
    *,
    dry_run: bool = False,
    queue_path: Path = QUEUE_PATH,
    l2_path: Path = L2_PATH,
) -> dict:
    """Merge pending accept/correct queue items into L2. Returns summary dict."""
    if not queue_path.exists():
        raise FileNotFoundError(f"missing queue: {queue_path}")

    queue = load_json(queue_path)
    l2 = load_json(l2_path)
    l1_caps = load_json(L1_PATH)["capabilities"]
    l1_ids = {c["id"] for c in l1_caps}
    alias_by_id = {c["id"]: c.get("alias") for c in l1_caps}
    synonyms: list[dict] = list(l2["synonyms"])
    keys = existing_keys(synonyms)

    added = 0
    skipped_dup = 0
    skipped_reject = 0
    skipped_published = 0
    skipped_bad = 0
    marked = 0
    now = datetime.now(timezone.utc).isoformat()
    before = len(synonyms)

    for item in queue.get("items", []):
        action = item.get("action", "")
        status = item.get("status", "pending")

        if action == "reject":
            skipped_reject += 1
            continue
        if action not in PUBLISHABLE:
            skipped_bad += 1
            continue
        if status == "published":
            skipped_published += 1
            continue

        phrase = (item.get("phrase") or "").strip()
        cid = item.get("capability_id") or ""
        if not phrase or not cid:
            skipped_bad += 1
            continue
        if cid not in l1_ids:
            skipped_bad += 1
            continue

        key = (normalize_key(phrase), cid)
        if key in keys:
            skipped_dup += 1
            if not dry_run:
                item["status"] = "published"
                item["published_at"] = now
                item["publish_note"] = "already_in_l2"
                marked += 1
            continue

        alias = item.get("capability_alias") or alias_by_id.get(cid)
        row = {
            "phrase": phrase,
            "source_doc_id": "analyst_ui",
            "source_file": "analyst_ui",
            "page": None,
            "phrase_id": phrase_id(phrase, cid),
            "capability_id": cid,
            "capability_alias": alias,
            "confidence": 0.95,
            "match_method": "feedback",
            "status": "analyst_accepted",
            "feedback_action": action,
            "feedback_note": item.get("note") or "",
            "feedback_ts": item.get("ts"),
        }
        added += 1
        if not dry_run:
            synonyms.append(row)
            keys.add(key)
            item["status"] = "published"
            item["published_at"] = now
            item["publish_note"] = "merged"
            marked += 1

    summary = {
        "dry_run": dry_run,
        "added": added,
        "skipped_dup": skipped_dup,
        "skipped_reject": skipped_reject,
        "skipped_published": skipped_published,
        "skipped_bad": skipped_bad,
        "queue_marked_published": marked,
        "synonyms_before": before,
        "synonyms_after": before + added if dry_run else len(synonyms),
    }

    if dry_run:
        return summary

    if added or marked:
        l2["synonyms"] = synonyms
        l2["counts"]["synonyms"] = len(synonyms)
        l2["counts"]["capabilities_with_synonyms"] = len({s["capability_id"] for s in synonyms})
        l2["last_feedback_publish"] = now
        l2["sprint"] = "P3-012"
        l2_path.write_text(json.dumps(l2, indent=2) + "\n", encoding="utf-8")
        queue_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish L2 review queue → l2_synonyms.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--queue", type=Path, default=QUEUE_PATH)
    ap.add_argument("--l2", type=Path, default=L2_PATH)
    args = ap.parse_args()

    try:
        summary = publish_review_queue(
            dry_run=args.dry_run,
            queue_path=args.queue,
            l2_path=args.l2,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2))
    if not args.dry_run and (summary["added"] or summary["queue_marked_published"]):
        print(f"Wrote {args.l2}", file=sys.stderr)
        print(f"Wrote {args.queue}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
