# Agent documentation

This is the stable Agent entrypoint for the `academic` asset library.

The repository is a **source-of-truth library for original academic assets and their inventory**, not a website application and not a generated cache copied from downstream projects.

## Read first

1. root [`README.md`](../../README.md) — library purpose, sync usage and human-facing structure;
2. this file — Agent ownership and change rules;
3. [`meta/manifest.json`](../../meta/manifest.json) — current machine-readable asset inventory;
4. [`scripts/generate-manifest.py`](../../scripts/generate-manifest.py) — manifest generation logic;
5. [`scripts/sync.py`](../../scripts/sync.py) — downstream consumer sync behavior;
6. [`scripts/README.md`](../../scripts/README.md) when changing portability/symlink behavior.

## Source-of-truth boundary

```text
academic/
├── images/
│   ├── avatar/             original avatar assets
│   ├── logos/              original institution/conference logos
│   └── papers/             original paper/project figures
├── transcripts/            academic transcript assets
├── data/                   structured academic data when populated
├── meta/manifest.json      generated/maintained asset inventory
├── scripts/                manifest + consumer-sync tooling
└── docs/agents/            stable Agent orientation
```

Original/highest-quality academic assets belong here when this repository is their declared owner. Downstream websites, slides and posters may consume synchronized copies, but those copies do not become a second writable SSOT.

## Change rules

- Preserve original-quality source assets; generate/compress downstream variants rather than replacing originals with lower-quality copies.
- Put new assets into the existing semantic category when one exists instead of creating near-duplicate folder taxonomies.
- After asset additions/removals/renames, regenerate or deliberately update `meta/manifest.json` using the repository tooling and verify the diff.
- When changing `scripts/sync.py`, consider all consumers: path stability and overwrite behavior are cross-repository contracts.
- Do not commit secrets or private operational credentials merely because this repository contains academic material.
- Do not import a downstream website's deployment, framework or build policy into this asset library.

## Consumer rule

A downstream project that needs these assets should consume them through the documented sync/submodule mechanism or another explicit integration contract. Agents should edit the canonical asset here first when the desired change is to the original, then update the consumer through its own repository workflow.

If a downstream project intentionally owns a transformed derivative, document that boundary there rather than making both repositories claim the same source file as canonical.

## Knowledge precedence

```text
current user instruction
> files + manifest + sync/generation scripts in this repository
> this Agent entrypoint / root README
> downstream copies or old project notes
```

A downstream copy never overrides the original-asset ownership declared here.

## Validation

For asset-library changes:

1. inspect the exact changed files and paths;
2. regenerate/verify the manifest when inventory changed;
3. run the relevant sync logic when a consumer contract changed;
4. check that no unexpected files, credentials or generated bulk artifacts were introduced;
5. report which downstream consumers, if any, require a follow-up synchronization.

## Maintenance rule

Keep this file focused on durable ownership, structure and consumer contracts. Add a separate dated history note only when a migration/incident has future diagnostic value; do not turn this entrypoint into a chronological diary.
