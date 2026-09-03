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
    ParsedVerdict,
    current_verdicts,
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
MAINTAINER_RE = re.compile(
    r"<!--\s*scenario-maintainer-request:([A-Za-z0-9-]+)"
    r"\s+head:([0-9a-f]{7,40})\s*-->",
    re.IGNORECASE,
)
TRUSTED_ASSIGNERS = {"github-actions[bot]", "keting"}


@dataclass(frozen=True)
class Assignment:
    reviewer: str
    stage: str
    head: str | None
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
        for match in ASSIGNMENT_RE.finditer(body):
            assignments.append(
                Assignment(
                    reviewer=match.group(1),
                    stage=stage,
                    head=match.group(2),
                    created_at=parse_time(str(comment["created_at"])),
                    comment_id=int(comment.get("id") or 0),
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


def verdict_after_assignment(
    verdicts: dict[str, ParsedVerdict], assignment: Assignment
) -> ParsedVerdict | None:
    verdict = verdicts.get(assignment.reviewer.lower())
    if verdict and verdict.submitted_at >= assignment.created_at:
        return verdict
    return None


def invalid_verdict_reason(
    records: Iterable[dict[str, Any]],
    assignment: Assignment,
    current_head: str,
) -> str | None:
    attempts: list[tuple[datetime, int, str]] = []
    for record in records:
        login = str((record.get("user") or {}).get("login") or "").lower()
        body = str(record.get("body") or "")
        submitted = record.get("submitted_at") or record.get("created_at")
        if login != assignment.reviewer.lower() or not submitted:
            continue
        submitted_at = parse_time(str(submitted))
        if submitted_at < assignment.created_at or "## Review verdict:" not in body:
            continue
        parsed, reason = parse_verdict_with_reason(record, current_head)
        if parsed is None and reason:
            attempts.append((submitted_at, int(record.get("id") or 0), reason))
    return max(attempts, default=(None, 0, None))[2]


def maintainer_assignment(
    comments: Iterable[dict[str, Any]], current_head: str
) -> Assignment | None:
    matches: list[Assignment] = []
    for comment in comments:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        if login not in TRUSTED_ASSIGNERS:
            continue
        body = str(comment.get("body") or "")
        for match in MAINTAINER_RE.finditer(body):
            if head_matches(current_head, match.group(2)):
                matches.append(
                    Assignment(
                        reviewer=match.group(1),
                        stage="maintainer",
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
    reviews: Iterable[dict[str, Any]], assignment: Assignment, current_head: str
) -> bool:
    for review in reviews:
        login = str((review.get("user") or {}).get("login") or "").lower()
        submitted = review.get("submitted_at")
        commit_id = str(review.get("commit_id") or "")
        if login != assignment.reviewer.lower() or review.get("state") != "APPROVED":
            continue
        if not submitted or parse_time(str(submitted)) < assignment.created_at:
            continue
        if not commit_id or not head_matches(current_head, commit_id):
            continue
        return True
    return False


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
    profiles = value.get("reviewer_profiles")
    if not isinstance(profiles, dict):
        raise RuntimeError(f"{CONFIG_PATH} must contain reviewer_profiles")
    value["reviewer_profiles"] = {
        str(login).lower(): str(family).lower() for login, family in profiles.items()
    }
    configured = {
        login.lower()
        for name in required_lists
        for login in value[name]
    }
    missing = configured - set(value["reviewer_profiles"])
    if missing:
        raise RuntimeError(f"reviewer_profiles missing: {sorted(missing)}")
    return value


def choose_candidates(
    config: dict[str, Any], first: ParsedVerdict, author: str
) -> list[tuple[str, str]]:
    profiles = config["reviewer_profiles"]
    if first.model_family == "zhipu-glm":
        pool = config["glm_first_fallback_reviewers"]
    else:
        pool = config["second_reviewers"]
    candidates = []
    for login in pool:
        lower = login.lower()
        family = profiles[lower]
        if lower in {author.lower(), first.commenter.lower()}:
            continue
        if family == first.model_family:
            continue
        candidates.append((login, family))
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
    protected_prefixes = (".github/", "docs/", "prompts/", "scripts/", "templates/", "tests/")
    protected_files = {
        "CONTRIBUTING.md",
        "CONTRIBUTING.zh-CN.md",
        "LICENSE",
        "LICENSE-DATA",
        "README.md",
        "README.zh-CN.md",
        "SECURITY.md",
        "SECURITY.zh-CN.md",
    }
    for item in files:
        filename = str(item.get("filename") or "")
        if filename in protected_files or filename.startswith(protected_prefixes):
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
    current, teams = requested_reviews(client, number)
    remove = [login for login in current if login.lower() != reviewer.lower()]
    if remove or teams:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="DELETE",
            payload={"reviewers": remove, "team_reviewers": teams},
        )
    if reviewer.lower() not in {login.lower() for login in current}:
        client.request(
            f"/pulls/{number}/requested_reviewers",
            method="POST",
            payload={"reviewers": [reviewer]},
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
        ]
    )
    if re_review:
        return "\n".join(
            [
                marker,
                "## Scenario re-review requested / 场景复审邀请",
                "",
                f"@{reviewer}, the PR head changed to `{head[:12]}`. Please re-review this head.",
                "You may consult your own prior verdict and the author's response, but do not read findings from other reviewers before publishing.",
                "",
                "```text",
                f"Re-review {pull['html_url']} at head {head} and post a new verdict that supersedes your prior verdict.",
                "```",
            ]
        )
    family_text = (
        f" Use `{required_family}` for this review. / 本轮请使用 `{required_family}`。"
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
    candidates: list[tuple[str, str]],
    stage: str,
    previous: Assignment | None,
) -> tuple[Assignment, dict[str, Any]]:
    number = int(pull["number"])
    ordered = rotated(candidates, number)
    if not ordered:
        raise RuntimeError(f"No {stage} reviewer is available")
    reviewer, family = ordered[0]
    existing = latest_assignment(
        assignment_records(client.comments(number)), stage, pull["head"]["sha"]
    )
    if existing:
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
        family,
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
    profiles = config["reviewer_profiles"]
    candidates = [
        (login, profiles[login.lower()])
        for login in config["reviewers"]
        if login.lower() not in {author, "keting"}
    ]
    previous = latest_assignment(assignments, "first")
    if previous:
        previous_match = [
            item for item in candidates if item[0].lower() == previous.reviewer.lower()
        ]
        if previous_match:
            candidates = previous_match
    assignment, _ = request_from_candidates(
        client, pull, candidates, "first", previous
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
            item for item in candidates if item[0].lower() == previous.reviewer.lower()
        ]
        if previous_match:
            candidates = previous_match
    assignment, _ = request_from_candidates(
        client, pull, candidates, "second", previous
    )
    return assignment


def ensure_maintainer(
    client: GitHubClient,
    pull: dict[str, Any],
    config: dict[str, Any],
    comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    reviewers: set[str],
) -> None:
    current = maintainer_assignment(comments, pull["head"]["sha"])
    if current:
        if has_formal_approval(reviews, current, pull["head"]["sha"]):
            return
        sync_review_request(client, int(pull["number"]), current.reviewer)
        return
    author = pull["user"]["login"].lower()
    pool = [login for login in config["maintainers"] if login.lower() != author]
    preferred = [login for login in pool if login.lower() not in reviewers]
    ordered = preferred or pool
    candidates = [(login, "") for login in ordered]
    if not candidates:
        raise RuntimeError("No maintainer is available after excluding the PR author")
    number = int(pull["number"])
    login, _ = rotated(candidates, number)[0]
    current = maintainer_assignment(client.comments(number), pull["head"]["sha"])
    if current:
        sync_review_request(client, number, current.reviewer)
        return
    try:
        sync_review_request(client, number, login)
    except Exception as error:
        raise RuntimeError(f"Could not request maintainer @{login}: {error}") from error
    marker = (
        f"<!-- scenario-maintainer-request:{login.lower()} "
        f"head:{pull['head']['sha'].lower()} -->"
    )
    try:
        client.add_comment(
            number,
            "\n".join(
                [
                    marker,
                    "## Maintainer final review requested / 维护者终审邀请",
                    "",
                    f"@{login}, `review-gate` has recorded two independent current-head APPROVE verdicts.",
                    "Please perform the final human check and use GitHub's formal Approve action if the PR is ready. Do not approve your own PR.",
                ]
            ),
        )
    except Exception as error:
        raise RuntimeError(
            f"@{login} may be requested but its maintainer comment failed: {error}"
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
        post_status(client, pull, "failure", "Scenario PR also changes protected protocol files")
        return None

    config = load_config()
    comments = client.comments(number)
    reviews = client.reviews(number)
    assignments = assignment_records(comments)
    current_head = pull["head"]["sha"]
    first = latest_assignment(assignments, "first", current_head)
    if first is None:
        first = request_first(client, pull, config, assignments)
        post_status(client, pull, "pending", f"Waiting for first verdict from @{first.reviewer}")
        return None

    records = comments + reviews
    verdicts = current_verdicts(records, current_head)
    first_verdict = verdict_after_assignment(verdicts, first)
    if first_verdict is None:
        sync_review_request(client, number, first.reviewer)
        reason = invalid_verdict_reason(records, first, current_head)
        description = (
            f"First verdict rejected: {reason}"
            if reason
            else f"Waiting for first verdict from @{first.reviewer}"
        )
        post_status(client, pull, "pending", description)
        return None
    if first_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
        clear_review_requests(client, number)
        post_status(client, pull, "failure", "Privacy concern raised; review flow stopped")
        return None
    expected_first_family = config["reviewer_profiles"][first.reviewer.lower()]
    if first_verdict.model_family not in {expected_first_family, "not-exposed"}:
        post_status(client, pull, "failure", "First verdict did not use its assigned model family")
        return None
    if first_verdict.verdict != "APPROVE":
        sync_review_request(client, number, first.reviewer)
        post_status(client, pull, "pending", f"Waiting for @{first.reviewer} to re-review changes")
        return None

    second = latest_assignment(assignments, "second", current_head)
    if second is None:
        second = request_second(client, pull, config, first_verdict, assignments)
        post_status(client, pull, "pending", f"Waiting for second verdict from @{second.reviewer}")
        return str(number) if second.reviewer.lower() == "keting" else None

    second_verdict = verdict_after_assignment(verdicts, second)
    if second_verdict is None:
        sync_review_request(client, number, second.reviewer)
        reason = invalid_verdict_reason(records, second, current_head)
        description = (
            f"Second verdict rejected: {reason}"
            if reason
            else f"Waiting for second verdict from @{second.reviewer}"
        )
        post_status(client, pull, "pending", description)
        return None
    if second_verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
        clear_review_requests(client, number)
        post_status(client, pull, "failure", "Privacy concern raised; review flow stopped")
        return None
    if second_verdict.verdict != "APPROVE":
        sync_review_request(client, number, second.reviewer)
        post_status(client, pull, "pending", f"Waiting for @{second.reviewer} to re-review changes")
        return None

    expected_second_family = config["reviewer_profiles"][second.reviewer.lower()]
    if second_verdict.model_family not in {expected_second_family, "not-exposed"}:
        post_status(client, pull, "failure", "Second verdict did not use its assigned model family")
        return None

    gate = evaluate_review_gate(
        records,
        current_head,
        expected_reviewers=(first.reviewer, second.reviewer),
    )
    if not gate["eligible"]:
        post_status(client, pull, "failure", "Two different reviewers and model families are required")
        return None

    post_status(client, pull, "success", "Two independent current-head APPROVE verdicts recorded")
    ensure_maintainer(
        client,
        pull,
        config,
        comments,
        reviews,
        {first.reviewer.lower(), second.reviewer.lower()},
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
