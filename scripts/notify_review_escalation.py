#!/usr/bin/env python3
"""Email the owner only for their own assignment or an overdue scenario review."""

from __future__ import annotations

import argparse
import json
import os
import re
import smtplib
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Any


API_ROOT = "https://api.github.com"
OWNER_LOGIN = "keting"
SCENARIO_RE = re.compile(
    r"^runs/\d{4}-\d{2}-\d{2}/[^/]+/manifest\.yaml$"
)
ASSIGNMENT_RE = re.compile(
    r"<!--\s*scenario-review-assignment:([A-Za-z0-9-]+)"
    r"(?:\s+head:([0-9a-f]{7,40}))?\s*-->",
    re.IGNORECASE,
)
VERDICT_RE = re.compile(
    r"^## Review verdict: "
    r"(APPROVE|REQUEST_CHANGES|PRIVACY-CONCERN-RAISED-PRIVATELY)\s*$",
    re.MULTILINE,
)
REVIEWED_HEAD_RE = re.compile(
    r"^Reviewed at head:\s*`?([0-9a-f]{7,40})`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
NOTIFICATION_RE = re.compile(
    r"<!--\s*review-notification:v1\s+reason:([a-z-]+)\s+"
    r"head:([0-9a-f]{40})\s+reviewer:([A-Za-z0-9_-]+)\s*-->",
    re.IGNORECASE,
)
TRUSTED_ASSIGNERS = {"github-actions[bot]", OWNER_LOGIN}
FOOTER = "本邮件由 Agent 自动发送，如有错误请联系yinkt@zju.edu.cn"


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def head_matches(current_head: str, recorded_head: str) -> bool:
    return current_head.lower().startswith(recorded_head.lower())


@dataclass(frozen=True)
class Assignment:
    reviewer: str
    assigned_at: datetime
    head: str | None


@dataclass(frozen=True)
class Alert:
    reason: str
    reviewer: str
    since: datetime


def assignment_from_comments(
    comments: list[dict[str, Any]], current_head: str
) -> Assignment | None:
    assignments: list[Assignment] = []
    for comment in comments:
        login = str(comment.get("user", {}).get("login", "")).lower()
        if login not in TRUSTED_ASSIGNERS:
            continue
        for match in ASSIGNMENT_RE.finditer(str(comment.get("body", ""))):
            recorded_head = match.group(2)
            if recorded_head and not head_matches(current_head, recorded_head):
                continue
            assignments.append(
                Assignment(
                    reviewer=match.group(1),
                    assigned_at=parse_time(comment["created_at"]),
                    head=recorded_head,
                )
            )
    return max(assignments, key=lambda item: item.assigned_at, default=None)


def has_completed_verdict(
    assignment: Assignment,
    current_head: str,
    comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> bool:
    candidates: list[tuple[str, str, str]] = []
    for comment in comments:
        candidates.append(
            (
                str(comment.get("user", {}).get("login", "")),
                str(comment.get("created_at", "")),
                str(comment.get("body", "")),
            )
        )
    for review in reviews:
        candidates.append(
            (
                str(review.get("user", {}).get("login", "")),
                str(review.get("submitted_at", "")),
                str(review.get("body", "")),
            )
        )

    for login, submitted_at, body in candidates:
        if login.lower() != assignment.reviewer.lower() or not submitted_at:
            continue
        if parse_time(submitted_at) < assignment.assigned_at:
            continue
        if not VERDICT_RE.search(body):
            continue
        reviewed_head = REVIEWED_HEAD_RE.search(body)
        if not reviewed_head:
            continue
        # Legacy assignment markers did not record a head. Any later structured
        # verdict proves that assignment was acted on; a new head-specific
        # assignment is responsible for requesting a re-review.
        if assignment.head is None or head_matches(current_head, reviewed_head.group(1)):
            return True
    return False


def notification_marker(reason: str, head: str, reviewer: str) -> str:
    return (
        f"<!-- review-notification:v1 reason:{reason} "
        f"head:{head.lower()} reviewer:{reviewer.lower()} -->"
    )


def already_notified(
    comments: list[dict[str, Any]], reason: str, head: str, reviewer: str
) -> bool:
    expected = (reason.lower(), head.lower(), reviewer.lower())
    for comment in comments:
        login = str(comment.get("user", {}).get("login", "")).lower()
        if login not in TRUSTED_ASSIGNERS:
            continue
        for match in NOTIFICATION_RE.finditer(str(comment.get("body", ""))):
            actual = (match.group(1).lower(), match.group(2).lower(), match.group(3).lower())
            if actual == expected:
                return True
    return False


def classify_watchdog_alert(
    pull: dict[str, Any],
    comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    requested_reviewers: list[str],
    now: datetime,
    threshold: timedelta,
    ready_at: datetime | None = None,
    requested_at: datetime | None = None,
) -> Alert | None:
    head = str(pull["head"]["sha"])
    assignment = assignment_from_comments(comments, head)

    if assignment is None and requested_reviewers:
        assignment = Assignment(
            reviewer=requested_reviewers[0],
            assigned_at=requested_at or ready_at or parse_time(pull["created_at"]),
            head=None,
        )

    if assignment is None:
        since = ready_at or parse_time(pull["created_at"])
        if now - since >= threshold:
            return Alert(reason="unassigned", reviewer="none", since=since)
        return None

    if has_completed_verdict(assignment, head, comments, reviews):
        return None
    if now - assignment.assigned_at >= threshold:
        return Alert(
            reason="stale-assignment",
            reviewer=assignment.reviewer,
            since=assignment.assigned_at,
        )
    return None


def ready_at_from_timeline(
    pull: dict[str, Any], timeline: list[dict[str, Any]]
) -> datetime:
    ready_at: datetime | None = parse_time(pull["created_at"])
    for event in timeline:
        event_name = event.get("event")
        if event_name == "convert_to_draft":
            ready_at = None
        elif event_name == "ready_for_review" and event.get("created_at"):
            ready_at = parse_time(str(event["created_at"]))
    # The caller excludes current drafts. If GitHub omitted a transition event,
    # creation time is the oldest safe bound and cannot be reset by comments.
    return ready_at or parse_time(pull["created_at"])


def requested_at_from_timeline(
    timeline: list[dict[str, Any]], requested_reviewers: list[str]
) -> datetime | None:
    requested = {login.lower() for login in requested_reviewers}
    times: list[datetime] = []
    for event in timeline:
        if event.get("event") != "review_requested":
            continue
        requested_reviewer = event.get("requested_reviewer") or {}
        login = str(requested_reviewer.get("login", "")).lower()
        if login in requested and event.get("created_at"):
            times.append(parse_time(str(event["created_at"])))
    return max(times, default=None)


class GitHubClient:
    def __init__(self, repository: str, token: str) -> None:
        self.repository = repository
        self.token = token

    def request(
        self, path: str, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> Any:
        url = f"{API_ROOT}/repos/{self.repository}{path}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "agent-hi-tax-review-notifier",
            },
        )
        attempts = 3 if method in {"GET", "PATCH"} else 1
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")[:1000]
                retryable = error.code in {429, 500, 502, 503, 504}
                if retryable and attempt + 1 < attempts:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError(
                    f"GitHub API {method} {path} failed: {error.code} {detail}"
                ) from error
            except urllib.error.URLError as error:
                if attempt + 1 < attempts:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError(f"GitHub API {method} {path} failed: {error}") from error
        raise AssertionError("unreachable")

    def paginate(self, path: str) -> list[dict[str, Any]]:
        separator = "&" if "?" in path else "?"
        results: list[dict[str, Any]] = []
        for page in range(1, 101):
            values = self.request(f"{path}{separator}per_page=100&page={page}")
            if not isinstance(values, list):
                raise RuntimeError(f"Expected a list from GitHub API path {path}")
            results.extend(values)
            if len(values) < 100:
                return results
        raise RuntimeError(f"GitHub API pagination exceeded 100 pages for {path}")

    def pull(self, number: int) -> dict[str, Any]:
        value = self.request(f"/pulls/{number}")
        if not isinstance(value, dict):
            raise RuntimeError(f"Pull request #{number} was not an object")
        return value

    def is_scenario_pull(self, number: int) -> bool:
        return any(
            item.get("status") == "added" and SCENARIO_RE.fullmatch(str(item.get("filename", "")))
            for item in self.paginate(f"/pulls/{number}/files")
        )

    def comments(self, number: int) -> list[dict[str, Any]]:
        return self.paginate(f"/issues/{number}/comments")

    def reviews(self, number: int) -> list[dict[str, Any]]:
        return self.paginate(f"/pulls/{number}/reviews")

    def timeline(self, number: int) -> list[dict[str, Any]]:
        return self.paginate(f"/issues/{number}/timeline")

    def requested_reviewers(self, number: int) -> list[str]:
        value = self.request(f"/pulls/{number}/requested_reviewers")
        return [str(user["login"]) for user in value.get("users", [])]

    def open_pulls(self) -> list[dict[str, Any]]:
        return self.paginate("/pulls?state=open&base=main")

    def add_comment(self, number: int, body: str) -> dict[str, Any]:
        value = self.request(
            f"/issues/{number}/comments", method="POST", payload={"body": body}
        )
        if not isinstance(value, dict):
            raise RuntimeError("GitHub did not return the notification reservation")
        return value

    def update_comment(self, comment_id: int, body: str) -> None:
        self.request(
            f"/issues/comments/{comment_id}", method="PATCH", payload={"body": body}
        )


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_email(
    pull: dict[str, Any], reason: str, reviewer: str, threshold_hours: int
) -> EmailMessage:
    number = pull["number"]
    title = str(pull["title"]).replace("\r", " ").replace("\n", " ")
    url = pull["html_url"]
    head = pull["head"]["sha"]
    repository_url = f"https://github.com/{pull['base']['repo']['full_name']}"
    entry_url = f"{repository_url}/blob/{pull['base']['sha']}/docs/agent-review-and-scoring.zh-CN.md"
    prompt = (
        f"Review and post a verdict for {url} using the repository's Agent "
        "review entry point. Do not read existing review findings before "
        "publishing your independent verdict."
    )

    message = EmailMessage()
    if reason == "assigned-to-keting":
        message["Subject"] = f"[Agent Hi Tax] PR #{number} 已分配给你评审"
        summary = "该场景 PR 的评审任务已明确分配给你。"
    elif reason == "unassigned":
        message["Subject"] = f"[Agent Hi Tax] PR #{number} 超过 {threshold_hours} 小时未分配评审"
        summary = f"该场景 PR 进入可评审状态后，超过 {threshold_hours} 小时仍没有成功分配 Reviewer。"
    else:
        message["Subject"] = f"[Agent Hi Tax] PR #{number} 评审超过 {threshold_hours} 小时未完成"
        summary = (
            f"该场景 PR 已分配给 @{reviewer}，但超过 {threshold_hours} 小时仍未发布结构化 verdict。"
        )

    body = "\n".join(
        [
            summary,
            "",
            f"PR：#{number} {title}",
            f"地址：{url}",
            f"Current head：{head}",
            f"评审入口：{entry_url}",
            "",
            "可复制 Prompt：",
            prompt,
            "",
            FOOTER,
        ]
    )
    message.set_content(body)
    return message


def send_email(message: EmailMessage) -> None:
    host = required_env("SMTP_HOST")
    port = int(required_env("SMTP_PORT"))
    username = required_env("SMTP_USER")
    password = required_env("SMTP_AUTH_CODE")
    recipient = required_env("NOTIFY_TO")
    message["From"] = username
    message["To"] = recipient

    tls_context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=tls_context, timeout=30) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls(context=tls_context)
            smtp.login(username, password)
            smtp.send_message(message)


def eligible_pull(pull: dict[str, Any]) -> bool:
    return (
        pull.get("state") == "open"
        and not pull.get("draft", False)
        and pull.get("base", {}).get("ref") == "main"
    )


def notify(
    client: GitHubClient,
    pull: dict[str, Any],
    comments: list[dict[str, Any]],
    reason: str,
    reviewer: str,
    threshold_hours: int,
    dry_run: bool = False,
) -> bool:
    head = str(pull["head"]["sha"]).lower()
    if already_notified(comments, reason, head, reviewer):
        print(f"PR #{pull['number']}: {reason} email already sent for {head[:12]}")
        return False

    if dry_run:
        print(f"PR #{pull['number']}: would send {reason} email")
        return True

    marker = notification_marker(reason, head, reviewer)
    reservation = client.add_comment(
        int(pull["number"]),
        f"{marker}\nReview notification reserved. / 评审通知已预留。",
    )
    message = build_email(pull, reason, reviewer, threshold_hours)
    try:
        send_email(message)
    except Exception:
        client.update_comment(
            int(reservation["id"]),
            f"{marker}\nReview notification failed; automatic retry is suppressed to prevent duplicate email. / 评审通知失败；为避免重复邮件，已停止自动重试。",
        )
        raise
    client.update_comment(
        int(reservation["id"]),
        f"{marker}\nReview notification sent to the maintainer. / 已向维护者发送评审通知。",
    )
    print(f"PR #{pull['number']}: sent {reason} email")
    return True


def process_assigned(
    client: GitHubClient, number: int, threshold_hours: int, dry_run: bool = False
) -> int:
    pull = client.pull(number)
    if not eligible_pull(pull) or not client.is_scenario_pull(number):
        print(f"PR #{number}: not an eligible open scenario PR")
        return 0
    comments = client.comments(number)
    return int(
        notify(
            client,
            pull,
            comments,
            reason="assigned-to-keting",
            reviewer=OWNER_LOGIN,
            threshold_hours=threshold_hours,
            dry_run=dry_run,
        )
    )


def process_watchdog(
    client: GitHubClient,
    now: datetime,
    threshold_hours: int,
    dry_run: bool = False,
) -> tuple[int, int]:
    sent = 0
    failures = 0
    threshold = timedelta(hours=threshold_hours)
    for pull in client.open_pulls():
        number = int(pull["number"])
        try:
            if not eligible_pull(pull) or not client.is_scenario_pull(number):
                continue
            comments = client.comments(number)
            reviews = client.reviews(number)
            requested = client.requested_reviewers(number)
            timeline = client.timeline(number)
            ready_at = ready_at_from_timeline(pull, timeline)
            requested_at = requested_at_from_timeline(timeline, requested)
            alert = classify_watchdog_alert(
                pull,
                comments,
                reviews,
                requested,
                now,
                threshold,
                ready_at=ready_at,
                requested_at=requested_at,
            )
            if alert is None:
                print(f"PR #{number}: no review escalation needed")
                continue
            sent += int(
                notify(
                    client,
                    pull,
                    comments,
                    reason=alert.reason,
                    reviewer=alert.reviewer,
                    threshold_hours=threshold_hours,
                    dry_run=dry_run,
                )
            )
        except Exception as error:
            failures += 1
            detail = str(error).replace("\r", " ").replace("\n", " ")
            print(f"::error title=Review watchdog failed for PR #{number}::{detail}")
    return sent, failures


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("assigned-to-keting", "watchdog"), required=True
    )
    parser.add_argument("--pull-request-number", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repository = required_env("REPOSITORY")
    token = required_env("GITHUB_TOKEN")
    threshold_hours = int(os.environ.get("REVIEW_ESCALATION_HOURS", "24"))
    if threshold_hours <= 0:
        raise RuntimeError("REVIEW_ESCALATION_HOURS must be positive")

    client = GitHubClient(repository, token)
    if args.mode == "assigned-to-keting":
        if args.pull_request_number is None:
            raise RuntimeError("--pull-request-number is required for assigned-to-keting")
        sent = process_assigned(
            client, args.pull_request_number, threshold_hours, dry_run=args.dry_run
        )
    else:
        sent, failures = process_watchdog(
            client,
            datetime.now(timezone.utc),
            threshold_hours,
            dry_run=args.dry_run,
        )
    print(f"review notifications sent: {sent}")
    if args.mode == "watchdog" and failures:
        raise RuntimeError(f"review watchdog failed for {failures} pull request(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
