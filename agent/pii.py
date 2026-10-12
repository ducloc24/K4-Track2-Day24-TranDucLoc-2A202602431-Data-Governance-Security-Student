from __future__ import annotations

import re


_PATTERNS = (
    ("EMAIL", re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("VN_CCCD", re.compile(r"(?<!\d)\d{12}(?!\d)")),
    ("VN_PHONE", re.compile(r"(?<!\d)0\d{9}(?!\d)")),
    ("VN_BANK_ACCOUNT", re.compile(r"(?<!\d)\d{8,16}(?!\d)")),
)


def detect(text: str) -> list[dict]:
    candidates = []
    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            candidates.append({"type": kind, "start": match.start(), "end": match.end()})

    # Prefer more specific entities when malformed or adjacent values overlap.
    priority = {"EMAIL": 0, "VN_CCCD": 1, "VN_PHONE": 2, "VN_BANK_ACCOUNT": 3}
    for entity in candidates:
        if entity["type"] == "VN_BANK_ACCOUNT":
            prefix = text[max(0, entity["start"] - 20):entity["start"]].lower()
            if "stk" in prefix or "tai khoan" in prefix or "tài khoản" in prefix:
                priority["VN_BANK_ACCOUNT"] = 0
    chosen = []
    for entity in sorted(candidates, key=lambda e: (e["start"], priority[e["type"]], -(e["end"] - e["start"]))):
        if any(entity["start"] < old["end"] and old["start"] < entity["end"] for old in chosen):
            continue
        chosen.append(entity)
    return sorted(chosen, key=lambda e: e["start"])


def redact(text: str) -> str:
    result = text
    for entity in reversed(detect(text)):
        replacement = f"[REDACTED_{entity['type']}]"
        result = result[:entity["start"]] + replacement + result[entity["end"]:]
    return result
