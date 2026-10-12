from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent import ledger, pii, policy, tools

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
DEFAULT_LEDGER_PATH = REPORTS_DIR / "ledger.jsonl"


class RunnerScaffoldPending(NotImplementedError):
    pass


def _hash_args(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def handle(message: str, llm, log_dir: Path | None = None, principal_id: str = "support_l1") -> str:
    principals = json.loads((Path(__file__).resolve().parent.parent / "data" / "principals.json").read_text(encoding="utf-8"))
    principal = principals.get(principal_id)
    scopes = tuple(principal.get("allowed_tools", [])) if principal else ()
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    agent_id = "lab24-agent"
    expires_at = "2099-01-01T00:00:00+00:00"
    ledger_path = Path(log_dir) / "ledger.jsonl" if log_dir else DEFAULT_LEDGER_PATH

    def call(tool_name: str, args, classification: str, purpose: str, egress: bool, fn):
        context = policy.PolicyContext(
            data_classification=classification,
            request_purpose=purpose,
            agent_owner=f"{agent_id}/{run_id}",
            delegation_depth=0,
            egress_enabled=egress,
            principal_id=principal_id,
            requested_tool=tool_name,
            agent_scopes=scopes,
            expires_at=expires_at,
        )
        allowed, reason = policy.check(context)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(), "agent_id": agent_id,
            "run_id": run_id, "tool": tool_name, "args_hash": _hash_args(args),
            "classification": classification, "decision": "allow" if allowed else "deny",
            "reason": reason, "on_behalf_of": principal_id, "expires_at": expires_at,
        }
        ledger.append(entry, ledger_path)
        return fn() if allowed else None

    docs = call("search_docs", {"query": message}, "internal", "summarize-tickets", False,
                lambda: tools.search_docs(message)) or []
    safe_docs = [{"id": doc["id"], "text": pii.redact(doc["text"])} for doc in docs]
    combined = "\n\n".join(doc["text"] for doc in safe_docs)
    llm.find_injection(combined)  # detection is telemetry only; IDs from free text are never used

    ticket_ids = []
    for doc in docs:
        match = re.search(r"ticket-(\d+)", doc["id"])
        if match:
            ticket_ids.append(int(match.group(1)))
    customers = json.loads(tools.CUSTOMERS_FILE.read_text(encoding="utf-8"))
    collected = []
    for ticket_id in sorted(set(ticket_ids)):
        for customer in customers:
            if ticket_id in customer.get("related_tickets", []):
                record = call("read_customer", {"ticket_id": ticket_id, "customer_id": customer["customer_id"]},
                              "restricted", "support-reply", False,
                              lambda cid=customer["customer_id"]: tools.read_customer(cid))
                if record:
                    collected.append(record)

    if collected:
        call("http_post", {"url": "http://127.0.0.1:10024/reconcile", "records": collected},
             "restricted", "support-reply", True,
             lambda: tools.http_post("http://127.0.0.1:10024/reconcile", {"records": collected}))
    return llm.summarize(safe_docs)
