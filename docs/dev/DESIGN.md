# Dev design — academic

The development model separates:
- canonical academic source data/assets;
- deterministic generation/check scripts;
- hosted validation of source/manifest consistency;
- downstream publication surfaces.

GitHub Actions is appropriate here for lightweight portable manifest/release validation. Do not make every content update run unrelated heavy work, and do not treat a generated site as the canonical academic record.
