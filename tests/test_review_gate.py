import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from review_gate import evaluate_review_gate, legacy_key  # noqa: E402


HEAD = "0123456789abcdef0123456789abcdef01234567"


def record(
    record_id,
    verdict="APPROVE",
    reviewer="Codex / gpt-5.6-sol / high",
    key="agent:openai-gpt",
    head=HEAD,
    login="reviewer",
    association="MEMBER",
    submitted="2026-09-03T08:00:00Z",
):
    key_line = f"\nIndependence key: {key}" if key else ""
    return {
        "id": record_id,
        "html_url": f"https://example.test/review/{record_id}",
        "author_association": association,
        "user": {"login": login},
        "created_at": submitted,
        "body": (
            "Reviewed under: docs/review-process.md @ abcdef1\n\n"
            f"## Review verdict: {verdict}\n\n"
            f"Reviewed at head: {head}\n"
            f"Reviewer: {reviewer}{key_line}\n"
            "Date: 2026-09-03"
        ),
    }


class ReviewGateTests(unittest.TestCase):
    def test_two_distinct_reviewers_and_families_pass(self):
        result = evaluate_review_gate(
            [
                record(1),
                record(
                    2,
                    reviewer="Claude / opus / high",
                    key="agent:anthropic-claude",
                    login="other-reviewer",
                ),
            ],
            HEAD,
        )
        self.assertTrue(result["eligible"])

    def test_same_reviewer_does_not_count_twice(self):
        result = evaluate_review_gate(
            [
                record(1),
                record(2, key="agent:anthropic-claude", submitted="2026-09-03T09:00:00Z"),
            ],
            HEAD,
        )
        self.assertFalse(result["eligible"])
        self.assertEqual(result["approval_count"], 1)

    def test_same_family_does_not_pass(self):
        result = evaluate_review_gate(
            [record(1), record(2, login="other-reviewer")], HEAD
        )
        self.assertFalse(result["eligible"])

    def test_different_key_spellings_in_same_family_do_not_pass(self):
        result = evaluate_review_gate(
            [
                record(1, key="agent:openai-gpt"),
                record(2, key="agent:openai-gpt-5", login="other-reviewer"),
            ],
            HEAD,
        )
        self.assertFalse(result["eligible"])

    def test_latest_verdict_per_reviewer_wins(self):
        result = evaluate_review_gate(
            [
                record(1),
                record(2, verdict="REQUEST_CHANGES", submitted="2026-09-03T09:00:00Z"),
                record(
                    3,
                    key="agent:anthropic-claude",
                    login="other-reviewer",
                ),
            ],
            HEAD,
        )
        self.assertFalse(result["eligible"])
        self.assertEqual(result["approval_count"], 1)

    def test_privacy_verdict_blocks(self):
        result = evaluate_review_gate(
            [
                record(1, verdict="PRIVACY-CONCERN-RAISED-PRIVATELY"),
                record(
                    2,
                    key="agent:anthropic-claude",
                    login="other-reviewer",
                ),
            ],
            HEAD,
        )
        self.assertTrue(result["privacy"])
        self.assertFalse(result["eligible"])

    def test_stale_and_untrusted_verdicts_are_ignored(self):
        result = evaluate_review_gate(
            [record(1, head="a" * 40), record(2, association="NONE")], HEAD
        )
        self.assertEqual(result["approval_count"], 0)

    def test_human_key_must_match_comment_author(self):
        valid = record(1, reviewer="Alice", key="human:alice", login="Alice")
        invalid = record(2, reviewer="Alice", key="human:bob", login="Alice")
        self.assertEqual(evaluate_review_gate([valid], HEAD)["approval_count"], 1)
        self.assertEqual(evaluate_review_gate([invalid], HEAD)["approval_count"], 0)

    def test_glm_model_beats_claude_code_product_in_legacy_line(self):
        self.assertEqual(
            legacy_key("Claude Code x GLM-5.2 x high"), "agent:zhipu-glm"
        )

    def test_pull_request_review_timestamp_is_supported(self):
        value = record(1)
        value["submitted_at"] = value.pop("created_at")
        self.assertEqual(evaluate_review_gate([value], HEAD)["approval_count"], 1)


if __name__ == "__main__":
    unittest.main()
