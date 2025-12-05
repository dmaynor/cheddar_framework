# Intent Graph Workflows

Ticket queues freeze dynamic problems into static forms. Cheddar replaces tickets with intent graphs that preserve context and learning.

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
