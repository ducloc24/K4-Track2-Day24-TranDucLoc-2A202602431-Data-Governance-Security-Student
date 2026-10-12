from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class PolicyContext:
    data_classification: str
    request_purpose: str
    agent_owner: str
    delegation_depth: int
    egress_enabled: bool
    principal_id: str = ""
    requested_tool: str = ""
    agent_scopes: tuple[str, ...] = ()
    parent_scopes: tuple[str, ...] = ()
    expires_at: str = ""


def _principals() -> dict:
    path = Path(__file__).resolve().parent.parent / "data" / "principals.json"
    return json.loads(path.read_text(encoding="utf-8"))


def check(context: PolicyContext) -> tuple[bool, str]:
    if context.data_classification not in {"public", "internal", "restricted"}:
        return False, "unknown data classification"
    if context.data_classification == "restricted" and context.egress_enabled:
        return False, "restricted data cannot use egress"
    principals = _principals()
    principal = principals.get(context.principal_id)
    if principal is None:
        return False, "unknown principal"
    if context.request_purpose not in principal.get("purposes", []):
        return False, "principal is not authorized for this purpose"
    if not context.requested_tool:
        return False, "requested tool is missing"
    effective = set(principal.get("allowed_tools", [])) & set(context.agent_scopes)
    if context.delegation_depth > 0:
        effective &= set(context.parent_scopes)
    if context.requested_tool not in effective:
        return False, "requested tool is outside the effective scope"
    if not context.expires_at:
        return False, "authorization expiry is missing"
    try:
        expiry = datetime.fromisoformat(context.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry.astimezone(timezone.utc) <= datetime.now(timezone.utc):
            return False, "authorization has expired"
    except ValueError:
        return False, "authorization expiry is invalid"
    return True, "principal, purpose, scope and expiry are valid"
