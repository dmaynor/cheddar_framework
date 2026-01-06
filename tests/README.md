# Tests Directory

**Status:** `[PLANNED]` — Structure defined, implementation pending

## Purpose

This directory contains **pytest tests** for the Cheddar Python package, mirroring the structure of `src/cheddar/`.

## Planned Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Shared fixtures
├── fixtures/                    # Test data
│   └── artifacts/               # Example artifacts for testing
├── test_core/
│   ├── test_artifact.py
│   ├── test_lineage.py
│   └── test_schema.py
├── test_governance/
│   ├── test_policy.py
│   └── test_roles.py
├── test_lint/
│   ├── test_validate.py
│   ├── test_hash.py
│   └── test_chain.py
└── test_runtime/
    ├── test_session.py
    └── test_audit.py
```

## Testing Philosophy

From AGENTS.md:
- Prefer small, deterministic tests
- Drive tests with example Cheddar artifacts stored in `fixtures/`
- Test behavior, not implementation details

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=cheddar --cov-report=html

# Specific module
pytest tests/test_lint/

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Fixtures

Test fixtures use the canonical examples from `/schemas/examples/`:

```python
# conftest.py
import pytest
from pathlib import Path
import yaml

@pytest.fixture
def mission_artifact():
    path = Path(__file__).parent.parent / "schemas/examples/mission_definition.example.yaml"
    return yaml.safe_load(path.read_text())

@pytest.fixture
def artifact_chain():
    """Load complete artifact chain for integration tests."""
    examples_dir = Path(__file__).parent.parent / "schemas/examples"
    return {
        "mission": yaml.safe_load((examples_dir / "mission_definition.example.yaml").read_text()),
        "initiative": yaml.safe_load((examples_dir / "flow_initiative.example.yaml").read_text()),
        "track": yaml.safe_load((examples_dir / "cheddar_track.example.yaml").read_text()),
        "brief": yaml.safe_load((examples_dir / "automation_brief.example.yaml").read_text()),
        "personal": yaml.safe_load((examples_dir / "personal_artifact.example.yaml").read_text()),
    }
```

## Test Categories

### Unit Tests

Test individual functions in isolation:

```python
def test_compute_hash_deterministic(mission_artifact):
    """Hash computation should be deterministic."""
    hash1 = compute_hash(mission_artifact)
    hash2 = compute_hash(mission_artifact)
    assert hash1 == hash2

def test_compute_hash_excludes_hash_field(mission_artifact):
    """Hash should not include the hash field itself."""
    mission_artifact["lineage"]["hash"] = "old_hash"
    hash1 = compute_hash(mission_artifact)
    mission_artifact["lineage"]["hash"] = "new_hash"
    hash2 = compute_hash(mission_artifact)
    assert hash1 == hash2
```

### Integration Tests

Test component interactions:

```python
def test_validate_chain_integrity(artifact_chain):
    """Chain verification should pass for valid chain."""
    result = verify_chain(artifact_chain)
    assert result.valid
    assert len(result.errors) == 0

def test_policy_evaluation_blocks_prohibited(session_config, policy):
    """Prohibited actions should be denied."""
    action = Action(type="deploy_to_production", target="production")
    decision = evaluate_action(action, policy)
    assert decision == Decision.DENY
```

## Coverage Requirements

- Minimum 80% line coverage for core modules
- 100% coverage for invariant enforcement code
- All public APIs must have tests

## Next Steps

1. Create `conftest.py` with shared fixtures
2. Implement tests alongside source code
3. Set up CI/CD test automation
4. Add coverage reporting
