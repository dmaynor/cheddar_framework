# Cheddar Python Package

**Status:** `[PLANNED]` — Structure defined, implementation pending

## Purpose

This directory will contain the **Python implementation** of Cheddar tooling — validators, hash computation, policy engine, and CLI utilities.

## Planned Structure

```
src/
└── cheddar/
    ├── __init__.py              # Package initialization
    ├── cli.py                   # Command-line interface
    ├── core/                    # Core primitives
    │   ├── __init__.py
    │   ├── artifact.py          # Artifact data structures
    │   ├── lineage.py           # Hash and chain utilities
    │   └── schema.py            # Schema loading and validation
    ├── governance/              # Policy engine
    │   ├── __init__.py
    │   ├── policy.py            # Policy evaluation
    │   └── roles.py             # Role resolution
    ├── lint/                    # Validation utilities
    │   ├── __init__.py
    │   ├── validate.py          # Artifact validation
    │   ├── hash.py              # Hash computation
    │   └── chain.py             # Lineage chain verification
    └── runtime/                 # Session management
        ├── __init__.py
        ├── session.py           # AI session manager
        └── audit.py             # Audit logging
```

## Installation (Planned)

```bash
# From repository root
pip install -e .

# Or with optional dependencies
pip install -e ".[dev]"  # Development tools
pip install -e ".[all]"  # All optional features
```

## CLI Usage (Planned)

```bash
# Validate an artifact
cheddar validate path/to/artifact.yaml

# Compute lineage hash
cheddar hash path/to/artifact.yaml --update

# Verify chain integrity
cheddar verify-chain path/to/artifacts/

# Start AI session with policy
cheddar session start --policy governance/policy.yaml

# Query audit logs
cheddar audit query --artifact "brief_prkin_v1"
```

## Development

### Requirements

- Python 3.11+
- Dependencies in `pyproject.toml`

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cheddar

# Run specific test file
pytest tests/test_validate.py
```

### Code Style

- PEP 8 compliance
- Type annotations required
- Docstrings on all public functions
- See `AGENTS.md` for detailed guidelines

## Module Responsibilities

### `cheddar.core`

Core data structures and utilities:
- `Artifact`: Base class for all artifact types
- `LineageHash`: Hash computation and verification
- `Schema`: JSON Schema loading and validation

### `cheddar.governance`

Policy evaluation and role management:
- `Policy`: Load and evaluate governance policies
- `RoleResolver`: Resolve role permissions from catalog

### `cheddar.lint`

Validation and verification:
- `ArtifactValidator`: Schema and invariant validation
- `HashComputer`: Lineage hash computation
- `ChainVerifier`: Lineage chain integrity verification

### `cheddar.runtime`

Session and audit management:
- `SessionManager`: AI session lifecycle
- `AuditLogger`: Session action logging

## Next Steps

1. Create `pyproject.toml` with dependencies
2. Implement core data structures in `cheddar.core`
3. Implement validation in `cheddar.lint`
4. Add CLI interface
5. Write tests
