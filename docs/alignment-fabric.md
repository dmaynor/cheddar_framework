# Alignment Fabric

The alignment fabric is the merged context that every human and AI consults before acting. It is assembled from stacked artifacts and captured as `combined_context.yaml`.

## Combined Context
```yaml
# Minimal structure
mission_definition:
  title: "develop_best_vulnerability_scanner"
  intent: "Deliver a scanner with high accuracy and minimal false positives."
flow_initiative:
  title: "reduce_false_positives"
  goal: "Lower rate below 2%."
cheddar_track:
  title: "classifier_threshold_adjustment"
  issue: "Model threshold drift detected."
automation_brief:
  title: "retrain_model_with_recent_telemetry"
  tests: ["false_positive_rate_below_2_percent"]
```

### Rules of the Fabric
- Intent moves downward through artifacts; feedback moves upward with evidence and telemetry.
- Every file contributes a cryptographic hash to the lineage chain.
- Humans and AI operate from the exact same merged context.

### Building a Session Context
```yaml
session_context:
  load_from:
    - "../artifacts/mission_definition.yaml"
    - "../artifacts/flow_initiative.yaml"
    - "../artifacts/cheddar_track.yaml"
    - "../artifacts/automation_brief.yaml"
  merge_order: "top_to_bottom"
  output_prompt: "session_prompt.yaml"
```

Use a helper such as:
```bash
build_context_chain --mission mission_definition.yaml \
                    --flow flow_initiative.yaml \
                    --cheddar cheddar_track.yaml \
                    --automation automation_brief.yaml \
                    --output session_prompt.yaml
```

### Bidirectional Contracts
Each artifact documents how it **supports** the layer above and **enables** the layer below:

- `supports_upper_layer`: How this artifact fulfills upstream goals.
- `enables_lower_layer`: How it empowers the next layer down.
- `upward_feedback`: Conditions that trigger escalation upward.
- `downward_contract`: Deliverables guaranteed downstream.

### Roles and Imports
Authority is declared explicitly via imported role catalogs under `/roles/` so every contract has a signed owner.
