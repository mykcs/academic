#!/usr/bin/env python3
"""
generate-manifest.py — Regenerate meta/manifest.json from the working tree.

Walks every tracked file (via `git ls-files`), filters out paths that are
internal/derived (`.git`, `.omc`, `.github`), and writes a fresh manifest
to `meta/manifest.json` with the schema consumed by `sync.py`:

    [
      {"source": "<path>", "dest": "<path>", "size": <bytes>},
      ...
    ]

Why this exists:
- The previous manifest was hand-maintained and drifted from the working
  tree (ACAD-P0-003: 14 stale `dest` entries). Regeneration from the
  filesystem guarantees the manifest and reality match.
- The companion `validate-manifest` CI workflow (see
  .github/workflows/validate-manifest.yml) fails the build if the
  committed manifest is out of sync.

Usage:
    python3 scripts/generate-manifest.py             # write to meta/manifest.json
    python3 scripts/generate-manifest.py --check     # exit 1 if manifest is stale
    python3 scripts/generate-manifest.py --stdout    # print to stdout (for diffing)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterator, List, Optional, TypedDict

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = REPO_ROOT / "meta" / "manifest.json"

# Paths to exclude from the manifest. These are repo-internal / derived.
EXCLUDED_PREFIXES = (".git/", ".omc/", ".github/")


class ManifestEntry(TypedDict):
    source: str
    dest: str
    size: int


def _git_ls_files(repo_root: Path) -> List[str]:
    """Return the list of tracked paths in ``repo_root``."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _is_excluded(rel_path: str) -> bool:
    return any(rel_path.startswith(p) for p in EXCLUDED_PREFIXES)


def _build_entries(repo_root: Path) -> List[ManifestEntry]:
    entries: List[ManifestEntry] = []
    for rel_path in _git_ls_files(repo_root):
        if _is_excluded(rel_path):
            continue
        full_path = repo_root / rel_path
        if not full_path.is_file():
            # Symlinks to directories or broken symlinks: skip silently.
            continue
        try:
            size = full_path.stat().st_size
        except OSError:
            continue
        entries.append({"source": rel_path, "dest": rel_path, "size": size})
    return entries


def generate() -> List[ManifestEntry]:
    """Build the manifest entry list for the current working tree."""
    return _build_entries(REPO_ROOT)


def write_manifest(entries: List[ManifestEntry], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")


def load_manifest(path: Path = MANIFEST_PATH) -> Optional[List[ManifestEntry]]:
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        return None
    return data


def _entries_equal(a: List[ManifestEntry], b: List[ManifestEntry]) -> bool:
    """Compare two manifest entry lists ignoring order."""
    a_sorted = sorted(
        (e["source"], e["dest"], e["size"]) for e in a
    )
    b_sorted = sorted(
        (e["source"], e["dest"], e["size"]) for e in b
    )
    return a_sorted == b_sorted


def _diff_entries(
    current: List[ManifestEntry], fresh: List[ManifestEntry]
) -> Iterator[str]:
    current_dests = {e["dest"] for e in current}
    fresh_dests = {e["dest"] for e in fresh}
    for added in sorted(fresh_dests - current_dests):
        yield f"+ {added}"
    for removed in sorted(current_dests - fresh_dests):
        yield f"- {removed}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate meta/manifest.json from the working tree"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 (and print a diff) if manifest is out of sync, do not write",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the fresh manifest to stdout instead of writing to disk",
    )
    args = parser.parse_args()

    fresh = generate()

    if args.stdout:
        json.dump(fresh, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if args.check:
        current = load_manifest()
        if current is None:
            print(
                f"ERROR: manifest does not exist at {MANIFEST_PATH}",
                file=sys.stderr,
            )
            return 1
        if _entries_equal(current, fresh):
            return 0
        print(
            f"Manifest out of sync with working tree. Diff (manifest vs fresh):",
            file=sys.stderr,
        )
        for line in _diff_entries(current, fresh):
            print(line, file=sys.stderr)
        print(
            "\nRun 'python3 scripts/generate-manifest.py' to refresh.",
            file=sys.stderr,
        )
        return 1

    write_manifest(fresh, MANIFEST_PATH)
    print(f"Wrote {len(fresh)} entries to {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
