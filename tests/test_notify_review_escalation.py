import http.client
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from notify_review_escalation import (  # noqa: E402
    Assignment,
    GitHubClient,
    already_notified,
    assignment_from_comments,
    build_email,
    classify_watchdog_alert,
    eligible_pull,
    has_completed_verdict,
    notify,
    notification_marker,
    process_watchdog,
    ready_at_from_timeline,
    requested_at_from_timeline,
)


NOW = datetime(2026, 9, 3, 8, 0, tzinfo=timezone.utc)
HEAD = "a" * 40


def pull(created_hours_ago=30, updated_hours_ago=30):
    return {
        "number": 42,
        "state": "open",
        "draft": False,
        "created_at": (NOW - timedelta(hours=created_hours_ago)).isoformat(),
        "updated_at": (NOW - timedelta(hours=updated_hours_ago)).isoformat(),
        "head": {"sha": HEAD},
        "base": {"ref": "main"},
    }


def comment(body, login="github-actions[bot]", hours_ago=30):
    return {
        "body": body,
        "created_at": (NOW - timedelta(hours=hours_ago)).isoformat(),
        "user": {"login": login},
    }


def verdict_body(head=HEAD, verdict="APPROVE"):
    return (
        "Reviewed under: docs/review-process.md @ 1234567\n\n"
        f"## Review verdict: {verdict}\n\n"
        f"Reviewed at head: {head}\n"
        "Reviewer: Codex / GPT-5 / high\n"
    )


class ReviewNotificationTests(unittest.TestCase):
    def test_parses_legacy_and_head_specific_assignments(self):
        legacy = comment("<!-- scenario-review-assignment:black-pwq -->")
        current = comment(
            f"<!-- scenario-review-assignment:XiaoCooder head:{HEAD} -->",
            hours_ago=10,
        )
        assignment = assignment_from_comments([legacy, current], HEAD)
        self.assertEqual(assignment.reviewer, "XiaoCooder")
        self.assertEqual(assignment.head, HEAD)

    def test_ignores_assignment_for_an_old_head(self):
        old = comment(f"<!-- scenario-review-assignment:black-pwq head:{'b' * 40} -->")
        self.assertIsNone(assignment_from_comments([old], HEAD))

    def test_legacy_assignment_is_done_by_any_later_structured_verdict(self):
        assigned = Assignment("black-pwq", NOW - timedelta(hours=30), None)
        stale_head = "b" * 40
        review = comment(
            verdict_body(stale_head), login="black-pwq", hours_ago=20
        )
        self.assertTrue(has_completed_verdict(assigned, HEAD, [review], []))

    def test_head_specific_assignment_requires_current_head_verdict(self):
        assigned = Assignment("black-pwq", NOW - timedelta(hours=30), HEAD)
        review = comment(
            verdict_body("b" * 40), login="black-pwq", hours_ago=20
        )
        self.assertFalse(has_completed_verdict(assigned, HEAD, [review], []))

    def test_trusted_carried_approval_completes_current_assignment(self):
        assigned = Assignment("black-pwq", NOW - timedelta(hours=30), HEAD)
        carried = comment(
            " ".join(
                [
                    "<!-- scenario-review-carried:black-pwq",
                    "stage:first",
                    f"reviewed-head:{'b' * 40}",
                    f"head:{HEAD}",
                    "verdict:42 -->",
                ]
            ),
            hours_ago=20,
        )
        self.assertTrue(has_completed_verdict(assigned, HEAD, [carried], []))

    def test_external_carried_marker_does_not_suppress_watchdog(self):
        assigned = Assignment("black-pwq", NOW - timedelta(hours=30), HEAD)
        carried = comment(
            " ".join(
                [
                    "<!-- scenario-review-carried:black-pwq",
                    "stage:first",
                    f"reviewed-head:{'b' * 40}",
                    f"head:{HEAD}",
                    "verdict:42 -->",
                ]
            ),
            login="external-author",
            hours_ago=20,
        )
        self.assertFalse(has_completed_verdict(assigned, HEAD, [carried], []))

    def test_unassigned_pull_alerts_after_threshold(self):
        alert = classify_watchdog_alert(
            pull(), [], [], [], NOW, timedelta(hours=24)
        )
        self.assertEqual(alert.reason, "unassigned")
        self.assertEqual(alert.reviewer, "none")

    def test_recent_unassigned_pull_does_not_alert(self):
        alert = classify_watchdog_alert(
            pull(created_hours_ago=3), [], [], [], NOW, timedelta(hours=24)
        )
        self.assertIsNone(alert)

    def test_old_draft_uses_recent_ready_time(self):
        value = pull(created_hours_ago=72)
        timeline = [
            {
                "event": "ready_for_review",
                "created_at": (NOW - timedelta(hours=2)).isoformat(),
            }
        ]
        alert = classify_watchdog_alert(
            value,
            [],
            [],
            [],
            NOW,
            timedelta(hours=24),
            ready_at=ready_at_from_timeline(value, timeline),
        )
        self.assertIsNone(alert)

    def test_requested_time_is_not_reset_by_later_pr_activity(self):
        value = pull(created_hours_ago=216, updated_hours_ago=0.1)
        requested_at = NOW - timedelta(hours=30)
        alert = classify_watchdog_alert(
            value,
            [],
            [],
            ["black-pwq"],
            NOW,
            timedelta(hours=24),
            requested_at=requested_at,
        )
        self.assertEqual(alert.reason, "stale-assignment")
        self.assertEqual(alert.since, requested_at)

    def test_extracts_current_review_request_time_from_timeline(self):
        timeline = [
            {
                "event": "review_requested",
                "created_at": (NOW - timedelta(hours=30)).isoformat(),
                "requested_reviewer": {"login": "black-pwq"},
            },
            {
                "event": "review_requested",
                "created_at": (NOW - timedelta(hours=2)).isoformat(),
                "requested_reviewer": {"login": "someone-else"},
            },
        ]
        self.assertEqual(
            requested_at_from_timeline(timeline, ["black-pwq"]),
            NOW - timedelta(hours=30),
        )

    def test_team_review_request_with_null_user_is_ignored(self):
        timeline = [
            {
                "event": "review_requested",
                "created_at": (NOW - timedelta(hours=30)).isoformat(),
                "requested_reviewer": None,
                "requested_team": {"slug": "release-maintainers"},
            }
        ]
        self.assertIsNone(requested_at_from_timeline(timeline, ["black-pwq"]))

    def test_stale_assignment_alerts_without_verdict(self):
        assigned = comment("<!-- scenario-review-assignment:black-pwq -->")
        alert = classify_watchdog_alert(
            pull(), [assigned], [], ["black-pwq"], NOW, timedelta(hours=24)
        )
        self.assertEqual(alert.reason, "stale-assignment")
        self.assertEqual(alert.reviewer, "black-pwq")

    def test_completed_request_changes_does_not_alert(self):
        assigned = comment("<!-- scenario-review-assignment:black-pwq -->")
        review = comment(
            verdict_body(verdict="REQUEST_CHANGES"),
            login="black-pwq",
            hours_ago=20,
        )
        alert = classify_watchdog_alert(
            pull(), [assigned, review], [], ["black-pwq"], NOW, timedelta(hours=24)
        )
        self.assertIsNone(alert)

    def test_completed_privacy_verdict_does_not_alert(self):
        assigned = comment("<!-- scenario-review-assignment:black-pwq -->")
        review = comment(
            verdict_body(verdict="PRIVACY-CONCERN-RAISED-PRIVATELY"),
            login="black-pwq",
            hours_ago=20,
        )
        alert = classify_watchdog_alert(
            pull(), [assigned, review], [], ["black-pwq"], NOW, timedelta(hours=24)
        )
        self.assertIsNone(alert)

    def test_pull_request_review_body_counts_as_completed(self):
        assigned = comment(f"<!-- scenario-review-assignment:black-pwq head:{HEAD} -->")
        review = {
            "body": verdict_body(),
            "submitted_at": (NOW - timedelta(hours=20)).isoformat(),
            "user": {"login": "black-pwq"},
        }
        alert = classify_watchdog_alert(
            pull(), [assigned], [review], ["black-pwq"], NOW, timedelta(hours=24)
        )
        self.assertIsNone(alert)

    def test_notification_marker_is_idempotent(self):
        marker = notification_marker("stale-assignment", HEAD, "black-pwq")
        self.assertTrue(
            already_notified(
                [comment(marker)], "stale-assignment", HEAD, "black-pwq"
            )
        )
        self.assertFalse(
            already_notified([comment(marker)], "unassigned", HEAD, "none")
        )

    def test_external_author_cannot_suppress_notification(self):
        marker = notification_marker("stale-assignment", HEAD, "black-pwq")
        self.assertFalse(
            already_notified(
                [comment(marker, login="external-author")],
                "stale-assignment",
                HEAD,
                "black-pwq",
            )
        )

    def test_eligible_pull_rejects_draft_closed_and_non_main(self):
        value = pull()
        self.assertTrue(eligible_pull(value))
        for field, replacement in (
            ("draft", True),
            ("state", "closed"),
            ("base", {"ref": "release"}),
        ):
            changed = {**value, field: replacement}
            self.assertFalse(eligible_pull(changed))

    def test_owner_assignment_email_contains_review_entry_and_footer(self):
        value = pull()
        value.update(
            {
                "title": "Scenario review",
                "html_url": "https://github.com/aicodingresearch/agent-hi-tax/pull/42",
                "base": {
                    "sha": "b" * 40,
                    "repo": {"full_name": "aicodingresearch/agent-hi-tax"},
                },
            }
        )
        message = build_email(value, "assigned-to-keting", "keting", 24)
        self.assertIn("已分配给你评审", str(message["Subject"]))
        self.assertIn("agent-review-and-scoring.zh-CN.md", message.get_content())
        self.assertIn("Review and post a verdict for", message.get_content())
        self.assertIn(
            "本邮件由 Agent 自动发送，如有错误请联系yinkt@zju.edu.cn",
            message.get_content(),
        )

    def test_reserves_marker_before_sending_email(self):
        events = []

        class Client:
            def add_comment(self, number, body):
                events.append(("reserve", number, body))
                return {"id": 123}

            def update_comment(self, comment_id, body):
                events.append(("update", comment_id, body))

        value = pull()
        value.update(
            {
                "title": "Scenario review",
                "html_url": "https://github.com/aicodingresearch/agent-hi-tax/pull/42",
                "base": {
                    "ref": "main",
                    "sha": "b" * 40,
                    "repo": {"full_name": "aicodingresearch/agent-hi-tax"},
                },
            }
        )
        with patch(
            "notify_review_escalation.send_email",
            side_effect=lambda message: events.append(("send", message)),
        ):
            notify(Client(), value, [], "assigned-to-keting", "keting", 24)
        self.assertEqual([event[0] for event in events], ["reserve", "send", "update"])

    def test_watchdog_continues_after_one_pull_fails(self):
        first = {**pull(), "number": 1}
        second = {**pull(), "number": 2}

        class Client:
            def open_pulls(self):
                return [first, second]

            def is_scenario_pull(self, number):
                if number == 1:
                    raise RuntimeError("temporary API failure")
                return True

            def comments(self, number):
                return []

            def reviews(self, number):
                return []

            def requested_reviewers(self, number):
                return []

            def timeline(self, number):
                return []

        sent, failures = process_watchdog(Client(), NOW, 24, dry_run=True)
        self.assertEqual(sent, 1)
        self.assertEqual(failures, 1)

    def test_github_get_retries_incomplete_read(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"{}"

        client = GitHubClient("aicodingresearch/agent-hi-tax", "test-token")
        with patch(
            "notify_review_escalation.urllib.request.urlopen",
            side_effect=[http.client.IncompleteRead(b""), Response()],
        ) as urlopen, patch("notify_review_escalation.time.sleep"):
            self.assertEqual(client.request("/pulls/58"), {})
        self.assertEqual(urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
