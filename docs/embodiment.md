# Embodiment Tenet

Embodiment asserts that Cheddar systems **participate** in their environments. Intelligence emerges from a continuous sensorimotor loop: sensing, acting, receiving feedback, and adapting.

## Principles
1. **Sense.** Ingest runtime telemetry (logs, traces, metrics, events, state snapshots).
2. **Act.** Execute bounded interventions (user-like flows, API calls, chaos pulses).
3. **Adapt.** Update plans, hypotheses, and verifications based on live feedback.

## Why It Matters
- **Robustness.** Reuse evidence from real interactions rather than episodic tests.
- **Drift Resistance.** Agents adapt to change via live feedback.
- **Reuse.** One run can satisfy multiple checks across functional, performance, and security goals.

## Design Principles
- **Continuous Context.** Preserve agent memory across runs (state cache + evidence graph).
- **Emergent Verification.** Prefer evidence reuse—single actions satisfy many assertions.
- **Observability-Native.** Treat logs/metrics/traces as versioned, linked artifacts.
- **Bounded Autonomy.** Guardrails on action class, rate, scope, and blast radius.
- **Explainability Hooks.** Every adaptive pivot records signal → decision → effect.
- **Governance Interlock.** All adaptation is policy-checked against governance rules.

## Embodied QA Pattern
**Sensorimotor loop for QA:**
- **Sensors:** `LogStream`, `TraceStream (OTel)`, `Metrics (PromQL)`, `NetTap`, `UI DOM/AX`, `SysProbes`.
- **Actuators:** `UIAction`, `APIAction`, `CLIRun`, `ChaosPulse`, `EnvPatch (ephemeral)`.
- **Memory:** `EvidenceGraph` linking {Action, Signal, Assertion} with provenance.
- **Policy:** `GuardrailSet` with caps, scopes, forbidden operations; governed by ethics rules.

By living inside the runtime, embodied QA converts interaction traces into multi-test verification and adaptive coverage.
