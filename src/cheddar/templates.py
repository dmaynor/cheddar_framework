"""Artifact template builders for Cheddar generator v0."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cheddar.canonical import with_computed_hash


def utc_now() -> str:
    """Return a second-precision UTC timestamp accepted by the schemas."""
    return datetime.now(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def lineage(upstream_hash: str | None, signed_by: str, timestamp: str | None = None) -> dict[str, Any]:
    """Create a lineage block with an empty hash placeholder for computation."""
    return {
        "upstream_hash": upstream_hash,
        "hash": "sha256:" + "0" * 64,
        "signed_by": signed_by,
        "timestamp": timestamp or utc_now(),
    }


def new_mission(artifact_id: str, title: str, signed_by: str) -> dict[str, Any]:
    """Create a mission artifact."""
    artifact = {
        "level": "mission",
        "id": artifact_id,
        "title": title,
        "intent": f"Define mission intent for {title}.",
        "success_criteria": [
            {"metric": "defined_success", "target": "documented"},
        ],
        "authorized_roles": [
            {"role_name": signed_by},
        ],
        "cheddar_state": "active",
        "lineage": lineage(None, signed_by),
    }
    return with_computed_hash(artifact)


def new_flow(
    artifact_id: str,
    title: str,
    parent: str,
    upstream_hash: str,
    signed_by: str,
) -> dict[str, Any]:
    """Create a flow initiative artifact."""
    artifact = {
        "level": "flow_initiative",
        "id": artifact_id,
        "title": title,
        "supports_upper_layer": parent,
        "objective": f"Translate upstream mission intent into an executable objective for {title}.",
        "constraints": ["Keep scope explicit and testable."],
        "telemetry_signals": ["progress", "quality"],
        "cheddar_state": "active",
        "lineage": lineage(upstream_hash, signed_by),
    }
    return with_computed_hash(artifact)


def new_track(
    artifact_id: str,
    title: str,
    parent: str,
    upstream_hash: str,
    signed_by: str,
) -> dict[str, Any]:
    """Create a cheddar track artifact."""
    artifact = {
        "level": "cheddar_track",
        "id": artifact_id,
        "title": title,
        "supports_upper_layer": parent,
        "issue": f"Track the reproducible issue or improvement opportunity for {title}.",
        "hypotheses": ["Root cause is not yet proven."],
        "repro_steps": ["Document minimal reproduction steps."],
        "cheddar_state": "active",
        "lineage": lineage(upstream_hash, signed_by),
    }
    return with_computed_hash(artifact)


def new_brief(
    artifact_id: str,
    title: str,
    parent: str,
    upstream_hash: str,
    signed_by: str,
) -> dict[str, Any]:
    """Create an automation brief artifact."""
    artifact = {
        "level": "automation_brief",
        "id": artifact_id,
        "title": title,
        "supports_upper_layer": parent,
        "owner": signed_by,
        "deliverables": ["Produce the requested automation deliverable."],
        "tests": [
            {
                "name": "deliverable_exists",
                "type": "artifact_check",
                "target": "present",
            }
        ],
        "change_management": {
            "approvals_required": [{"role": signed_by}],
            "rollback_plan": "Revert to the previous known-good state.",
            "rollout": {"strategy": "none"},
        },
        "cheddar_state": "active",
        "lineage": lineage(upstream_hash, signed_by),
    }
    return with_computed_hash(artifact)


def new_personal(
    artifact_id: str,
    title: str,
    parent: str,
    upstream_hash: str,
    signed_by: str,
) -> dict[str, Any]:
    """Create a personal artifact."""
    artifact = {
        "level": "personal",
        "id": artifact_id,
        "title": title,
        "supports_upper_layer": parent,
        "responsible_party": signed_by,
        "acceptance_criteria": ["Acceptance criteria are documented and satisfied."],
        "cheddar_state": "active",
        "lineage": lineage(upstream_hash, signed_by),
        "notes": "Generated starter artifact. Replace placeholder content before use.",
    }
    return with_computed_hash(artifact)


BUILDERS = {
    "mission": new_mission,
    "flow": new_flow,
    "track": new_track,
    "brief": new_brief,
    "personal": new_personal,
}
