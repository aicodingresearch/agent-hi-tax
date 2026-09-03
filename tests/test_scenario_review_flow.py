import base64
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scenario_review_flow import (  # noqa: E402
    assignment_records,
    choose_candidates,
    has_formal_approval,
    latest_assignment,
    normalized_config,
    process_pull,
)
from review_gate import parse_verdict  # noqa: E402


HEAD = "a" * 40
BASE = "b" * 40
NOW = "2026-09-03T08:00:00Z"


def config():
    return {
        "reviewers": [
            "beautyarbutin",
            "XiaoCooder",
            "AHMEDALATTAR416",
            "black-pwq",
            "leonadoor",
        ],
        "reviewer_profiles": {
            "beautyarbutin": "openai-gpt",
            "XiaoCooder": "openai-gpt",
            "AHMEDALATTAR416": "zhipu-glm",
            "black-pwq": "openai-gpt",
            "leonadoor": "openai-gpt",
            "keting": "anthropic-claude",
        },
        "second_reviewers": ["keting", "AHMEDALATTAR416"],
        "glm_first_fallback_reviewers": [
            "beautyarbutin",
            "XiaoCooder",
            "black-pwq",
            "leonadoor",
        ],
        "maintainers": ["beautyarbutin", "XiaoCooder"],
    }


def pull(number=1, author="contributor"):
    return {
        "number": number,
        "state": "open",
        "draft": False,
        "html_url": f"https://github.com/aicodingresearch/agent-hi-tax/pull/{number}",
        "user": {"login": author},
        "head": {"sha": HEAD},
        "base": {
            "ref": "main",
            "sha": BASE,
            "repo": {
                "html_url": "https://github.com/aicodingresearch/agent-hi-tax"
            },
        },
    }


def verdict(login, family, verdict="APPROVE", submitted="2026-09-03T09:00:00Z"):
    return {
        "id": 900,
        "html_url": "https://example.test/verdict",
        "author_association": "MEMBER",
        "created_at": submitted,
        "user": {"login": login},
        "body": (
            "Reviewed under: docs/review-process.md @ abcdef1\n\n"
            f"## Review verdict: {verdict}\n\n"
            f"Reviewed at head: {HEAD}\n"
            f"Reviewer: Agent / model / high\n"
            f"Independence key: agent:{family}\n"
            "Date: 2026-09-03\n"
            "Could not verify: private originals"
        ),
    }


class FakeClient:
    def __init__(self, value):
        self.value = value
        self.config = config()
        self.comments_data = []
        self.reviews_data = []
        self.requested = []
        self.statuses = []
        self.request_history = []
        self.next_comment = 1
        self.scenario = True

    def paginate(self, path):
        if path.startswith(f"/pulls/{self.value['number']}/files"):
            return [] if not self.scenario else [
                {
                    "status": "added",
                    "filename": "runs/2026-09-03/example/manifest.yaml",
                }
            ]
        raise AssertionError(path)

    def request(self, path, method="GET", payload=None):
        if path.startswith("/contents/.github/scenario-reviewers.json"):
            raw = json.dumps(self.config).encode("utf-8")
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(raw).decode("ascii"),
            }
        if path == f"/pulls/{self.value['number']}/requested_reviewers":
            if method == "GET":
                return {"users": [{"login": login} for login in self.requested]}
            if method == "DELETE":
                removed = {login.lower() for login in payload["reviewers"]}
                self.requested = [
                    login for login in self.requested if login.lower() not in removed
                ]
                return {}
            if method == "POST":
                reviewer = payload["reviewers"][0]
                self.requested = [reviewer]
                self.request_history.append(reviewer)
                return {}
        if path == f"/statuses/{self.value['head']['sha']}" and method == "POST":
            self.statuses.append(payload)
            return {}
        raise AssertionError((method, path, payload))

    def comments(self, number):
        return list(self.comments_data)

    def reviews(self, number):
        return list(self.reviews_data)

    def add_comment(self, number, body):
        value = {
            "id": self.next_comment,
            "created_at": NOW,
            "author_association": "MEMBER",
            "user": {"login": "github-actions[bot]"},
            "body": body,
            "html_url": f"https://example.test/comment/{self.next_comment}",
        }
        self.next_comment += 1
        self.comments_data.append(value)
        return value

    def add_verdict(self, login, family, decision="APPROVE", submitted="2026-09-03T09:00:00Z"):
        value = verdict(login, family, decision, submitted)
        value["id"] = 800 + len(self.comments_data)
        self.comments_data.append(value)


class ScenarioReviewFlowTests(unittest.TestCase):
    def test_untrusted_assignment_marker_is_ignored(self):
        comments = [
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "external-author"},
                "body": (
                    f"<!-- scenario-review-assignment:keting head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:first -->"
                ),
            }
        ]
        self.assertEqual(assignment_records(comments), [])

    def test_head_and_stage_select_current_assignment(self):
        comments = [
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"<!-- scenario-review-assignment:black-pwq head:{'c' * 40} -->\n"
                    "<!-- scenario-review-stage:first -->"
                ),
            },
            {
                "id": 2,
                "created_at": "2026-09-03T09:00:00Z",
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"<!-- scenario-review-assignment:XiaoCooder head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:second -->"
                ),
            },
        ]
        assignments = assignment_records(comments)
        self.assertIsNone(latest_assignment(assignments, "first", HEAD))
        self.assertEqual(
            latest_assignment(assignments, "second", HEAD).reviewer, "XiaoCooder"
        )

    def test_openai_first_routes_to_keting_or_glm(self):
        parsed = parse_verdict(verdict("beautyarbutin", "openai-gpt"), HEAD)
        candidates = choose_candidates(normalized_config(config()), parsed, "contributor")
        self.assertEqual(
            candidates,
            [("keting", "anthropic-claude"), ("AHMEDALATTAR416", "zhipu-glm")],
        )

    def test_glm_first_routes_to_codex_and_excludes_owner(self):
        parsed = parse_verdict(verdict("AHMEDALATTAR416", "zhipu-glm"), HEAD)
        candidates = choose_candidates(normalized_config(config()), parsed, "XiaoCooder")
        self.assertEqual(
            {login for login, _ in candidates},
            {"beautyarbutin", "black-pwq", "leonadoor"},
        )
        self.assertNotIn("keting", {login for login, _ in candidates})

    def test_new_scenario_assigns_first_reviewer_but_never_owner(self):
        client = FakeClient(pull(number=1))
        self.assertIsNone(process_pull(client, client.value))
        assignment = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        self.assertEqual(assignment.reviewer, "beautyarbutin")
        self.assertNotEqual(assignment.reviewer, "keting")
        self.assertEqual(client.statuses[-1]["state"], "pending")

    def test_non_scenario_pull_reports_not_applicable_success(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        self.assertIsNone(process_pull(client, client.value))
        self.assertEqual(client.statuses[-1]["state"], "success")
        self.assertIn("does not apply", client.statuses[-1]["description"])

    def test_glm_first_approval_assigns_another_codex_reviewer(self):
        client = FakeClient(pull(number=3))
        process_pull(client, client.value)
        first = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        self.assertEqual(first.reviewer.lower(), "ahmedalattar416")
        client.add_verdict("AHMEDALATTAR416", "zhipu-glm")
        self.assertIsNone(process_pull(client, client.value))
        second = latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        self.assertIn(
            second.reviewer,
            {"beautyarbutin", "XiaoCooder", "black-pwq", "leonadoor"},
        )
        self.assertNotEqual(second.reviewer, "keting")

    def test_openai_first_approval_assigns_owner_and_requests_email(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        self.assertEqual(process_pull(client, client.value), "1")
        second = latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        self.assertEqual(second.reviewer, "keting")

    def test_request_changes_keeps_first_reviewer_and_does_not_assign_second(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt", "REQUEST_CHANGES")
        self.assertIsNone(process_pull(client, client.value))
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )
        self.assertEqual(client.requested, ["beautyarbutin"])

    def test_new_head_reuses_first_reviewer_with_short_re_review_message(self):
        client = FakeClient(pull(number=3))
        process_pull(client, client.value)
        original = latest_assignment(
            assignment_records(client.comments_data), "first", HEAD
        )
        client.value["head"]["sha"] = "c" * 40
        process_pull(client, client.value)
        first = latest_assignment(
            assignment_records(client.comments_data), "first", "c" * 40
        )
        self.assertEqual(first.reviewer, original.reviewer)
        self.assertIn("Scenario re-review requested", client.comments_data[-1]["body"])
        self.assertIn("your own prior verdict", client.comments_data[-1]["body"])

    def test_privacy_verdict_stops_flow_and_clears_request(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict(
            "beautyarbutin", "openai-gpt", "PRIVACY-CONCERN-RAISED-PRIVATELY"
        )
        process_pull(client, client.value)
        self.assertEqual(client.requested, [])
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_two_independent_approvals_request_one_maintainer(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict("keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z")
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "success")
        maintainer = next(
            comment
            for comment in client.comments_data
            if "scenario-maintainer-request" in comment["body"]
        )
        self.assertIn("xiaocooder", maintainer["body"].lower())
        self.assertEqual(client.requested, ["XiaoCooder"])

    def test_second_reviewer_must_use_assigned_model_family(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict("keting", "zhipu-glm", submitted="2026-09-03T10:00:00Z")
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertFalse(
            any(
                "scenario-maintainer-request" in comment["body"]
                for comment in client.comments_data
            )
        )

    def test_formal_maintainer_approval_is_not_re_requested(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict("keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z")
        process_pull(client, client.value)
        assignment = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(assignment.reviewer, "keting")
        maintainer_comment = next(
            comment
            for comment in client.comments_data
            if "scenario-maintainer-request" in comment["body"]
        )
        client.reviews_data.append(
            {
                "state": "APPROVED",
                "submitted_at": "2026-09-03T11:00:00Z",
                "commit_id": HEAD,
                "user": {"login": "XiaoCooder"},
            }
        )
        before = len(client.request_history)
        process_pull(client, client.value)
        self.assertEqual(len(client.request_history), before)
        maintenance = assignment_records([maintainer_comment])
        self.assertEqual(maintenance, [])

    def test_formal_approval_must_match_maintainer_and_head(self):
        from scenario_review_flow import Assignment
        from review_gate import parse_time

        assignment = Assignment(
            reviewer="XiaoCooder",
            stage="maintainer",
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
        )
        wrong = {
            "state": "APPROVED",
            "submitted_at": "2026-09-03T11:00:00Z",
            "commit_id": "c" * 40,
            "user": {"login": "XiaoCooder"},
        }
        self.assertFalse(has_formal_approval([wrong], assignment, HEAD))


if __name__ == "__main__":
    unittest.main()
