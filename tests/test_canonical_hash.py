"""Golden-vector and conformance tests for lineage hashing.

Enforces docs/canonical-serialization.md (v1.0):
- Vector A: exact golden hash for a minimal mission artifact
- Vector B: NFC normalization (spec-conformance gap, expected failure)
- Vector C: prohibited-type rejection (spec-conformance gap, expected failure)
- Vector D: runtime-metadata (_-prefixed key) exclusion
- Live vectors: every example artifact's stored lineage.hash must verify
- Tamper detection: any content change must change the hash

The xfail tests document known gaps between the spec and
lint/compute_hash.py. They are strict: when the implementation becomes
conformant (Tier 1), the xfail markers must be removed or the suite fails.
"""

import pytest
import yaml

from compute_hash import compute_hash, get_existing_hash

from conftest import EXAMPLES_DIR

VECTOR_A_YAML = """
level: "mission"
id: "mission_test_v1"
title: "test"
intent: "smoke test for hashing"
success_criteria:
  - "hash is stable"
authorized_roles:
  - "vp_of_engineering"
cheddar_state: "active"
lineage:
  upstream_hash: null
  signed_by: "vp_of_engineering"
  timestamp: "2026-01-06T00:00:00Z"
"""

VECTOR_A_HASH = "sha256:061f485b8a895c8fd3e9049533db6c36ad6e4388c072e41b79d4e285a90ec283"

EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.yaml"))


def load_vector_a() -> dict:
    return yaml.safe_load(VECTOR_A_YAML)


def test_vector_a_golden_hash():
    """Spec Vector A: byte-exact golden hash."""
    assert compute_hash(load_vector_a()) == VECTOR_A_HASH


def test_vector_a_stable_across_key_order():
    """Key order in the source mapping must not affect the hash."""
    artifact = load_vector_a()
    reordered = dict(reversed(list(artifact.items())))
    assert compute_hash(reordered) == VECTOR_A_HASH


def test_vector_d_runtime_metadata_excluded():
    """Spec Vector D: _-prefixed keys are invisible to the hash."""
    artifact = load_vector_a()
    artifact["_source_path"] = "/tmp/somewhere.yaml"
    artifact["lineage"]["_loaded_at"] = "2026-06-10T00:00:00Z"
    assert compute_hash(artifact) == VECTOR_A_HASH


def test_lineage_hash_field_excluded():
    """The stored lineage.hash value must not affect the computed hash."""
    artifact = load_vector_a()
    artifact["lineage"]["hash"] = "sha256:" + "0" * 64
    assert compute_hash(artifact) == VECTOR_A_HASH


@pytest.mark.parametrize(
    "field, value",
    [
        ("intent", "a different intent"),
        ("title", "test2"),
        ("cheddar_state", "resolved"),
    ],
)
def test_tamper_changes_hash(field, value):
    """Any substantive content change must produce a different hash."""
    artifact = load_vector_a()
    artifact[field] = value
    assert compute_hash(artifact) != VECTOR_A_HASH


def test_signing_fields_are_hash_material():
    """Re-signing (signed_by/timestamp) changes the hash, per the
    Hash Exclusion Rule's stated consequence."""
    artifact = load_vector_a()
    artifact["lineage"]["signed_by"] = "someone_else"
    assert compute_hash(artifact) != VECTOR_A_HASH


@pytest.mark.parametrize(
    "example", EXAMPLE_FILES, ids=lambda p: p.name
)
def test_package_hash_matches_lint_hash(example):
    """Cross-implementation tripwire: if a package-level hashing module
    exists (src/cheddar/canonical.py, introduced by the artifact
    generator), it must produce byte-identical hashes to
    lint/compute_hash.py on every canonical example. Skips until the
    package module lands; fails loudly if the two implementations ever
    drift."""
    canonical = pytest.importorskip(
        "cheddar.canonical",
        reason="package hashing module not present on this branch",
    )
    with open(example, encoding="utf-8") as f:
        artifact = yaml.safe_load(f)
    assert canonical.compute_hash(artifact) == compute_hash(artifact)


@pytest.mark.parametrize(
    "example", EXAMPLE_FILES, ids=lambda p: p.name
)
def test_example_stored_hash_verifies(example):
    """Live vectors: stored lineage.hash in every canonical example must
    match recomputation. Guards against silent divergence between any
    future hashing implementation and the shipped hashes."""
    with open(example, encoding="utf-8") as f:
        artifact = yaml.safe_load(f)
    stored = get_existing_hash(artifact)
    if stored is None:
        # documentation_log carries no lineage block in the canonical
        # example; a lineage hash is optional for log artifacts.
        pytest.skip(f"{example.name} has no stored lineage.hash")
    assert compute_hash(artifact) == stored


# ---------------------------------------------------------------------------
# Spec-conformance gaps (docs/canonical-serialization.md, "Gaps" section).
# strict=True: these must start passing — and lose their markers — when the
# Tier 1 conformant implementation lands.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason="NFC normalization not yet implemented in lint/compute_hash.py "
    "(canonical-serialization.md gap; Tier 1)",
    strict=True,
)
def test_vector_b_nfc_value_normalization():
    """Spec Vector B: NFC-equivalent strings must hash identically."""
    precomposed = load_vector_a()
    precomposed["title"] = "caf\u00e9"  # e-acute as one code point (NFC)
    decomposed = load_vector_a()
    decomposed["title"] = "cafe\u0301"  # e + combining acute (NFD)
    assert compute_hash(precomposed) == compute_hash(decomposed)


@pytest.mark.xfail(
    reason="NFC normalization of mapping keys not yet implemented "
    "(canonical-serialization.md gap; Tier 1)",
    strict=True,
)
def test_nfc_key_normalization():
    precomposed = load_vector_a()
    precomposed["caf\u00e9"] = "x"
    decomposed = load_vector_a()
    decomposed["cafe\u0301"] = "x"
    assert compute_hash(precomposed) == compute_hash(decomposed)


@pytest.mark.xfail(
    reason="Prohibited-type rejection not yet implemented "
    "(canonical-serialization.md gap; Tier 1)",
    strict=True,
)
def test_vector_c_float_rejected():
    """Spec Vector C: floats must be refused, not silently hashed."""
    artifact = load_vector_a()
    artifact["canary_percentage"] = 0.05
    with pytest.raises(Exception):
        compute_hash(artifact)


def test_mixed_key_types_rejected():
    """Mixed string/int keys at one level are rejected today (the sorted
    serialization cannot compare them). This is incidental but acceptable
    rejection behavior under the Type Rules."""
    artifact = load_vector_a()
    artifact[42] = "x"
    with pytest.raises(Exception):
        compute_hash(artifact)


@pytest.mark.xfail(
    reason="Pure non-string-key mappings are silently coerced to strings "
    "(json.dumps {42: 'x'} -> {\"42\": \"x\"}) instead of rejected "
    "(canonical-serialization.md gap; Tier 1)",
    strict=True,
)
def test_int_key_mapping_rejected():
    artifact = load_vector_a()
    artifact["bad"] = {42: "x"}
    with pytest.raises(Exception):
        compute_hash(artifact)
