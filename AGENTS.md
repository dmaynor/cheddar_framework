# AGENTS.md — Guidance for Codegen & Agent Tools

This repository currently holds **documents and design notes for the Cheddar framework**. Code will be added later. Treat this repo as a **spec + thinking space first**, and a codebase second.

Cheddar is intended to be a **cryptographically-linked, self-describing YAML/JSON artifact system** that captures the chain from:
> board-level mission → initiatives → projects → tasks → evidence

Your job as an agent is to **clarify, formalize, and only then automate**.

---

## 1. Overall Intent

**Primary goal:**  
Help design and evolve Cheddar as a framework for:
- Defining missions, goals, projects, and tasks as structured artifacts.
- Maintaining cryptographic lineage between those artifacts.
- Attaching evidence, metrics, and automation hooks in a way that is auditable and portable across tools.

**Near-term reality:**  
- Most of this repo is **concept docs, sketches, and notes**.  
- Your first responsibility is **sense-making**, not dumping code.

---

## 2. Operating Principles for Agents

When working in this repo, follow these rules:

1. **Documentation-first.**  
   - Before writing code, **summarize, reorganize, or clarify** existing docs.  
   - Prefer adding/cleaning `.md` or `.mdx` files, or structured examples in `.yaml`/`.json`, over adding new modules.

2. **Model the domain explicitly.**  
   - Identify core Cheddar primitives (e.g., `Mission`, `Objective`, `Initiative`, `Project`, `Task`, `Evidence`, `Run`, `Trace`).  
   - Represent them first as **schema drafts** (YAML/JSON examples, proto-schemas, or pseudo-code) before implementation.

3. **Preserve intent.**  
   - Cheddar is about **alignment, traceability, and cryptographic lineage**.  
   - Any changes must **strengthen** these properties, not weaken them (e.g., don’t hide lineage, don’t mix concerns).

4. **No hidden magic.**  
   - Avoid “black box” abstractions. All transformations should be explainable in English and traceable in the artifacts.  
   - If a behavior can’t be described plainly, don’t implement it yet—write a design note instead.

5. **Be explicit when guessing.**  
   - If you must infer missing behavior, **mark it clearly** in docs as a hypothesis or open question.  
   - Use clear language like: `OPEN QUESTION:`, `ASSUMPTION:`, `HYPOTHESIS:`.

6. **Write to be read by humans first, agents second.**  
   - Anything you generate should be understandable by a human reading the repo with no prior context.

---

## 3. Current Repo Phase & Priorities

We are in **Phase 0–1: Concept → Stable Specification**.

Priorities, in this order:

1. **Clarify the Cheddar mental model**
   - Extract & consolidate key ideas from existing docs into a small set of “core” documents:
     - `docs/overview.md` — what Cheddar is and why it exists.
     - `docs/domain-model.md` — entities and relationships.
     - `docs/use-cases.md` — concrete workflows (board, exec, IC/engineer, AI agent).

2. **Define canonical artifact formats**
   - Propose 1–3 canonical artifact schemas, e.g.:
     - `cheddar_mission.yaml`
     - `cheddar_initiative.yaml`
     - `cheddar_task.yaml`
     - `cheddar_evidence.yaml`
   - Express these as **realistic examples**, and, if useful, a separate schema-ish description.

3. **Capture invariants**
   - Document non-negotiable rules such as:
     - Every artifact has a stable ID and a version.
     - Artifacts have explicit upstream/downstream references.
     - There is a defined place for cryptographic material (hashes, signatures, etc.).
   - Put these in `docs/invariants.md`.

4. **Only then: start thin, composable tooling**
   - Small, clear utilities to:
     - Validate artifact structure.  
     - Compute & verify checksums/hashes.  
     - Render lineage graphs or simple reports from a set of artifacts.

---

## 4. Languages, Style, and Coding Expectations

Code will eventually exist here. When you add code:

- **Default language:** Python 3.11+.
- **Style:** PEP 8, type-annotated, with full docstrings that explain:
  - What the function/module does.
  - Input/output types and formats.
  - Any assumptions or side effects.

- **Testing:**
  - Use `pytest`.
  - Prefer small, deterministic tests.
  - Where possible, drive tests with **example Cheddar artifacts** stored in a `fixtures/` directory.

- **YAML/JSON artifacts:**
  - Be strict and predictable:
    - Avoid clever magic keys.
    - Make fields explicit (no implicit “magic default” behavior).
  - Where you introduce fields, document them in `docs/domain-model.md` or an appropriate schema doc.

- **Interfaces:**
  - Prefer **pure functions and small CLIs** over complex frameworks at this stage.
  - Any CLIs should:
    - Accept input files/directories of artifacts.
    - Emit JSON/YAML or markdown reports, not opaque binary blobs.

---

## 5. Directory and File Conventions

Agents SHOULD steer towards the following structure (even if not all of it exists yet):

- `docs/`
  - `overview.md` — human-friendly intro to Cheddar.
  - `domain-model.md` — entities, relationships, key fields.
  - `use-cases.md` — example workflows.
  - `invariants.md` — core guarantees Cheddar aims to enforce.
  - `roadmap.md` — phased implementation ideas.

- `schemas/`
  - `cheddar_mission.example.yaml`
  - `cheddar_initiative.example.yaml`
  - `cheddar_task.example.yaml`
  - `cheddar_evidence.example.yaml`

- `examples/`
  - End-to-end small story: mission → tasks → evidence → report.

- `src/` (only when we’re ready for code)
  - `cheddar/` package with small, composable modules.
- `tests/`
  - Mirrors `src/cheddar/` structure with unit tests.

When modifying or creating files, **respect existing structure** and prefer extending it over inventing a conflicting pattern.

---

## 6. Agent Workflow Checklist

When invoked on this repo, follow this sequence:

1. **Scan & orient**
   - Read `README.md` and any key docs.  
   - Identify duplicated, outdated, or conflicting descriptions of Cheddar.

2. **Propose consolidation**
   - Suggest specific moves like:
     - “Merge X and Y into `docs/overview.md`.”
     - “Promote this section into its own `docs/invariants.md`.”
   - Implement low-risk reorganizations directly; leave notes for bigger moves.

3. **Extract and codify the domain model**
   - Enumerate entities and relationships explicitly.
   - Write or update `docs/domain-model.md` to reflect current understanding.

4. **Design artifact examples**
   - Add/clean up `schemas/*.example.yaml` showing realistic, end-to-end usage.
   - Ensure examples align with the domain model and invariants.

5. **Only then propose code**
   - If the domain model and examples are reasonably stable:
     - Propose minimal Python modules (validation, hashing, reporting).
     - Add tests and clearly explain behavior in docstrings and docs.

6. **Leave the repo better than you found it**
   - Each change set should:
     - Reduce ambiguity.
     - Improve consistency.
     - Move Cheddar closer to being implementable and testable.

---

## 7. Things Agents Should NOT Do (Yet)

- Do **not**:
  - Introduce heavy frameworks (Django, large ORMs, huge dependency trees).
  - Build complex web UIs in this repo at this stage.
  - Introduce vendor-specific integrations (Jira, GitHub, etc.) directly into the core model.
  - Invent opaque state machines without documenting the intent and transitions.

- If you feel the urge to:
  - Stop, write a **short design note in `docs/roadmap.md` or a dedicated proposal file**, and keep the implementation small and reversible.

---

## 8. Success Criteria

You are “doing it right” in this repo if:

- A new human can read `docs/overview.md` + `docs/domain-model.md` and understand:
  - What Cheddar is.
  - What artifacts look like.
  - How those artifacts relate to each other.

- The artifact examples are:
  - Valid YAML/JSON.
  - Internally consistent.
  - Usable as fixtures for testing future code.

- Any new code:
  - Is small, composable, and well-tested.
  - Operates *on* Cheddar artifacts, rather than redefining them.
  - Makes it easier to trust and adopt Cheddar, not harder.

---