#!/usr/bin/env python3
"""Advance scenario PRs through first review, second review, and final review."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


sys.path.insert(0, str(Path(__file__).resolve().parent))

from notify_review_escalation import GitHubClient, required_env  # noqa: E402
from review_gate import (  # noqa: E402
    CANONICAL_AGENT_KEYS,
    ParsedVerdict,
    evaluate_review_gate,
    parse_time,
    parse_verdict_with_reason,
)


CONFIG_PATH = ".github/scenario-reviewers.json"
SCENARIO_RE = re.compile(r"^runs/\d{4}-\d{2}-\d{2}/[^/]+/manifest\.yaml$")
ASSIGNMENT_RE = re.compile(
    r"<!--\s*scenario-review-assignment:([A-Za-z0-9-]+)"
    r"(?:\s+head:([0-9a-f]{7,40}))?\s*-->",
    re.IGNORECASE,
)
STAGE_RE = re.compile(
    r"<!--\s*scenario-review-stage:(first|second)\s*-->", re.IGNORECASE
)
CAPABILITY_RE = re.compile(
    r"<!--\s*scenario-review-capability:([a-z0-9][a-z0-9-]*)"
    r"\s+model-family:([a-z0-9][a-z0-9-]*)\s*-->",
    re.IGNORECASE,
)
VERDICT_HEADING_RE = re.compile(r"^## Review verdict:", re.MULTILINE)
REVIEWED_HEAD_RE = re.compile(
    r"^Reviewed at head:[ \t]*`?([0-9a-f]{7,40})`?[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
MAINTAINER_RE = re.compile(
    r"<!--\s*scenario-maintainer-request:([A-Za-z0-9-]+(?:,[A-Za-z0-9-]+)*)"
    r"\s+head:([0-9a-f]{7,40})\s*-->",
    re.IGNORECASE,
)
TRUSTED_ASSIGNERS = {"github-actions[bot]", "keting"}
PROTECTED_PROTOCOL_PREFIXES = (
    ".github/",
    "prompts/",
    "scripts/",
    "templates/",
    "tests/",
)
PROTECTED_PROTOCOL_FILES = {
    "CONTRIBUTING.md",
    "CONTRIBUTING.zh-CN.md",
    "docs/agent-review-and-scoring.md",
    "docs/agent-review-and-scoring.zh-CN.md",
    "docs/review-process.md",
    "docs/review-process.zh-CN.md",
    "LICENSE",
    "LICENSE-DATA",
    "SECURITY.md",
    "SECURITY.zh-CN.md",
}


@dataclass(frozen=True)
class Capability:
    login: str
    agent_product: str
    model_family: str


@dataclass(frozen=True)
class Assignment:
    reviewer: str
    stage: str
    head: str | None
    created_at: datetime
    comment_id: int
    agent_product: str | None = None
    model_family: str | None = None


@dataclass(frozen=True)
class MaintainerRequest:
    reviewers: tuple[str, ...]
    head: str
    created_at: datetime
    comment_id: int


class DryRunGitHubClient(GitHubClient):
    """Read live state while replacing every GitHub write with a log line."""

    def __init__(self, repository: str, token: str) -> None:
        super().__init__(repository, token)
        self.next_comment_id = 10_000_000

    def request(
        self, path: str, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> Any:
        if method == "GET":
            return super().request(path, method=method, payload=payload)
        if path.startswith("/statuses/"):
            print(f"DRY-RUN GitHub {method} {path} {json.dumps(payload, sort_keys=True)}")
        else:
            print(f"DRY-RUN GitHub {method} {path}")
        if method == "POST" and re.fullmatch(r"/issues/\d+/comments", path):
            self.next_comment_id += 1
            return {
                "id": self.next_comment_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "body": str((payload or {}).get("body") or ""),
                "user": {"login": "github-actions[bot]"},
            }
        return {}


def head_matches(current_head: str, recorded_head: str) -> bool:
    return current_head.lower().startswith(recorded_head.lower())


def assignment_records(comments: Iterable[dict[str, Any]]) -> list[Assignment]:
    assignments: list[Assignment] = []
    for comment in comments:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        if login not in TRUSTED_ASSIGNERS:
            continue
        body = str(comment.get("body") or "")
        stage_match = STAGE_RE.search(body)
        stage = stage_match.group(1).lower() if stage_match else "first"
        capability_match = CAPABILITY_RE.search(body)
        for match in ASSIGNMENT_RE.finditer(body):
            assignments.append(
                Assignment(
                    reviewer=match.group(1),
                    stage=stage,
                    head=match.group(2),
                    created_at=parse_time(str(comment["created_at"])),
                    comment_id=int(comment.get("id") or 0),
                    agent_product=(
                        capability_match.group(1).lower()
                        if capability_match
                        else None
                    ),
                    model_family=(
                        capability_match.group(2).lower()
                        if capability_match
                        else None
                    ),
                )
            )
    return assignments


def latest_assignment(
    assignments: Iterable[Assignment], stage: str, current_head: str | None = None
) -> Assignment | None:
    matching = []
    for assignment in assignments:
        if assignment.stage != stage:
            continue
        if current_head and assignment.head and not head_matches(current_head, assignment.head):
            continue
        matching.append(assignment)
    return max(
        matching,
        key=lambda item: (item.created_at, item.comment_id),
        default=None,
    )


def assigned_verdict(
    records: Iterable[dict[str, Any]],
    assignment: Assignment,
    current_head: str | None,
    before: datetime | None = None,
) -> tuple[ParsedVerdict | None, str | None]:
    attempts: list[tuple[datetime, int, dict[str, Any]]] = []
    for record in records:
        login = str((record.get("user") or {}).get("login") or "").lower()
        body = str(record.get("body") or "")
        submitted = record.get("submitted_at") or record.get("created_at")
        if login != assignment.reviewer.lower() or not submitted:
            continue
        submitted_at = parse_time(str(submitted))
        # Only a line that starts the verdict heading is a verdict attempt. An
        # ordinary reply that merely mentions `## Review verdict:` inline, or
        # quotes it with a `>` prefix, must not supersede a published verdict.
        if (
            submitted_at < assignment.created_at
            or (before is not None and submitted_at >= before)
            or not VERDICT_HEADING_RE.search(body)
        ):
            continue
        attempts.append((submitted_at, int(record.get("id") or 0), record))
    if not attempts:
        return None, None
    latest = max(attempts, key=lambda item: (item[0], item[1]))[2]
    expected_head = current_head
    if expected_head is None:
        match = REVIEWED_HEAD_RE.search(str(latest.get("body") or ""))
        if not match:
            return None, "missing Reviewed at head"
        expected_head = match.group(1)
    return parse_verdict_with_reason(
        latest,
        expected_head,
        trusted_commenters=(assignment.reviewer,),
    )


def previous_stage_verdict(
    records: Iterable[dict[str, Any]],
    assignments: Iterable[Assignment],
    stage: str,
    current_head: str,
) -> tuple[Assignment | None, ParsedVerdict | None]:
    ordered = sorted(
        (assignment for assignment in assignments if assignment.stage == stage),
        key=lambda item: (item.created_at, item.comment_id),
    )
    for index in range(len(ordered) - 1, -1, -1):
        assignment = ordered[index]
        if assignment.head and head_matches(current_head, assignment.head):
            continue
        before = ordered[index + 1].created_at if index + 1 < len(ordered) else None
        verdict, reason = assigned_verdict(
            records,
            assignment,
            assignment.head,
            before=before,
        )
        if reason:
            return None, None
        if verdict:
            return assignment, verdict
    return None, None


def scenario_package_roots(files: Iterable[dict[str, Any]]) -> tuple[str, ...]:
    roots = set()
    for item in files:
        for name in ("filename", "previous_filename"):
            parts = str(item.get(name) or "").split("/")
            if len(parts) >= 4 and parts[0] == "runs":
                roots.add("/".join(parts[:3]))
    return tuple(sorted(roots))


def scenario_tree_shas(
    client: GitHubClient,
    head: str,
    roots: Iterable[str],
    cache: dict[str, dict[str, str]],
) -> dict[str, str]:
    if head not in cache:
        response = client.request(f"/git/trees/{head}?recursive=1")
        if not isinstance(response, dict) or response.get("truncated"):
            raise RuntimeError(f"Could not prove scenario content at {head[:12]} is complete")
        cache[head] = {
            str(item.get("path") or ""): str(item.get("sha") or "")
            for item in response.get("tree", [])
            if item.get("type") == "tree"
        }
    return {root: cache[head].get(root, "") for root in roots}


def scenario_content_unchanged(
    client: GitHubClient,
    files: Iterable[dict[str, Any]],
    reviewed_head: str,
    current_head: str,
    cache: dict[str, dict[str, str]],
) -> bool:
    roots = scenario_package_roots(files)
    if not roots or len(reviewed_head) != 40 or len(current_head) != 40:
        return False
    reviewed = scenario_tree_shas(client, reviewed_head, roots, cache)
    current = scenario_tree_shas(client, current_head, roots, cache)
    return all(reviewed[root] and reviewed[root] == current[root] for root in roots)


def carried_marker(
    reviewer: str,
    stage: str,
    reviewed_head: str,
    current_head: str,
    verdict_id: int,
) -> str:
    return (
        f"<!-- scenario-review-carried:{reviewer.lower()} stage:{stage} "
        f"reviewed-head:{reviewed_head.lower()} head:{current_head.lower()} "
        f"verdict:{verdict_id} -->"
    )


def ensure_carried_assignment(
    client: GitHubClient,
    pull: dict[str, Any],
    comments: list[dict[str, Any]],
    assignment: Assignment,
    verdict: ParsedVerdict,
    capability: Capability,
) -> Assignment:
    current_head = str(pull["head"]["sha"])
    reviewed_head = verdict.reviewed_head
    marker = carried_marker(
        assignment.reviewer,
        assignment.stage,
        reviewed_head,
        current_head,
        verdict.record_id,
    )
    for comment in comments:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        if login in TRUSTED_ASSIGNERS and marker in str(comment.get("body") or ""):
            existing = latest_assignment(
                assignment_records([comment]), assignment.stage, current_head
            )
            if existing:
                return existing

    number = int(pull["number"])
    refreshed = client.comments(number)
    for comment in refreshed:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        if login in TRUSTED_ASSIGNERS and marker in str(comment.get("body") or ""):
            existing = latest_assignment(
                assignment_records([comment]), assignment.stage, current_head
            )
            if existing:
                return existing

    body = "\n".join(
        [
            f"<!-- scenario-review-assignment:{assignment.reviewer.lower()} head:{current_head.lower()} -->",
            f"<!-- scenario-review-stage:{assignment.stage} -->",
            f"<!-- scenario-review-capability:{capability.agent_product} model-family:{capability.model_family} -->",
            marker,
            "## Review carried forward / 评审已沿用",
            "",
            f"The APPROVE from `{assignment.reviewer}` at `{reviewed_head[:12]}` remains valid because the submitted scenario package content is unchanged at `{current_head[:12]}`.",
            "No reviewer action is required. Changes inside the scenario package will still require re-review.",
        ]
    )
    comment = client.add_comment(number, body)
    return Assignment(
        reviewer=assignment.reviewer,
        stage=assignment.stage,
        head=current_head,
        created_at=parse_time(str(comment["created_at"])),
        comment_id=int(comment["id"]),
        agent_product=capability.agent_product,
        model_family=capability.model_family,
    )


def maintainer_assignment(
    comments: Iterable[dict[str, Any]], current_head: str
) -> MaintainerRequest | None:
    matches: list[MaintainerRequest] = []
    for comment in comments:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        if login not in TRUSTED_ASSIGNERS:
            continue
        body = str(comment.get("body") or "")
        for match in MAINTAINER_RE.finditer(body):
            if head_matches(current_head, match.group(2)):
                matches.append(
                    MaintainerRequest(
                        reviewers=tuple(match.group(1).split(",")),
                        head=match.group(2),
                        created_at=parse_time(str(comment["created_at"])),
                        comment_id=int(comment.get("id") or 0),
                    )
                )
    return max(
        matches,
        key=lambda item: (item.created_at, item.comment_id),
        default=None,
    )


def has_formal_approval(
    reviews: Iterable[dict[str, Any]], request: MaintainerRequest, current_head: str
) -> str | None:
    requested = {login.lower() for login in request.reviewers}
    eligible: list[tuple[datetime, int, str]] = []
    for review in reviews:
        login = str((review.get("user") or {}).get("login") or "").lower()
        submitted = review.get("submitted_at")
        commit_id = str(review.get("commit_id") or "")
        if login not in requested or review.get("state") != "APPROVED":
            continue
        if not submitted or parse_time(str(submitted)) < request.created_at:
            continue
        if not commit_id or not head_matches(current_head, commit_id):
            continue
        eligible.append(
            (parse_time(str(submitted)), int(review.get("id") or 0), login)
        )
    return min(eligible)[-1] if eligible else None


def normalized_config(value: dict[str, Any]) -> dict[str, Any]:
    required_lists = (
        "reviewers",
        "second_reviewers",
        "glm_first_fallback_reviewers",
        "maintainers",
    )
    for name in required_lists:
        if not isinstance(value.get(name), list) or not value[name]:
            raise RuntimeError(f"{CONFIG_PATH} must contain a non-empty {name} list")
        value[name] = list(dict.fromkeys(str(item).strip() for item in value[name] if str(item).strip()))
    capabilities = value.get("reviewer_capabilities")
    if not isinstance(capabilities, dict):
        raise RuntimeError(f"{CONFIG_PATH} must contain reviewer_capabilities")
    canonical_families = {
        key.removeprefix("agent:")
        for key in CANONICAL_AGENT_KEYS
        if key != "agent:not-exposed"
    }
    normalized_capabilities: dict[str, list[dict[str, str]]] = {}
    for login, entries in capabilities.items():
        if not isinstance(entries, list) or not entries:
            raise RuntimeError(f"reviewer_capabilities for {login} must be a non-empty list")
        normalized_entries = []
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise RuntimeError(f"reviewer capability for {login} must be an object")
            agent_product = str(entry.get("agent_product") or "").lower()
            model_family = str(entry.get("model_family") or "").lower()
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", agent_product):
                raise RuntimeError(f"invalid agent_product for {login}: {agent_product}")
            if model_family not in canonical_families:
                raise RuntimeError(f"invalid model_family for {login}: {model_family}")
            pair = (agent_product, model_family)
            if pair not in seen:
                normalized_entries.append(
                    {"agent_product": agent_product, "model_family": model_family}
                )
                seen.add(pair)
        normalized_capabilities[str(login).lower()] = normalized_entries
    value["reviewer_capabilities"] = normalized_capabilities
    configured = {
        login.lower()
        for name in required_lists
        for login in value[name]
    }
    missing = configured - set(value["reviewer_capabilities"])
    if missing:
        raise RuntimeError(f"reviewer_capabilities missing: {sorted(missing)}")
    return value


def capabilities_for(config: dict[str, Any], login: str) -> list[Capability]:
    return [
        Capability(
            login=login,
            agent_product=entry["agent_product"],
            model_family=entry["model_family"],
        )
        for entry in config["reviewer_capabilities"].get(login.lower(), [])
    ]


def assignment_supported(
    config: dict[str, Any],
    assignment: Assignment,
    candidates: Iterable[Capability],
) -> bool:
    allowed_families = allowed_assignment_families(config, assignment)
    for capability in candidates:
        if capability.login.lower() != assignment.reviewer.lower():
            continue
        if assignment.agent_product and assignment.agent_product != capability.agent_product:
            continue
        if capability.model_family not in allowed_families:
            continue
        return True
    return False


def matching_capability(
    config: dict[str, Any],
    assignment: Assignment,
    candidates: Iterable[Capability],
) -> Capability | None:
    return next(
        (
            capability
            for capability in candidates
            if assignment_supported(config, assignment, [capability])
        ),
        None,
    )


def allowed_assignment_families(
    config: dict[str, Any], assignment: Assignment
) -> set[str]:
    if assignment.model_family:
        return {assignment.model_family}
    # Markers created before capability pinning used the reviewer's single
    # configured profile. Preserve that behavior by treating the first listed
    # capability as the legacy default rather than granting every new option.
    capabilities = capabilities_for(config, assignment.reviewer)
    return {capabilities[0].model_family} if capabilities else set()


def choose_candidates(
    config: dict[str, Any], first: ParsedVerdict, author: str
) -> list[Capability]:
    if first.model_family == "zhipu-glm":
        pool = config["glm_first_fallback_reviewers"]
    else:
        pool = config["second_reviewers"]
    candidates = []
    for login in pool:
        lower = login.lower()
        if lower in {author.lower(), first.commenter.lower()}:
            continue
        compatible = [
            capability
            for capability in capabilities_for(config, login)
            if capability.model_family != first.model_family
        ]
        if compatible:
            candidates.append(compatible[0])
    return candidates


def rotated(values: list[Any], pull_number: int) -> list[Any]:
    if not values:
        return []
    start = (pull_number - 1) % len(values)
    return values[start:] + values[:start]


def pull_files(client: GitHubClient, number: int) -> list[dict[str, Any]]:
    return client.paginate(f"/pulls/{number}/files")


def is_scenario_pull(files: Iterable[dict[str, Any]]) -> bool:
    return any(
        item.get("status") == "added"
        and SCENARIO_RE.fullmatch(str(item.get("filename") or ""))
        for item in files
    )


def changes_protected_protocol(files: Iterable[dict[str, Any]]) -> bool:
    # Keep this list aligned with .github/CODEOWNERS. A scenario submission
    # that changes one of these paths must be split before normal review.
    for item in files:
        filename = str(item.get("filename") or "")
        if filename in PROTECTED_PROTOCOL_FILES or filename.startswith(
            PROTECTED_PROTOCOL_PREFIXES
        ):
            return True
    return False


def load_config() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / CONFIG_PATH
    return normalized_config(json.loads(path.read_text(encoding="utf-8")))


def requested_reviews(
    client: GitHubClient, number: int
) -> tuple[list[str], list[str]]:
    response = client.request(f"/pulls/{number}/requested_reviewers")
    users = [str(item["login"]) for item in response.get("users", [])]
    teams = [str(item["slug"]) for item in response.get("teams", [])]
    return users, teams


def sync_review_request(client: GitHubClient, number: int, reviewer: str) -> None:
    sync_review_requests(client, number, [reviewer])


def sync_review_requests(
    client: GitHubClient, number: int, reviewers: Iterable[str]
) -> None:
    desired = list(dict.fromkeys(reviewers))
    desired_lower = {login.lower() for login in desired}
    current, teams = requested_reviews(client, number)
    remove = [login for login in current if login.lower() not in desired_lower]
    if remove or teams:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="DELETE",
            payload={"reviewers": remove, "team_reviewers": teams},
        )
    current_lower = {login.lower() for login in current}
    add = [login for login in desired if login.lower() not in current_lower]
    if add:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="POST",
            payload={"reviewers": add},
        )


def remove_review_requests(
    client: GitHubClient, number: int, reviewers: Iterable[str]
) -> None:
    targets = {login.lower() for login in reviewers}
    current, _ = requested_reviews(client, number)
    remove = [login for login in current if login.lower() in targets]
    if remove:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="DELETE",
            payload={"reviewers": remove, "team_reviewers": []},
        )


def clear_review_requests(client: GitHubClient, number: int) -> None:
    current, teams = requested_reviews(client, number)
    if current or teams:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="DELETE",
            payload={"reviewers": current, "team_reviewers": teams},
        )


def post_status(
    client: GitHubClient,
    pull: dict[str, Any],
    state: str,
    description: str,
) -> None:
    description = description[:140]
    combined = client.request(f"/commits/{pull['head']['sha']}/status")
    for status in combined.get("statuses", []):
        if status.get("context") != "review-gate":
            continue
        if status.get("state") == state and status.get("description") == description:
            return
        break
    client.request(
        f"/statuses/{pull['head']['sha']}",
        method="POST",
        payload={
            "state": state,
            "context": "review-gate",
            "description": description,
            "target_url": pull["html_url"],
        },
    )


def assignment_body(
    pull: dict[str, Any],
    reviewer: str,
    stage: str,
    agent_product: str,
    required_family: str,
    re_review: bool,
) -> str:
    head = pull["head"]["sha"].lower()
    repository_url = pull["base"]["repo"]["html_url"]
    base_sha = pull["base"]["sha"]
    entry_url = f"{repository_url}/blob/{base_sha}/docs/agent-review-and-scoring.md"
    entry_zh_url = f"{repository_url}/blob/{base_sha}/docs/agent-review-and-scoring.zh-CN.md"
    process_url = f"{repository_url}/blob/{base_sha}/docs/review-process.md"
    process_zh_url = f"{repository_url}/blob/{base_sha}/docs/review-process.zh-CN.md"
    marker = "\n".join(
        [
            f"<!-- scenario-review-assignment:{reviewer.lower()} head:{head} -->",
            f"<!-- scenario-review-stage:{stage} -->",
            f"<!-- scenario-review-capability:{agent_product} model-family:{required_family} -->",
        ]
    )
    if re_review:
        return "\n".join(
            [
                marker,
                "## Scenario re-review requested / 场景复审邀请",
                "",
                f"@{reviewer}, the PR head changed to `{head[:12]}`. Please re-review this head.",
                f"Continue with `{agent_product}` and model family `{required_family}`.",
                "You may consult your own prior verdict and the author's response, but do not read findings from other reviewers before publishing.",
                "",
                "```text",
                f"Re-review {pull['html_url']} at head {head} and post a new verdict that supersedes your prior verdict.",
                "```",
            ]
        )
    family_text = (
        f" Use `{agent_product}` with model family `{required_family}` for this review. / 本轮请使用 `{agent_product}` 和模型家族 `{required_family}`。"
        if required_family
        else ""
    )
    return "\n".join(
        [
            marker,
            f"## Scenario {stage} review requested / 场景{('首评' if stage == 'first' else '二评')}邀请",
            "",
            f"@{reviewer}, you have been selected to independently review this scenario PR.{family_text}",
            "",
            f"Start from the [Agent review entry]({entry_url}) ([中文]({entry_zh_url})). The criteria and verdict template are in the [review process]({process_url}) ([中文]({process_zh_url})).",
            "",
            "```text",
            f"Review and post a verdict for {pull['html_url']} using the repository's Agent review entry point.",
            "```",
            "",
            "Do not open the PR conversation or read another reviewer's findings before publishing your independent verdict.",
        ]
    )


def request_from_candidates(
    client: GitHubClient,
    pull: dict[str, Any],
    config: dict[str, Any],
    candidates: list[Capability],
    stage: str,
    previous: Assignment | None,
) -> tuple[Assignment, dict[str, Any]]:
    number = int(pull["number"])
    ordered = rotated(candidates, number) if stage == "first" else candidates
    if not ordered:
        raise RuntimeError(f"No {stage} reviewer is available")
    capability = ordered[0]
    reviewer = capability.login
    existing = latest_assignment(
        assignment_records(client.comments(number)), stage, pull["head"]["sha"]
    )
    if existing and assignment_supported(config, existing, candidates):
        return existing, {}
    # Do not fall through to another person after an ambiguous API failure:
    # the first request may have succeeded even if its response was lost.
    try:
        sync_review_request(client, number, reviewer)
    except Exception as error:
        raise RuntimeError(f"Could not request @{reviewer}: {error}") from error
    body = assignment_body(
        pull,
        reviewer,
        stage,
        capability.agent_product,
        capability.model_family,
        re_review=previous is not None and previous.reviewer.lower() == reviewer.lower(),
    )
    try:
        comment = client.add_comment(number, body)
    except Exception as error:
        raise RuntimeError(
            f"@{reviewer} may be requested but its assignment comment failed: {error}"
        ) from error
    return (
        Assignment(
            reviewer=reviewer,
            stage=stage,
            head=pull["head"]["sha"],
            created_at=parse_time(str(comment["created_at"])),
            comment_id=int(comment["id"]),
            agent_product=capability.agent_product,
            model_family=capability.model_family,
        ),
        comment,
    )


def request_first(
    client: GitHubClient,
    pull: dict[str, Any],
    config: dict[str, Any],
    assignments: list[Assignment],
) -> Assignment:
    author = pull["user"]["login"].lower()
    candidates = [
        capabilities_for(config, login)[0]
        for login in config["reviewers"]
        if login.lower() not in {author, "keting"}
    ]
    previous = latest_assignment(assignments, "first")
    if previous:
        previous_match = [
            item
            for item in candidates
            if item.login.lower() == previous.reviewer.lower()
            and assignment_supported(config, previous, [item])
        ]
        if previous_match:
            candidates = previous_match
    assignment, _ = request_from_candidates(
        client, pull, config, candidates, "first", previous
    )
    return assignment


def request_second(
    client: GitHubClient,
    pull: dict[str, Any],
    config: dict[str, Any],
    first_verdict: ParsedVerdict,
    assignments: list[Assignment],
) -> Assignment:
    candidates = choose_candidates(
        config, first_verdict, pull["user"]["login"]
    )
    if not candidates:
        raise RuntimeError(
            f"No second reviewer has a model family different from {first_verdict.model_family}"
        )
    previous = latest_assignment(assignments, "second")
    if previous:
        previous_match = [
            item
            for item in candidates
            if item.login.lower() == previous.reviewer.lower()
            and assignment_supported(config, previous, [item])
        ]
        if previous_match:
            candidates = previous_match
    assignment, _ = request_from_candidates(
        client, pull, config, candidates, "second", previous
    )
    return assignment


def maintainer_approved(
    config: dict[str, Any],
    reviews: Iterable[dict[str, Any]],
    author: str,
    head: str,
) -> bool:
    """Has a non-author maintainer formally approved exactly this head?

    Shared by the pull-request status and the merge-group check so both sides of
    `review-gate` answer the same question. The repository ruleset only requires
    one approving review from anyone with access, so this is the rule that makes
    the approval a *maintainer* decision.
    """
    maintainers = {login.lower() for login in config["maintainers"]}
    for review in reviews:
        login = str((review.get("user") or {}).get("login") or "").lower()
        commit = str(review.get("commit_id") or "").lower()
        if review.get("state") != "APPROVED":
            continue
        if login not in maintainers or login == author.lower():
            continue
        if commit and head.lower().startswith(commit):
            return True
    return False


def ensure_maintainers(
    client: GitHubClient,
    pull: dict[str, Any],
    config: dict[str, Any],
    comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> None:
    current = maintainer_assignment(comments, pull["head"]["sha"])
    author = pull["user"]["login"].lower()
    desired = [
        login
        for login in config["maintainers"]
        if login.lower() != author
    ]
    desired_lower = {login.lower() for login in desired}
    if not desired:
        raise RuntimeError(
            "No maintainer is available after excluding the PR author"
        )
    if current:
        approved = has_formal_approval(reviews, current, pull["head"]["sha"])
        if approved:
            remove_review_requests(
                client,
                int(pull["number"]),
                [login for login in current.reviewers if login.lower() != approved],
            )
            return
    if current and {login.lower() for login in current.reviewers} == desired_lower:
        sync_review_requests(client, int(pull["number"]), desired)
        return
    number = int(pull["number"])
    current = maintainer_assignment(client.comments(number), pull["head"]["sha"])
    if current:
        approved = has_formal_approval(reviews, current, pull["head"]["sha"])
        if approved:
            remove_review_requests(
                client,
                number,
                [login for login in current.reviewers if login.lower() != approved],
            )
            return
    if current and {login.lower() for login in current.reviewers} == desired_lower:
        sync_review_requests(client, number, desired)
        return
    try:
        sync_review_requests(client, number, desired)
    except Exception as error:
        logins = ", ".join(f"@{login}" for login in desired)
        raise RuntimeError(f"Could not request maintainers {logins}: {error}") from error
    marker = (
        f"<!-- scenario-maintainer-request:{','.join(login.lower() for login in desired)} "
        f"head:{pull['head']['sha'].lower()} -->"
    )
    mentions = " ".join(f"@{login}" for login in desired)
    try:
        client.add_comment(
            number,
            "\n".join(
                [
                    marker,
                    "## Maintainer final review requested / 维护者终审邀请",
                    "",
                    f"{mentions}, `review-gate` has recorded two independent APPROVE verdicts covering the current scenario content.",
                    "The first eligible Maintainer to finish may use GitHub's formal Approve action. After one approval, the other Review Request is no longer needed and will be removed automatically.",
                    "Do not approve your own PR.",
                ]
            ),
        )
    except Exception as error:
        raise RuntimeError(
            f"Maintainers may be requested but the maintainer comment failed: {error}"
        ) from error


def process_pull(client: GitHubClient, pull: dict[str, Any]) -> str | None:
    number = int(pull["number"])
    if pull.get("state") != "open" or pull.get("base", {}).get("ref") != "main":
        return None
    if pull.get("draft", False):
        post_status(client, pull, "pending", "Draft PRs are not eligible for review")
        return None
    files = pull_files(client, number)
    if not is_scenario_pull(files):
        post_status(client, pull, "success", "Not a new scenario PR; review-gate does not apply")
        return None
    if changes_protected_protocol(files):
        post_status(client, pull, "failure", "Split scenario data and protected protocol changes into separate PRs")
        return None

    config = load_config()
    comments = client.comments(number)
    reviews = client.reviews(number)
    records = comments + reviews
    assignments = assignment_records(comments)
    current_head = pull["head"]["sha"]
    tree_cache: dict[str, dict[str, str]] = {}
    carried_verdicts: list[ParsedVerdict] = []
    first = latest_assignment(assignments, "first", current_head)
    first_candidates = [
        capabilities_for(config, login)[0]
        for login in config["reviewers"]
        if login.lower() not in {pull["user"]["login"].lower(), "keting"}
    ]
    if first and not assignment_supported(config, first, first_candidates):
        first = request_first(client, pull, config, assignments)
        post_status(client, pull, "pending", f"Reassigned first review to @{first.reviewer}")
        return None

    first_verdict: ParsedVerdict | None = None
    first_reason: str | None = None
    if first:
        first_verdict, first_reason = assigned_verdict(records, first, current_head)
    if first_verdict is None and (first_reason is None or (first and first.head is None)):
        prior_assignment, prior_verdict = previous_stage_verdict(
            records, assignments, "first", current_head
        )
        if prior_verdict and prior_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
            clear_review_requests(client, number)
            post_status(
                client,
                pull,
                "failure",
                "Privacy concern from an earlier head remains unresolved",
            )
            return None
        if prior_assignment and prior_verdict and prior_verdict.verdict == "APPROVE":
            target = first or prior_assignment
            capability = matching_capability(config, target, first_candidates)
            same_reviewer = (
                first is None
                or first.reviewer.lower() == prior_assignment.reviewer.lower()
            )
            allowed = allowed_assignment_families(config, target) | {"human"}
            if (
                same_reviewer
                and capability
                and prior_verdict.model_family in allowed
                and scenario_content_unchanged(
                    client,
                    files,
                    prior_verdict.reviewed_head,
                    current_head,
                    tree_cache,
                )
            ):
                first = ensure_carried_assignment(
                    client,
                    pull,
                    comments,
                    prior_assignment,
                    prior_verdict,
                    capability,
                )
                first_verdict = prior_verdict
                carried_verdicts.append(prior_verdict)

    if first is None:
        first = request_first(client, pull, config, assignments)
        post_status(client, pull, "pending", f"Waiting for first verdict from @{first.reviewer}")
        return None

    if first_verdict is None:
        sync_review_request(client, number, first.reviewer)
        description = (
            f"First verdict rejected: {first_reason}"
            if first_reason
            else f"Waiting for first verdict from @{first.reviewer}"
        )
        post_status(client, pull, "pending", description)
        return None
    if first_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
        clear_review_requests(client, number)
        post_status(client, pull, "failure", "Privacy concern raised; review flow stopped")
        return None
    if first_verdict.verdict != "APPROVE":
        sync_review_request(client, number, first.reviewer)
        post_status(client, pull, "pending", f"Waiting for @{first.reviewer} to re-review changes")
        return None
    expected_first_families = allowed_assignment_families(config, first)
    if first_verdict.model_family not in expected_first_families | {"human"}:
        post_status(client, pull, "failure", "First verdict did not use its assigned model family")
        return None

    second = latest_assignment(assignments, "second", current_head)
    second_candidates = choose_candidates(
        config, first_verdict, pull["user"]["login"]
    )
    if second and not assignment_supported(config, second, second_candidates):
        second = request_second(client, pull, config, first_verdict, assignments)
        post_status(client, pull, "pending", f"Reassigned second review to @{second.reviewer}")
        return str(number) if second.reviewer.lower() == "keting" else None

    second_verdict: ParsedVerdict | None = None
    second_reason: str | None = None
    if second:
        second_verdict, second_reason = assigned_verdict(records, second, current_head)
    if second_verdict is None and (second_reason is None or (second and second.head is None)):
        prior_assignment, prior_verdict = previous_stage_verdict(
            records, assignments, "second", current_head
        )
        if prior_verdict and prior_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
            clear_review_requests(client, number)
            post_status(
                client,
                pull,
                "failure",
                "Privacy concern from an earlier head remains unresolved",
            )
            return None
        if prior_assignment and prior_verdict and prior_verdict.verdict == "APPROVE":
            target = second or prior_assignment
            capability = matching_capability(config, target, second_candidates)
            same_reviewer = (
                second is None
                or second.reviewer.lower() == prior_assignment.reviewer.lower()
            )
            allowed = allowed_assignment_families(config, target) | {"human"}
            if (
                same_reviewer
                and capability
                and prior_verdict.model_family in allowed
                and scenario_content_unchanged(
                    client,
                    files,
                    prior_verdict.reviewed_head,
                    current_head,
                    tree_cache,
                )
            ):
                second = ensure_carried_assignment(
                    client,
                    pull,
                    comments,
                    prior_assignment,
                    prior_verdict,
                    capability,
                )
                second_verdict = prior_verdict
                carried_verdicts.append(prior_verdict)

    if second is None:
        second = request_second(client, pull, config, first_verdict, assignments)
        post_status(client, pull, "pending", f"Waiting for second verdict from @{second.reviewer}")
        return str(number) if second.reviewer.lower() == "keting" else None

    if second_verdict is None:
        sync_review_request(client, number, second.reviewer)
        description = (
            f"Second verdict rejected: {second_reason}"
            if second_reason
            else f"Waiting for second verdict from @{second.reviewer}"
        )
        post_status(client, pull, "pending", description)
        return str(number) if second.reviewer.lower() == "keting" else None
    if second_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
        clear_review_requests(client, number)
        post_status(client, pull, "failure", "Privacy concern raised; review flow stopped")
        return None
    if second_verdict.verdict != "APPROVE":
        sync_review_request(client, number, second.reviewer)
        post_status(client, pull, "pending", f"Waiting for @{second.reviewer} to re-review changes")
        return None

    expected_second_families = allowed_assignment_families(config, second)
    if second_verdict.model_family not in expected_second_families | {"human"}:
        post_status(client, pull, "failure", "Second verdict did not use its assigned model family")
        return None

    gate = evaluate_review_gate(
        records,
        current_head,
        expected_reviewers=(first.reviewer, second.reviewer),
        carried_verdicts=carried_verdicts,
    )
    if not gate["eligible"]:
        post_status(client, pull, "failure", "Two different reviewers and model families are required")
        return None

    # Invite the maintainers first, then decide the status. `review-gate` only
    # succeeds once a non-author maintainer has formally approved this head, so
    # that the pull-request side and the merge-group side of the same check
    # agree: a merge queue evaluates `review-gate` again on the merge group, and
    # a check that passed here but fails there would eject the pull request from
    # the queue for a reason that was never visible on the pull request.
    ensure_maintainers(
        client,
        pull,
        config,
        comments,
        reviews,
    )
    if not maintainer_approved(config, reviews, pull["user"]["login"], current_head):
        post_status(
            client,
            pull,
            "pending",
            "Waiting for a maintainer to formally approve this head",
        )
        return None

    post_status(
        client,
        pull,
        "success",
        "Two independent APPROVE verdicts and a maintainer approval cover this head",
    )
    return None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull-request-number", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    client_class = DryRunGitHubClient if args.dry_run else GitHubClient
    client = client_class(required_env("REPOSITORY"), required_env("GITHUB_TOKEN"))
    if args.pull_request_number:
        pulls = [client.pull(args.pull_request_number)]
    else:
        pulls = client.open_pulls()

    notify_prs = []
    failures = []
    for pull in pulls:
        number = int(pull["number"])
        try:
            notify_pr = process_pull(client, pull)
            if notify_pr:
                notify_prs.append(notify_pr)
        except Exception as error:
            detail = str(error).replace("\r", " ").replace("\n", " ")
            print(f"::error title=Scenario review flow failed for PR #{number}::{detail}")
            try:
                if pull.get("state") == "open" and pull.get("base", {}).get("ref") == "main":
                    post_status(
                        client,
                        pull,
                        "error",
                        f"Review automation failed: {detail}",
                    )
            except Exception as status_error:
                print(f"::error title=Could not report review-gate error::{status_error}")
            failures.append(number)

    write_output("notify_prs", ",".join(notify_prs))
    print(f"scenario review flow processed: {len(pulls)}, failures: {len(failures)}")
    if failures:
        raise RuntimeError(f"scenario review flow failed for PRs: {failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
