# Repository Agent guide

This repository is the canonical academic asset library. Read [`docs/agents/README.md`](docs/agents/README.md) before non-trivial changes, then inspect the root `README.md`, `meta/manifest.json` and task-relevant scripts/files.

Key rules:

- original/highest-quality assets owned here remain canonical; downstream copies do not become a second writable source;
- update/verify `meta/manifest.json` when the asset inventory changes;
- treat `scripts/sync.py` path/overwrite behavior as a cross-repository consumer contract;
- do not copy deployment/framework policy from a downstream website into this asset library;
- keep credentials and private operational data out of the repository;
- report downstream repositories that need re-sync after a canonical asset or sync-contract change.

Project structure, ownership and validation details live in `docs/agents/README.md`; keep this root file short so Agents can reach that context quickly.
