from __future__ import annotations

import hashlib
import json
from pathlib import Path


REQUIRED = {"ts", "agent_id", "run_id", "tool", "args_hash", "classification", "decision", "reason"}


def _digest(entry: dict) -> str:
    payload = {key: value for key, value in entry.items() if key != "hash"}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append(entry: dict, path: Path) -> dict:
    missing = REQUIRED - set(entry)
    if missing:
        raise ValueError(f"ledger entry missing fields: {sorted(missing)}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = "0" * 64
    if path.exists() and path.stat().st_size:
        last = path.read_text(encoding="utf-8").splitlines()[-1]
        previous = json.loads(last)["hash"]
    result = dict(entry)
    result["prev_hash"] = previous
    result["hash"] = _digest(result)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
    return result


def verify(path: Path) -> bool:
    path = Path(path)
    if not path.exists():
        return False
    previous = "0" * 64
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            if not entry.get("reason") or entry.get("prev_hash") != previous:
                return False
            if entry.get("hash") != _digest(entry):
                return False
            previous = entry["hash"]
    except (ValueError, KeyError, json.JSONDecodeError):
        return False
    return True
