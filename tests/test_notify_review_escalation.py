import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from notify_review_escalation import (  # noqa: E402
    Assignment,
    already_notified,
    assignment_from_comments,
    build_email,
    classify_watchdog_alert,
    has_completed_verdict,
    notification_marker,
)


NOW = datetime(2026, 9, 3, 8, 0, tzinfo=timezone.utc)
HEAD = "a" * 40


def pull(created_hours_ago=30, updated_hours_ago=30):
    return {
        "number": 42,
        "created_at": (NOW - timedelta(hours=created_hours_ago)).isoformat(),
        "updated_at": (NOW - timedelta(hours=updated_hours_ago)).isoformat(),
        "head": {"sha": HEAD},
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
        alert = classify_watchdog_alert(
            pull(created_hours_ago=72),
            [],
            [],
            [],
            NOW,
            timedelta(hours=24),
            ready_at=NOW - timedelta(hours=2),
        )
        self.assertIsNone(alert)

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
        self.assertIn(
            "本邮件由 Agent 自动发送，如有错误请联系yinkt@zju.edu.cn",
            message.get_content(),
        )


if __name__ == "__main__":
    unittest.main()
