# Academic Asset Library

Centralized media and data repository for all academic outputs.

## Structure

```
academic/
├── images/
│   ├── avatar/
│   │   └── avatar.png
│   ├── logos/
│   │   ├── polyu.svg
│   │   ├── szu.svg
│   │   ├── cvpr.svg
│   │   └── iccv.png
│   └── papers/
│       ├── cvpr2026-osa/      # CVPR 2026 OSA paper figures
│       └── iccv2025-gdkvm/    # ICCV 2025 GDKVM paper figures
├── data/                       # Structured data (citations, stats)
├── meta/
│   └── manifest.json          # Asset inventory
└── scripts/
    └── sync.py                # Consumer sync script
```

## Usage

Consumers (websites, slides, posters) run the sync script to pull assets:

```bash
python3 scripts/sync.py --target ~/projects/my-website/vendor/academic
```

Or clone as a submodule:

```bash
git submodule add https://github.com/mykcs/academic.git vendor/academic
```

## Single Source of Truth

- **Original figures** live here (highest quality)
- **Compressed variants** are generated at build time
- **Metadata** (paper titles, authors, links) will be added to `meta/`

## Adding New Assets

1. Place original file in the appropriate `images/` subdirectory
2. Update `meta/manifest.json`
3. Commit and push
4. Consumers re-run sync
