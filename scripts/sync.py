#!/usr/bin/env python3
"""
sync.py — Pull assets from academic library into a consumer project.

Usage:
    python3 scripts/sync.py --target ./vendor/academic
    python3 scripts/sync.py --target ./vendor/academic --papers cvpr2026-osa
"""

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Iterable, Optional

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent

logger = logging.getLogger("academic.sync")


def sync(
    target_dir: str,
    filters: Optional[Iterable[str]] = None,
) -> int:
    """Copy manifest entries from academic repo to ``target_dir``.

    Returns the number of files successfully copied.
    """
    target = Path(target_dir).resolve()
    manifest_path = REPO_ROOT / "meta" / "manifest.json"

    if not manifest_path.exists():
        logger.error("Manifest not found: %s", manifest_path)
        sys.exit(1)

    with open(manifest_path) as f:
        manifest: list[dict] = json.load(f)

    filters_list = list(filters) if filters else None
    copied = 0
    skipped = 0
    missing = 0

    for entry in manifest:
        dest_rel: str = entry["dest"]
        src = REPO_ROOT / dest_rel
        dst = target / dest_rel

        if filters_list and not any(f in dest_rel for f in filters_list):
            skipped += 1
            continue

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        else:
            missing += 1
            logger.warning("Source missing: %s", src)

    logger.info("Synced %d files to %s", copied, target)
    if skipped:
        logger.info("Skipped %d files (filtered)", skipped)
    if missing:
        logger.warning("%d manifest entries had no source on disk", missing)
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync academic assets to consumer project"
    )
    parser.add_argument(
        "--target", required=True, help="Target directory in consumer project"
    )
    parser.add_argument(
        "--papers",
        nargs="+",
        help="Filter by paper slug (e.g. cvpr2026-osa)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    sync(args.target, filters=args.papers)


if __name__ == "__main__":
    main()
