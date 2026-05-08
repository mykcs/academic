#!/usr/bin/env python3
"""
sync.py — Pull assets from academic library into a consumer project.

Usage:
    python3 scripts/sync.py --target ./vendor/academic
    python3 scripts/sync.py --target ./vendor/academic --papers cvpr2026-osa
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent


def sync(target_dir, filters=None):
    target = Path(target_dir).resolve()
    manifest_path = REPO_ROOT / "meta" / "manifest.json"

    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    copied = 0
    skipped = 0

    for entry in manifest:
        dest_rel = entry["dest"]
        src = REPO_ROOT / dest_rel
        dst = target / dest_rel

        if filters:
            if not any(f in dest_rel for f in filters):
                skipped += 1
                continue

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"Warning: source missing: {src}", file=sys.stderr)

    print(f"Synced {copied} files to {target}")
    if skipped:
        print(f"Skipped {skipped} files (filtered)")


def main():
    parser = argparse.ArgumentParser(description="Sync academic assets to consumer project")
    parser.add_argument("--target", required=True, help="Target directory in consumer project")
    parser.add_argument("--papers", nargs="+", help="Filter by paper slug (e.g. cvpr2026-osa)")
    args = parser.parse_args()

    sync(args.target, filters=args.papers)


if __name__ == "__main__":
    main()
