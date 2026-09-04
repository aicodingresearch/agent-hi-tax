import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from review_gate import evaluate_review_gate, legacy_key, parse_verdict_with_reason  # noqa: E402


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

    def test_noncanonical_agent_keys_are_rejected(self):
        for key in ("agent:codex", "agent:gpt-5.6-sol", "agent:claude", "agent:glm"):
            parsed, reason = parse_verdict_with_reason(record(1, key=key), HEAD)
            self.assertIsNone(parsed)
            self.assertIn("canonical", reason)

    def test_not_exposed_cannot_satisfy_two_family_gate(self):
        result = evaluate_review_gate(
            [
                record(1, key="agent:not-exposed"),
                record(
                    2,
                    key="agent:anthropic-claude",
                    login="other-reviewer",
                ),
            ],
            HEAD,
        )
        self.assertFalse(result["eligible"])

    def test_human_review_can_pair_with_a_known_agent_family(self):
        result = evaluate_review_gate(
            [
                record(1, reviewer="Reviewer", key="human:reviewer"),
                record(
                    2,
                    key="agent:anthropic-claude",
                    login="other-reviewer",
                ),
            ],
            HEAD,
        )
        self.assertTrue(result["eligible"])

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

    def test_expected_reviewer_is_trusted_when_actions_hides_association(self):
        hidden = record(1, association="NONE", login="black-pwq")
        result = evaluate_review_gate(
            [hidden], HEAD, expected_reviewers=("black-pwq",)
        )
        self.assertEqual(result["approval_count"], 1)

    def test_unassigned_hidden_association_reviewer_remains_untrusted(self):
        hidden = record(1, association="NONE", login="external-author")
        result = evaluate_review_gate(
            [hidden], HEAD, expected_reviewers=("black-pwq",)
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

    def test_kimi_family_is_canonical_and_wins_over_product_name(self):
        parsed, reason = parse_verdict_with_reason(
            record(1, reviewer="WorkBuddy / Kimi / high", key="agent:moonshot-kimi"),
            HEAD,
        )
        self.assertIsNone(reason)
        self.assertEqual(parsed.model_family, "moonshot-kimi")
        self.assertEqual(
            legacy_key("Codex-compatible client / Kimi K2.5"),
            "agent:moonshot-kimi",
        )

    def test_pull_request_review_timestamp_is_supported(self):
        value = record(1)
        value["submitted_at"] = value.pop("created_at")
        self.assertEqual(evaluate_review_gate([value], HEAD)["approval_count"], 1)

    def test_verified_carried_approvals_can_satisfy_the_gate(self):
        old_head = "a" * 40
        first, _ = parse_verdict_with_reason(record(1, head=old_head), old_head)
        second, _ = parse_verdict_with_reason(
            record(
                2,
                reviewer="Claude / opus / high",
                key="agent:anthropic-claude",
                head=old_head,
                login="other-reviewer",
            ),
            old_head,
        )
        result = evaluate_review_gate(
            [], HEAD, carried_verdicts=(first, second)
        )
        self.assertTrue(result["eligible"])

    def test_current_head_verdict_supersedes_a_carried_approval(self):
        old_head = "a" * 40
        carried, _ = parse_verdict_with_reason(record(1, head=old_head), old_head)
        result = evaluate_review_gate(
            [record(2, verdict="REQUEST_CHANGES")],
            HEAD,
            carried_verdicts=(carried,),
        )
        self.assertEqual(result["approval_count"], 0)


if __name__ == "__main__":
    unittest.main()
