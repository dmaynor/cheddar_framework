# Tests Directory

**Status:** `[EXISTS]` — first tests landed; structure grows with the package

## Purpose

This directory contains **pytest tests** for Cheddar's tooling. Today the
tests exercise the lint scripts directly (via a `sys.path` shim in
`conftest.py`); when lint logic moves under `src/cheddar/` (Tier 1), the
imports move with it.

## Current Contents

```
tests/
├── README.md                    # This file
├── conftest.py                  # Repo paths + lint import shim
├── test_canonical_hash.py       # Golden vectors + conformance gaps for
│                                #   docs/canonical-serialization.md
└── test_examples_lint.py        # Full strict lint run on schemas/examples/
```

## What the hashing tests enforce

`test_canonical_hash.py` is the executable form of
`docs/canonical-serialization.md`:

- **Vector A** — byte-exact golden hash for a minimal mission artifact
- **Vector D** — `_`-prefixed runtime metadata is excluded from the hash
- **Live vectors** — every stored `lineage.hash` in `schemas/examples/`
  must verify against recomputation
- **Tamper detection** — content changes (including `signed_by`) change
  the hash; the stored `lineage.hash` field itself does not
- **Conformance gaps** — Vectors B (NFC) and C (prohibited types) are
  `xfail(strict=True)`: they document known gaps in
  `lint/compute_hash.py` and will force marker removal the moment the
  implementation becomes conformant

## Running Tests

```bash
pip install pytest pyyaml jsonschema

# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

CI runs the same suite (see `.github/workflows/ci.yml`).

## Testing Philosophy

From AGENTS.md:
- Prefer small, deterministic tests
- Drive tests with the canonical artifacts in `schemas/examples/`
- Test behavior, not implementation details

## Planned Growth (with Tier 1 package work)

```
tests/
├── test_core/        # artifact, lineage, schema modules
├── test_governance/  # policy engine, roles
└── test_runtime/     # sessions, audit logging
```

Coverage targets once the package exists: 80% line coverage minimum for
core modules; 100% for invariant-enforcement code.
