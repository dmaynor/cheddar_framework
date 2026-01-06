# Cheddar Schemas

This directory contains canonical schema definitions and examples for Cheddar artifacts.

## Directory Structure

```
schemas/
├── README.md                           # This file
├── common.schema.json                  # Shared definitions
├── mission_definition.schema.json      # Mission artifact schema
├── flow_initiative.schema.json         # Initiative artifact schema
├── cheddar_track.schema.json           # Track artifact schema
├── automation_brief.schema.json        # Brief artifact schema
├── personal_artifact.schema.json       # Personal artifact schema
├── documentation_log.schema.json       # Log entry schema
└── examples/                           # Human-readable example artifacts
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
| JSON Schema definitions | `[EXISTS]` |
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

### For Validation

JSON Schema definitions exist and can be used with any JSON Schema validator:

```python
import json
import yaml
from jsonschema import validate, ValidationError
from pathlib import Path

def validate_artifact(artifact_path: str, schema_name: str) -> bool:
    """Validate a Cheddar artifact against its schema."""
    schema_path = Path(__file__).parent / "schemas" / f"{schema_name}.schema.json"
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    with open(artifact_path) as f:
        artifact = yaml.safe_load(f)
    
    try:
        validate(instance=artifact, schema=schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

# Example usage
validate_artifact("my_mission.yaml", "mission_definition")
```

CLI validation (planned):

```bash
# [PLANNED] - lint/ implementation pending
cheddar validate --schema schemas/mission_definition.schema.json artifact.yaml
```

## JSON Schema Reference

| Schema | Validates | Key Constraints |
|--------|-----------|-----------------|
| `common.schema.json` | Shared definitions | Lineage block, cheddar_state enum |
| `mission_definition.schema.json` | Mission artifacts | `level` must be "mission", `upstream_hash` must be null |
| `flow_initiative.schema.json` | Initiative artifacts | `supports_upper_layer` must reference mission |
| `cheddar_track.schema.json` | Track artifacts | `supports_upper_layer` must reference flow |
| `automation_brief.schema.json` | Brief artifacts | `supports_upper_layer` must reference track |
| `personal_artifact.schema.json` | Personal artifacts | `cheddar_state` is required |
| `documentation_log.schema.json` | Log files | Entries array with cheddar_stats |

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
