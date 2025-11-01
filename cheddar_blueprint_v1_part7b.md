# Cheddar Blueprint v1 — Part 7b: Embodiment Tenet (with Embodied QA exemplar)

**Status:** Draft • **Owner:** Architect / Strategist • **Version:** 1.0  
**Related:** Part 7 (Governance & Ethics), Part 7a (Operationalization), Part 6 (MCPOS Prototype)

## 1. Executive Summary
**Embodiment** asserts that Cheddar systems do not merely observe; they **participate** in their environments. Intelligence emerges through a continuous **sensorimotor loop**: sensing, acting, receiving feedback, and adapting.  
**Embodied QA** is the primary exemplar: test intelligence that lives inside the runtime, collecting telemetry while acting, and converting interaction traces into multi-test verification and adaptive coverage.

## 2. Tenet: Embodiment
**Principle.** Cheddar agents should be designed to:
1) **Sense**—ingest runtime telemetry (logs, traces, metrics, events, state snapshots).  
2) **Act**—execute bounded interventions (user-like flows, API calls, chaos pulses).  
3) **Adapt**—update plans, hypotheses, and verifications based on live feedback.

**Why.** Disembodied systems ossify because their test orops are episodic. Embodiment increases **robustness**, **reuse** (one run satisfies many checks), and **drift resistance** (agents adapt to change).

## 3. Definitions
- **Sensorimotor Loop:** A closed loop where actions are selected using live telemetry and outcomes recondition future actions.  
- **Embodied QA:** Quality assurance that verifies *through* participation: the agent acts in the SUT and treats every signal as potential evidence across many test objectives.

## 4. Design Principles
- **P1 — Continuous Context:** Preserve agent memory across runs (state cache + evidence graph).  
- **P2 — Emergent Verification:** Prefer evidence reuse. A single action can satisfy many assertions.  
- **P3 — Observability-Native:** Treat logs/metrics/traces as first-class artifacts, versioned and linked.  
- **P4 — Bounded Autonomy:** Guardrails on action classes, rate, scope, and blast radius.  
- **P5 — Explainability Hooks:** Every adaptive pivot records *why* (signal → decision → effect).  
- **P6 — Governance Interlock:** All adaptation is policy-checked against Part 7 doctrines.

## 5. Operational Patterns
- **Pattern A: One-Run/Many-Checks (OR/MAC).** Execute end-to-end user journeys; multiplex assertions over captured telemetry (functional, performance, security, UX coherence).  
- **Pattern B: Opportunistic Branching.** When a signal crosses a threshold (e.g., error bursts, new feature flag), spawn a side probe within limits; record linkage both ways.  
- **Pattern C: Self-Healing Selectors/Contracts.** When UI/API contracts shift, learn replacement selectors or schema mappings from live diffs; require dual confirmation (telemetry corroboration + stable replay).

## 6. Embodied QA — Reference Implementation (Framework-Agnostic)
**Interfaces**
- **Sensors:** `LogStream`, `TraceStream (OTel)`, `Metrics (PromQL)`, `NetTap`, `UI DOM/AX`, `SysProbes`.  
- **Actuators:** `UIAction`, `APIAction`, `CLIRun`, `ChaosPulse`, `EnvPatch (ephemeral)`.  
- **Memory:** `EvidenceGraph` (DAG of {Action, Signal, Assertion} with provenance + time).  
- **Policy:** `GuardrailSet` (caps, scopes, forbidden ops), `Ethics/Compliance` (Part 7).  

**Core Loop (pseudo-spec):**
1. Plan next **Task** from backlog → compile to **ActionSet**.  
2. Execute **Action**(s) with trace IDs → stream sensors concurrently.  
3. Normalize signals → write **EvidenceGraph** nodes and edges.  
4. Run **AssertionPack** over the new evidence (functional/perf/sec).  
5. Evaluate **Heuristics**: if “interesting”, branch **Probe**; else proceed.  
6. Emit **ReportBundle** (JUnit/xUnit + Perf + Security) with cross-links.  
7. Update **Policy Scorecards** and **Agent Memory**.

**Minimal SLAs**
- Attach a **trace-id** to every action and propagate to all sensor spans.  
- Record **co-visibility**: which signals were present for which actions.  
- Ensure **deterministic replays** for any reported defect (snapshot inputs + environment deltas + action list).

## 7. Architecture Hooks (Cheddar Alignment)
- **MCPOS Integration (Part 6):** Embodied agents register as MCP tools with declared actuators/sensors. Health endpoints expose guardrail counters.  
- **Artifact Ontology:** Each EvidenceGraph node gets `intent_link` and `audit_link` for governance audits.  
- **Rollup:** All runs publish `run_manifest.json` (see §10) for cross-part indexing.

## 8. Metrics & KPIs
- **Evidence Yield / hr** (edges added to EvidenceGraph per wall-hour).  
- **Multi-Assertion Density** (avg assertions satisfied per action).  
- **Adaptation Precision** (fraction of adaptive branches that surface novel defects or coverage).  
- **Flake Attrition Half-Life** (time to stabilize top-N flaky checks).  
- **Repro Determinism Rate** (defects with single-click deterministic replay).

## 9. Governance & Safety (Part 7 Interlock)
- **Action Budgeting:** Per run, per env caps (count, scope, data mutation).  
- **Ethical Gates:** No PII exfil; no prod data mutation without explicit allow-list.  
- **SBOM & Supply Hooks:** If actuators deploy binaries, attach SBOM + signature; log to audit chain.

## 10. Run Manifest (Rollup Contract)
Every embodied run emits `/artifacts/run_manifest.json`:
```json
{
  "blueprint_part": "7b-embodiment",
  "run_id": "<uuid>",
  "time_utc": "<iso8601>",
  "sut_version": "<semver|git_sha>",
  "trace_root": "<trace-id>",
  "evidence_graph_uri": "artifact://evidence/<run_id>.graph.jsonl",
  "reports": {
    "junit": "artifact://reports/<run_id>/junit.xml",
    "perf": "artifact://reports/<run_id>/perf.json",
    "security": "artifact://reports/<run_id>/security.json"
  },
  "rollup_links": {
    "part7": "cheddar_blueprint_v1_part7.md",
    "part7a": "cheddar_blueprint_v1_part7a.md"
  }
}
```

## 11. Embodied QA – Worked Example (Concise)
- **Scenario:** “Login → Search → Export”  
- **ActionSet:** UI login, API `/search?q=...`, UI export click.  
- **Sensors:** OTel trace spans, nginx access logs, browser console, DB query metrics.  
- **Assertions multiplexed:**  
  `A1 Auth OK`, `A2 Token TTL sane`, `A3 P95 < 400ms`, `A4 Export file schema stable`,  
  `A5 No 5xx in span window`, `A6 DPI fingerprint unchanged`, `A7 Trace completeness > 0.98`.  
- **Adaptive Branch Trigger:** If `A3` breached and DB `rows_returned > θ`, spawn `Probe: paginate-search` with tighter filters; attach to same evidence graph.

## 12. Deliverables
- **Spec:** This document.  
- **Schema:** `evidence_graph.schema.json` (Part 1 ontology extension).  
- **Manifests:** `run_manifest.json` per run (see §10).  
- **Policies:** `guardrails.yaml` templates (env scoping).

## 13. Change Log
- v1.0 — Initial cut of Embodiment Tenet and Embodied QA exemplar.