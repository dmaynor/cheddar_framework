# ADR-001: Artifact Hierarchy is Canonical

**Status:** Accepted  
**Date:** 2026-01-06  
**Deciders:** Framework architects  

---

## Context

Cheddar artifacts form a directed acyclic graph (DAG) through `supports_upper_layer` references:

```
mission_definition
    └──► flow_initiative
            └──► cheddar_track
                    └──► automation_brief
                            └──► personal_artifact
```

Separately, the framework includes the concept of "intent nodes" and "intent graphs" — a workflow pattern where nodes represent living statements of purpose with confidence scores, entropy measures, and dynamic dependencies.

The question: **Which representation is authoritative when they conflict?**

---

## Decision

**The artifact hierarchy is canonical. Intent graphs are derived views.**

### What This Means

1. **Source of Truth:** The `supports_upper_layer` field in YAML artifacts defines the authoritative parent-child relationships.

2. **Intent Graphs Are Computed:** Intent graphs are generated from artifact relationships, not stored separately. They exist for visualization and workflow tooling, not as persistent data structures.

3. **No Dual Maintenance:** There is exactly one place to update relationships — the artifact files themselves. Intent graph renderings automatically reflect artifact changes.

4. **Lineage Follows Hierarchy:** The `lineage.upstream_hash` field always references the artifact identified by `supports_upper_layer`. There is no separate "intent lineage."

---

## Rationale

### Why Hierarchy Over Intent Graphs

| Factor | Hierarchy | Intent Graph |
|--------|-----------|--------------|
| **Simplicity** | Single file per artifact | Requires separate graph store |
| **Auditability** | Git history tracks all changes | Graph changes harder to audit |
| **Portability** | YAML files work anywhere | Graph DB adds dependencies |
| **Conflict Resolution** | Impossible (single source) | Requires reconciliation logic |
| **Human Readability** | Direct file inspection | Requires tooling to visualize |

### Intent Graphs Still Have Value

Intent graphs remain useful as:
- **Visualization:** Render artifact relationships as interactive diagrams
- **Analysis:** Compute metrics like path length, bottlenecks, orphaned nodes
- **Workflow:** Power UI features like "show me everything blocking this mission"

The key insight: these are **read operations** on the canonical hierarchy, not a parallel data structure.

---

## Consequences

### Positive

- **Single Source of Truth:** No synchronization bugs between hierarchy and intent graph
- **Simpler Tooling:** Validation only needs to check artifact files
- **Clearer Mental Model:** "The YAML files are the system"
- **Git-Native:** All changes are commits to artifact files

### Negative

- **Computed Views:** Intent graph visualizations require runtime computation
- **No Graph Queries:** Cannot use graph database query languages directly
- **Limited Expressiveness:** Some graph patterns (e.g., cross-cutting edges) require workarounds

### Mitigations

For complex graph queries:
1. Build artifacts into an in-memory graph at load time
2. Use NetworkX or similar library for analysis
3. Cache computed views for performance

---

## Implementation

### Artifact Structure (Unchanged)

```yaml
# Every non-mission artifact has exactly one parent
supports_upper_layer: "flow_reduce_false_positives_v1"

# Lineage hash references the same parent
lineage:
  upstream_hash: "sha256:..."  # Hash of flow_reduce_false_positives_v1
```

### Intent Graph Generation (New)

```python
def build_intent_graph(artifacts: list[dict]) -> nx.DiGraph:
    """Build intent graph from artifact hierarchy."""
    graph = nx.DiGraph()
    
    for artifact in artifacts:
        node_id = artifact["id"]
        graph.add_node(node_id, **artifact)
        
        if parent := artifact.get("supports_upper_layer"):
            graph.add_edge(parent, node_id)
    
    return graph
```

### Validation (Unchanged)

Validation operates on artifacts, not graphs:
- INV-003: Every non-mission artifact MUST reference exactly one upstream artifact
- INV-005: Every non-mission artifact's `lineage.upstream_hash` MUST match its parent's `lineage.hash`

---

## Alternatives Considered

### Alternative 1: Intent Graph as Primary

Store relationships in a graph database, generate YAML exports.

**Rejected because:**
- Adds infrastructure dependency
- Git versioning becomes complex
- Harder to audit changes

### Alternative 2: Dual Storage

Maintain both artifact files and separate graph store.

**Rejected because:**
- Synchronization bugs inevitable
- "Which is right?" ambiguity
- Doubles maintenance burden

### Alternative 3: Graph Embedded in Artifacts

Add explicit `children` arrays to artifacts alongside `supports_upper_layer`.

**Rejected because:**
- Violates single-source-of-truth (parent and child both store relationship)
- Update anomalies (add child but forget to update parent)
- Bidirectional contract already captured in optional `enables_lower_layer` field

---

## References

- `docs/domain-model.md` — Entity definitions and hierarchy diagram
- `docs/invariants.md` — INV-003, INV-005 (hierarchy invariants)
- `docs/intent-graphs.md` — Intent node concept documentation

---

## Revision History

| Date | Change |
|------|--------|
| 2026-01-06 | Initial decision recorded |
