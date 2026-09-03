#!/usr/bin/env python3
"""Parse structured review verdicts and evaluate two-review independence."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


TRUSTED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
VERDICTS = {
    "APPROVE",
    "REQUEST_CHANGES",
    "PRIVACY-CONCERN-RAISED-PRIVATELY",
}
HUMAN_KEY_RE = re.compile(r"^human:[a-z0-9-]+$")
CANONICAL_AGENT_KEYS = {
    "agent:openai-gpt",
    "agent:anthropic-claude",
    "agent:zhipu-glm",
    "agent:google-gemini",
    "agent:moonshot-kimi",
    "agent:not-exposed",
}


@dataclass(frozen=True)
class ParsedVerdict:
    record_id: int
    record_url: str
    commenter: str
    verdict: str
    reviewed_head: str
    reviewer: str
    independence_key: str
    model_family: str
    key_source: str
    submitted_at: datetime


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _field(body: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.+?)[ \t]*$", body, re.I | re.M)
    return match.group(1).strip() if match else None


def legacy_key(reviewer: str) -> str | None:
    """Conservatively classify comments written before Independence key."""
    value = reviewer.lower()
    # Product names such as "Claude Code" can host a GLM model. Prefer an
    # explicit model token over a product token when both appear.
    if "glm" in value or "zhipu" in value or "智谱" in value:
        return "agent:zhipu-glm"
    if "gemini" in value or "google" in value:
        return "agent:google-gemini"
    if "kimi" in value or "moonshot" in value:
        return "agent:moonshot-kimi"
    if "codex" in value or "openai" in value or re.search(r"\bgpt[- ]", value):
        return "agent:openai-gpt"
    if "claude" in value or "anthropic" in value:
        return "agent:anthropic-claude"
    return None


def model_family(independence_key: str) -> str:
    if independence_key.startswith("human:"):
        return "human"
    return independence_key.removeprefix("agent:")


def parse_verdict_with_reason(
    record: dict[str, Any], current_head: str
) -> tuple[ParsedVerdict | None, str | None]:
    if record.get("author_association") not in TRUSTED_ASSOCIATIONS:
        return None, "comment author is not a repository member or collaborator"

    body = str(record.get("body") or "").replace("\r\n", "\n")
    if not re.search(
        r"^Reviewed under: docs/review-process\.md @ `?[0-9a-f]{7,40}`?[ \t]*$",
        body,
        re.I | re.M,
    ):
        return None, "missing or invalid Reviewed under declaration"

    matches = re.findall(
        r"^## Review verdict: "
        r"(APPROVE|REQUEST_CHANGES|PRIVACY-CONCERN-RAISED-PRIVATELY)[ \t]*$",
        body,
        re.M,
    )
    if len(matches) != 1 or matches[0] not in VERDICTS:
        return None, "expected exactly one supported Review verdict heading"

    head_value = _field(body, "Reviewed at head")
    reviewer = _field(body, "Reviewer")
    if not head_value:
        return None, "missing Reviewed at head"
    if not reviewer:
        return None, "missing Reviewer"
    reviewed_head = head_value.strip("`").lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", reviewed_head):
        return None, "Reviewed at head is not a commit SHA"
    if not current_head.lower().startswith(reviewed_head):
        return None, "Reviewed at head does not match the current PR head"

    commenter = str((record.get("user") or {}).get("login") or "").lower()
    if not commenter:
        return None, "missing GitHub reviewer login"

    explicit_key = _field(body, "Independence key")
    if explicit_key:
        independence_key = explicit_key.lower()
        if not (
            HUMAN_KEY_RE.fullmatch(independence_key)
            or independence_key in CANONICAL_AGENT_KEYS
        ):
            return None, "Independence key is not a supported canonical family"
        if independence_key.startswith("human:"):
            if independence_key.removeprefix("human:") != commenter:
                return None, "human Independence key does not match the commenter"
        key_source = "explicit"
    else:
        independence_key = legacy_key(reviewer) or ""
        if not independence_key:
            return None, "missing Independence key and legacy family is ambiguous"
        key_source = "legacy-inference"

    submitted = record.get("submitted_at") or record.get("created_at")
    if not submitted:
        return None, "missing verdict timestamp"
    return (
        ParsedVerdict(
            record_id=int(record.get("id") or 0),
            record_url=str(record.get("html_url") or ""),
            commenter=commenter,
            verdict=matches[0],
            reviewed_head=reviewed_head,
            reviewer=reviewer,
            independence_key=independence_key,
            model_family=model_family(independence_key),
            key_source=key_source,
            submitted_at=parse_time(str(submitted)),
        ),
        None,
    )


def parse_verdict(record: dict[str, Any], current_head: str) -> ParsedVerdict | None:
    parsed, _ = parse_verdict_with_reason(record, current_head)
    return parsed


def current_verdicts(
    records: Iterable[dict[str, Any]], current_head: str
) -> dict[str, ParsedVerdict]:
    latest: dict[str, ParsedVerdict] = {}
    for record in records:
        parsed = parse_verdict(record, current_head)
        if not parsed:
            continue
        previous = latest.get(parsed.commenter)
        if previous is None or (parsed.submitted_at, parsed.record_id) > (
            previous.submitted_at,
            previous.record_id,
        ):
            latest[parsed.commenter] = parsed
    return latest


def evaluate_review_gate(
    records: Iterable[dict[str, Any]],
    current_head: str,
    expected_reviewers: Iterable[str] | None = None,
) -> dict[str, Any]:
    latest = current_verdicts(records, current_head)
    if expected_reviewers is not None:
        allowed = {login.lower() for login in expected_reviewers}
        latest = {login: verdict for login, verdict in latest.items() if login in allowed}

    values = sorted(latest.values(), key=lambda item: (item.submitted_at, item.record_id))
    approvals = [item for item in values if item.verdict == "APPROVE"]
    privacy = any(
        item.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY" for item in values
    )
    distinct_reviewers = {item.commenter for item in approvals}
    distinct_families = {item.model_family for item in approvals}
    eligible = (
        not privacy
        and len(approvals) >= 2
        and len(distinct_reviewers) >= 2
        and len(distinct_families) >= 2
        and "not-exposed" not in distinct_families
    )
    return {
        "eligible": eligible,
        "privacy": privacy,
        "approval_count": len(approvals),
        "approvals": [asdict(item) for item in approvals],
        "latest_verdicts": [asdict(item) for item in values],
    }
