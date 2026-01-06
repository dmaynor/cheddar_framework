# Cheddar Schemas

This directory contains canonical schema definitions and examples for Cheddar artifacts.

## Directory Structure

```
schemas/
├── README.md                 # This file
└── examples/                 # Human-readable example artifacts
    ├── mission_definition.example.yaml
    ├── flow_initiative.example.yaml
    ├── cheddar_track.example.yaml
    ├── automation_brief.example.yaml
    ├── personal_artifact.example.yaml
    └── documentation_log.example.yaml
```

## Status

| Component | Status |
|-----------|--------|
| Example artifacts | `[EXISTS]` |
| JSON Schema definitions | `[PLANNED]` |
| Validation tooling | `[PLANNED]` |

## Usage

### As Documentation

The example files in `examples/` demonstrate the canonical structure of each artifact type. They are the authoritative reference for field names, required fields, and relationships.

### As Test Fixtures

Example files can be used as fixtures for testing Cheddar tooling:

```python
import yaml
from pathlib import Path

def load_example(name: str) -> dict:
    path = Path(__file__).parent / "schemas" / "examples" / f"{name}.example.yaml"
    return yaml.safe_load(path.read_text())

# Load mission example
mission = load_example("mission_definition")
```

### For Validation (Planned)

When JSON Schema definitions are added, validate artifacts like:

```bash
# [PLANNED] - Not yet implemented
cheddar validate --schema schemas/mission.schema.json artifact.yaml
```

## Field Requirements

See [docs/domain-model.md](../docs/domain-model.md) for complete field definitions.

### Required Fields (All Artifacts)

| Field | Description |
|-------|-------------|
| `level` | Artifact type identifier |
| `id` | Stable unique identifier with version |
| `title` | Snake_case descriptive name |
| `lineage` | Cryptographic provenance block |

### Required Fields (Non-Mission Artifacts)

| Field | Description |
|-------|-------------|
| `supports_upper_layer` | ID of parent artifact |

## Contributing Examples

When adding new examples:

1. Follow the naming convention: `{artifact_type}.example.yaml`
2. Include comments explaining required vs optional fields
3. Use realistic but anonymized data
4. Ensure lineage hash references are consistent (parent hash matches child's upstream_hash)
5. Update this README

## Lineage Chain Consistency

The example files demonstrate a complete lineage chain:

```
mission_example_v1
  └── flow_reduce_false_positives_v1
        └── track_classifier_threshold_drift_v1
              └── brief_retrain_classifier_v1
                    └── personal_train_model_alice_v1
```

Each artifact's `lineage.upstream_hash` matches its parent's `lineage.hash`, demonstrating proper chain continuity.
