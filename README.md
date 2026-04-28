# Cheddar Framework

Cheddar is a PM/accountability framework for AI-augmented organizations. It aligns missions, initiatives, tasks, and automation through signed, traceable artifacts that humans and AI share.

## Quick Start

1. Read `docs/domain-model.md`
2. Review `docs/invariants.md`
3. Explore `schemas/examples/`
4. Browse `docs/`

## Validation

Run directly through the lint scripts:

```bash
python lint/run_all.py --examples --strict
```

Or install the package in editable mode from a repository checkout and use the CLI wrapper:

```bash
python -m pip install -e .
cheddar lint --examples --strict
```

Current CLI limitation: `cheddar lint` is a thin wrapper over `lint/run_all.py` and expects a repository checkout/editable install. A future package refactor should move lint internals under `src/cheddar/` for wheel-safe execution.

## Documentation Map

### Core
- docs/domain-model.md
- docs/invariants.md
- schemas/

### Guides
- docs/overview.md
- docs/artifact-hierarchy.md
- docs/ai-integration.md

## Repository Status

| Component | Status |
|-----------|--------|
| Domain model | EXISTS |
| Invariants | EXISTS |
| Schemas | PARTIAL (SHA256 enforcement added) |
| Validation tooling | PARTIAL (strict mode added) |
| Examples | PARTIAL (lineage normalized) |
| Python package | PARTIAL (minimal editable-install CLI wrapper added) |

## Current Reality

- Deterministic hashing (metadata-safe)
- Strict linting (no silent bypass)
- Full SHA256 enforcement across schemas
- Example lineage chains use real hashes
- Minimal `cheddar lint` CLI wrapper for repository checkout/editable installs

## Meta-Rule

Cheddar must never claim reality it cannot enforce.
