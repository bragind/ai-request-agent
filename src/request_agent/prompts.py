from __future__ import annotations

SYSTEM_PROMPT = """You analyze Russian customer support requests.
Return only valid JSON. Do not use Markdown. Do not add text outside JSON.

Allowed request_type values:
technical_issue, billing, account_access, complaint, consultation, feature_request, other.

Allowed priority values:
low, medium, high, critical.

The response must use exactly this JSON shape:
{
  "request_type": "account_access",
  "summary": "One short Russian sentence.",
  "priority": "high",
  "needs_human": true,
  "confidence": 0.92
}

Rules:
- Do not invent categories or priorities.
- summary must be one short sentence in Russian.
- confidence must be a number from 0 to 1.
- Use critical only for safety threats, data leaks, total outage, hacking, fire,
  or critical failure.
"""


def build_user_prompt(text: str) -> str:
    return f"Analyze this support request and return JSON only:\n{text}"
