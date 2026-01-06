# Intent Graph Workflows

Ticket queues freeze dynamic problems into static forms. Cheddar replaces tickets with intent graphs that preserve context and learning.

> **Note:** Intent graphs are **derived views** computed from the canonical artifact hierarchy, not a separate data structure. See [ADR-001](adr/ADR-001-hierarchy-is-canonical.md) for the architectural decision.

## Relationship to Artifact Hierarchy

The artifact hierarchy (`mission → flow_initiative → cheddar_track → automation_brief → personal_artifact`) is the **source of truth**. Intent graphs are generated from artifact relationships for:

- **Visualization:** Interactive diagrams showing artifact dependencies
- **Analysis:** Computing metrics like path length, bottlenecks, orphaned nodes
- **Workflow:** Powering UI features like "show me everything blocking this mission"

Intent nodes and intent graphs do not replace the `supports_upper_layer` field in artifacts — they visualize it.

## Diagnosis: Why Ticketing Breaks
- Tickets reward closure, not comprehension.
- Each update re-translates context already present in telemetry or code.
- Humans and AI remain context-blind because information is scattered across forms.

## Replacement: Intent Nodes
```yaml
intent_node:
  id: intent_reduce_false_positives
  description: "Resolve false-positive spike in scan telemetry."
  dependencies: [telemetry_pipeline, model_thresholds]
  confidence: 0.91
  entropy: 0.47
  owner: "ai_ops_team"
  updated_at: "2025-10-30T11:00:00Z"
```

### How Intent Graphs Flow
- Nodes stay **living statements of purpose**, not static cases.
- Edges encode dependencies and confidence, letting AI/Humans co-author the path to resolution.
- Context propagates automatically rather than moving tickets through queues.

### Operational Outcomes
- Reduced information loss at handoffs.
- Real-time shared understanding for humans and AI.
- Metrics shift from SLA/MTTR to entropy reduction and confidence.
