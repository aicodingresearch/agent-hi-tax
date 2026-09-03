import base64
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scenario_review_flow import (  # noqa: E402
    Assignment,
    MaintainerRequest,
    allowed_assignment_families,
    assignment_records,
    changes_protected_protocol,
    choose_candidates,
    has_formal_approval,
    latest_assignment,
    main,
    normalized_config,
    PROTECTED_PROTOCOL_FILES,
    PROTECTED_PROTOCOL_PREFIXES,
    process_pull,
    request_first,
)
from review_gate import parse_time, parse_verdict  # noqa: E402


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
        "reviewer_capabilities": {
            "beautyarbutin": [
                {"agent_product": "codex", "model_family": "openai-gpt"}
            ],
            "XiaoCooder": [
                {"agent_product": "codex", "model_family": "openai-gpt"}
            ],
            "AHMEDALATTAR416": [
                {"agent_product": "claude-code", "model_family": "zhipu-glm"}
            ],
            "black-pwq": [
                {"agent_product": "codex", "model_family": "openai-gpt"}
            ],
            "leonadoor": [
                {"agent_product": "codex", "model_family": "openai-gpt"}
            ],
            "keting": [
                {"agent_product": "claude-code", "model_family": "anthropic-claude"},
                {"agent_product": "workbuddy", "model_family": "moonshot-kimi"},
                {"agent_product": "codex", "model_family": "openai-gpt"},
            ],
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
        self.teams = []
        self.statuses = []
        self.request_history = []
        self.next_comment = 1
        self.comment_time = NOW
        self.scenario = True
        self.protocol_change = False
        self.fail_files = False

    def paginate(self, path):
        if path.startswith(f"/pulls/{self.value['number']}/files"):
            if self.fail_files:
                raise RuntimeError("file API unavailable")
            values = [] if not self.scenario else [
                {
                    "status": "added",
                    "filename": "runs/2026-09-03/example/manifest.yaml",
                }
            ]
            if self.protocol_change:
                values.append({"status": "modified", "filename": ".github/CODEOWNERS"})
            return values
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
                return {
                    "users": [{"login": login} for login in self.requested],
                    "teams": [{"slug": slug} for slug in self.teams],
                }
            if method == "DELETE":
                removed = {login.lower() for login in payload["reviewers"]}
                self.requested = [
                    login for login in self.requested if login.lower() not in removed
                ]
                removed_teams = {
                    slug.lower() for slug in payload.get("team_reviewers", [])
                }
                self.teams = [
                    slug for slug in self.teams if slug.lower() not in removed_teams
                ]
                return {}
            if method == "POST":
                current = {login.lower() for login in self.requested}
                for reviewer in payload["reviewers"]:
                    if reviewer.lower() not in current:
                        self.requested.append(reviewer)
                        self.request_history.append(reviewer)
                        current.add(reviewer.lower())
                return {}
        if path == f"/commits/{self.value['head']['sha']}/status" and method == "GET":
            return {"statuses": list(reversed(self.statuses))}
        if path == f"/statuses/{self.value['head']['sha']}" and method == "POST":
            self.statuses.append(payload)
            return {}
        raise AssertionError((method, path, payload))

    def comments(self, number):
        return list(self.comments_data)

    def pull(self, number):
        return self.value

    def reviews(self, number):
        return list(self.reviews_data)

    def add_comment(self, number, body):
        value = {
            "id": self.next_comment,
            "created_at": self.comment_time,
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

    def test_protocol_boundary_matches_documented_paths(self):
        self.assertTrue(
            changes_protected_protocol(
                [{"filename": "docs/review-process.md"}]
            )
        )
        self.assertFalse(
            changes_protected_protocol(
                [{"filename": "docs/wanted-scenarios.md"}]
            )
        )

    def test_protocol_boundary_matches_codeowners(self):
        path = Path(__file__).resolve().parents[1] / ".github" / "CODEOWNERS"
        patterns = {
            line.split()[0]
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        expected = {f"/{prefix}" for prefix in PROTECTED_PROTOCOL_PREFIXES}
        expected.update(f"/{filename}" for filename in PROTECTED_PROTOCOL_FILES)
        self.assertEqual(patterns, expected)

    def test_openai_first_routes_to_keting_or_glm(self):
        parsed = parse_verdict(verdict("beautyarbutin", "openai-gpt"), HEAD)
        candidates = choose_candidates(normalized_config(config()), parsed, "contributor")
        self.assertEqual(
            [
                (item.login, item.agent_product, item.model_family)
                for item in candidates
            ],
            [
                ("keting", "claude-code", "anthropic-claude"),
                ("AHMEDALATTAR416", "claude-code", "zhipu-glm"),
            ],
        )

    def test_glm_first_routes_to_codex_and_excludes_owner(self):
        parsed = parse_verdict(verdict("AHMEDALATTAR416", "zhipu-glm"), HEAD)
        candidates = choose_candidates(normalized_config(config()), parsed, "XiaoCooder")
        self.assertEqual(
            {item.login for item in candidates},
            {"beautyarbutin", "black-pwq", "leonadoor"},
        )
        self.assertNotIn("keting", {item.login for item in candidates})

    def test_same_reviewer_can_offer_multiple_capabilities(self):
        parsed = parse_verdict(verdict("XiaoCooder", "anthropic-claude"), HEAD)
        candidates = choose_candidates(normalized_config(config()), parsed, "contributor")
        keting = next(item for item in candidates if item.login == "keting")
        self.assertEqual(
            (keting.agent_product, keting.model_family),
            ("workbuddy", "moonshot-kimi"),
        )

    def test_legacy_assignment_uses_only_first_configured_capability(self):
        legacy = Assignment(
            reviewer="keting",
            stage="second",
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
        )
        self.assertEqual(
            allowed_assignment_families(normalized_config(config()), legacy),
            {"anthropic-claude"},
        )

    def test_new_scenario_assigns_first_reviewer_but_never_owner(self):
        client = FakeClient(pull(number=1))
        self.assertIsNone(process_pull(client, client.value))
        assignment = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        self.assertEqual(assignment.reviewer, "beautyarbutin")
        self.assertNotEqual(assignment.reviewer, "keting")
        self.assertEqual(
            (assignment.agent_product, assignment.model_family),
            ("codex", "openai-gpt"),
        )
        self.assertEqual(client.statuses[-1]["state"], "pending")

    def test_owner_is_excluded_even_if_misconfigured_as_first_reviewer(self):
        client = FakeClient(pull(number=1))
        value = normalized_config(config())
        value["reviewers"].insert(0, "keting")
        assignment = request_first(client, client.value, value, [])
        self.assertNotEqual(assignment.reviewer.lower(), "keting")

    def test_first_assignment_removes_a_pending_team_request(self):
        client = FakeClient(pull(number=1))
        client.teams = ["release-maintainers"]
        process_pull(client, client.value)
        self.assertEqual(client.teams, [])
        self.assertEqual(client.requested, ["beautyarbutin"])

    def test_removed_first_reviewer_is_reassigned(self):
        client = FakeClient(pull(number=1))
        client.requested = ["someone-new"]
        client.comments_data.append(
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"<!-- scenario-review-assignment:someone-new head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:first -->"
                ),
            }
        )
        client.next_comment = 2
        process_pull(client, client.value)
        current = latest_assignment(
            assignment_records(client.comments_data), "first", HEAD
        )
        self.assertNotEqual(current.reviewer, "someone-new")
        self.assertIn(current.reviewer, config()["reviewers"])

    def test_owner_marker_cannot_make_owner_the_first_reviewer(self):
        client = FakeClient(pull(number=1))
        client.requested = ["keting"]
        client.comments_data.append(
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "keting"},
                "body": (
                    f"<!-- scenario-review-assignment:keting head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:first -->"
                ),
            }
        )
        client.next_comment = 2
        process_pull(client, client.value)
        current = latest_assignment(
            assignment_records(client.comments_data), "first", HEAD
        )
        self.assertNotEqual(current.reviewer, "keting")

    def test_existing_assignment_found_during_recheck_prevents_duplicate_comment(self):
        class RaceClient(FakeClient):
            def __init__(self, value):
                super().__init__(value)
                self.comment_reads = 0

            def comments(self, number):
                self.comment_reads += 1
                if self.comment_reads == 2 and not self.comments_data:
                    self.requested = ["beautyarbutin"]
                    self.comments_data.append(
                        {
                            "id": 99,
                            "created_at": NOW,
                            "user": {"login": "github-actions[bot]"},
                            "body": (
                                f"<!-- scenario-review-assignment:beautyarbutin head:{HEAD} -->\n"
                                "<!-- scenario-review-stage:first -->"
                            ),
                        }
                    )
                return list(self.comments_data)

        client = RaceClient(pull(number=1))
        process_pull(client, client.value)
        assignment_comments = [
            item
            for item in client.comments_data
            if "scenario-review-assignment" in item["body"]
        ]
        self.assertEqual(len(assignment_comments), 1)

    def test_non_scenario_pull_reports_not_applicable_success(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        self.assertIsNone(process_pull(client, client.value))
        self.assertEqual(client.statuses[-1]["state"], "success")
        self.assertIn("does not apply", client.statuses[-1]["description"])
        process_pull(client, client.value)
        self.assertEqual(len(client.statuses), 1)

    def test_draft_pull_reports_pending_without_assignment(self):
        value = pull(number=1)
        value["draft"] = True
        client = FakeClient(value)
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "pending")
        self.assertEqual(client.requested, [])

    def test_main_reports_error_status_when_processing_fails(self):
        client = FakeClient(pull(number=1))
        client.fail_files = True
        with patch("scenario_review_flow.GitHubClient", return_value=client), patch.dict(
            os.environ,
            {"REPOSITORY": "aicodingresearch/agent-hi-tax", "GITHUB_TOKEN": "test"},
        ):
            with self.assertRaises(RuntimeError):
                main(["--pull-request-number", "1"])
        self.assertEqual(client.statuses[-1]["state"], "error")
        self.assertIn("file API unavailable", client.statuses[-1]["description"])

    def test_scenario_with_protocol_changes_stops_without_reassigning(self):
        client = FakeClient(pull(number=1))
        client.protocol_change = True
        client.requested = ["keting"]
        self.assertIsNone(process_pull(client, client.value))
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertEqual(client.requested, ["keting"])

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
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(second.reviewer, "keting")
        self.assertEqual(process_pull(client, client.value), "1")

    def test_second_reviewer_outside_route_is_reassigned(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        client.requested = ["black-pwq"]
        client.comments_data.append(
            {
                "id": 700,
                "created_at": "2026-09-03T09:30:00Z",
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"<!-- scenario-review-assignment:black-pwq head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:second -->"
                ),
            }
        )
        client.comment_time = "2026-09-03T10:00:00Z"
        process_pull(client, client.value)
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertIn(second.reviewer.lower(), {"keting", "ahmedalattar416"})

    def test_request_changes_keeps_first_reviewer_and_does_not_assign_second(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt", "REQUEST_CHANGES")
        self.assertIsNone(process_pull(client, client.value))
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )
        self.assertEqual(client.requested, ["beautyarbutin"])

    def test_request_changes_is_pending_even_with_wrong_model_family(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "zhipu-glm", "REQUEST_CHANGES")
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "pending")
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )

    def test_verdict_before_assignment_is_ignored(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict(
            "beautyarbutin",
            "openai-gpt",
            submitted="2026-09-03T07:00:00Z",
        )
        process_pull(client, client.value)
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )

    def test_invalid_structured_verdict_has_visible_status_reason(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        bad = verdict("beautyarbutin", "openai-gpt")
        bad["body"] = bad["body"].replace(
            "agent:openai-gpt", "human:<github-login> | agent:<model-family>"
        )
        client.comments_data.append(bad)
        process_pull(client, client.value)
        self.assertIn("verdict rejected", client.statuses[-1]["description"].lower())
        self.assertIn("canonical", client.statuses[-1]["description"].lower())

    def test_latest_invalid_attempt_replaces_an_earlier_valid_approval(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        bad = verdict(
            "beautyarbutin",
            "openai-gpt",
            verdict="REQUEST_CHANGES",
            submitted="2026-09-03T10:00:00Z",
        )
        bad["body"] = bad["body"].replace(
            "agent:openai-gpt", "agent:codex"
        )
        client.comments_data.append(bad)
        process_pull(client, client.value)
        self.assertIn("verdict rejected", client.statuses[-1]["description"].lower())
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )

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

    def test_second_privacy_verdict_stops_flow_and_clears_request(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict(
            "keting",
            "anthropic-claude",
            "PRIVACY-CONCERN-RAISED-PRIVATELY",
            submitted="2026-09-03T10:00:00Z",
        )
        process_pull(client, client.value)
        self.assertEqual(client.requested, [])
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_two_independent_approvals_request_both_maintainers(self):
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
        self.assertIn(
            "scenario-maintainer-request:beautyarbutin,xiaocooder",
            maintainer["body"].lower(),
        )
        self.assertIn("@beautyarbutin @XiaoCooder", maintainer["body"])
        self.assertEqual(client.requested, ["beautyarbutin", "XiaoCooder"])

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

    def test_first_reviewer_must_use_assigned_model_family(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "zhipu-glm")
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )

    def test_assigned_reviewer_can_submit_a_human_only_verdict(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        human = verdict("beautyarbutin", "openai-gpt")
        human["body"] = human["body"].replace(
            "Reviewer: Agent / model / high",
            "Reviewer: beautyarbutin (human-only)",
        ).replace("agent:openai-gpt", "human:beautyarbutin")
        client.comments_data.append(human)
        process_pull(client, client.value)
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertIsNotNone(second)

    def test_first_not_exposed_family_does_not_route_second_review(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "not-exposed")
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        )

    def test_removed_second_reviewer_is_reassigned(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        current = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(current.reviewer, "keting")
        revised = config()
        revised["second_reviewers"] = ["AHMEDALATTAR416"]
        revised["reviewer_capabilities"].pop("keting")
        with patch(
            "scenario_review_flow.load_config",
            return_value=normalized_config(revised),
        ):
            process_pull(client, client.value)
        reassigned = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(reassigned.reviewer.lower(), "ahmedalattar416")

    def test_production_path_calls_review_gate_evaluator(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict(
            "keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z"
        )
        with patch(
            "scenario_review_flow.evaluate_review_gate",
            return_value={"eligible": False},
        ) as gate:
            process_pull(client, client.value)
        gate.assert_called_once()
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_maintainer_author_is_excluded(self):
        client = FakeClient(pull(number=1, author="beautyarbutin"))
        process_pull(client, client.value)
        first = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        client.add_verdict(first.reviewer, "openai-gpt")
        process_pull(client, client.value)
        second = latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        client.add_verdict(
            second.reviewer,
            "anthropic-claude" if second.reviewer.lower() == "keting" else "zhipu-glm",
            submitted="2026-09-03T10:00:00Z",
        )
        process_pull(client, client.value)
        maintainer_comment = next(
            comment
            for comment in client.comments_data
            if "scenario-maintainer-request" in comment["body"]
        )
        self.assertNotIn("scenario-maintainer-request:beautyarbutin", maintainer_comment["body"])
        self.assertEqual(client.requested, ["XiaoCooder"])

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
        self.assertEqual(client.requested, [])
        maintenance = assignment_records([maintainer_comment])
        self.assertEqual(maintenance, [])

    def test_formal_approval_must_match_maintainer_and_head(self):
        request = MaintainerRequest(
            reviewers=("beautyarbutin", "XiaoCooder"),
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
        self.assertIsNone(has_formal_approval([wrong], request, HEAD))

    def test_unrequested_formal_approval_does_not_finish_maintainer_review(self):
        request = MaintainerRequest(
            reviewers=("beautyarbutin", "XiaoCooder"),
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
        )
        unrelated = {
            "state": "APPROVED",
            "submitted_at": "2026-09-03T11:00:00Z",
            "commit_id": HEAD,
            "user": {"login": "someone-else"},
        }
        self.assertIsNone(has_formal_approval([unrelated], request, HEAD))


if __name__ == "__main__":
    unittest.main()
