import base64
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scenario_review_flow import (  # noqa: E402
    Assignment,
    Capability,
    MaintainerRequest,
    allowed_assignment_families,
    assignment_supported,
    assignment_records,
    changes_protected_protocol,
    choose_candidates,
    has_formal_approval,
    index_refresh_pull,
    latest_assignment,
    main,
    non_scenario_gate,
    normalized_config,
    PROTECTED_PROTOCOL_FILES,
    PROTECTED_PROTOCOL_PREFIXES,
    process_pull,
    request_first,
    scenario_package_roots,
)
from review_gate import (  # noqa: E402
    parse_time,
    parse_verdict,
    parse_verdict_with_reason,
)


HEAD = "a" * 40
BASE = "b" * 40
NOW = "2026-09-03T08:00:00Z"


def verdict_template(path: Path) -> str:
    """Return the fenced verdict template published in a review-process page."""
    block: list[str] = []
    inside = False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("```"):
            if inside:
                if any(item.startswith("## Review verdict:") for item in block):
                    return "\n".join(block)
                block = []
            inside = not inside
            continue
        if inside:
            block.append(line)
    raise AssertionError(f"no verdict template found in {path}")


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
        self.fail_trees = False
        self.tree_shas = {HEAD: "scenario-tree-v1"}

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
        if path.startswith("/git/trees/") and path.endswith("?recursive=1"):
            if self.fail_trees:
                raise RuntimeError("tree API unavailable")
            head = path.removeprefix("/git/trees/").removesuffix("?recursive=1")
            return {
                "truncated": False,
                "tree": [
                    {
                        "path": "runs/2026-09-03/example",
                        "type": "tree",
                        "sha": self.tree_shas.get(head, f"scenario-tree-{head}"),
                    }
                ],
            }
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


class TwoPackageFakeClient(FakeClient):
    """A PR that submits two scenario packages with independent tree SHAs."""

    ROOTS = ("runs/2026-09-03/alpha", "runs/2026-09-03/beta")

    def __init__(self, value):
        super().__init__(value)
        # {head: {package root: tree sha}}
        self.package_shas = {
            HEAD: {root: f"{root}-v1" for root in self.ROOTS},
        }

    def paginate(self, path):
        if path.startswith(f"/pulls/{self.value['number']}/files"):
            return [
                {"status": "added", "filename": f"{root}/manifest.yaml"}
                for root in self.ROOTS
            ]
        raise AssertionError(path)

    def request(self, path, method="GET", payload=None):
        if path.startswith("/git/trees/") and path.endswith("?recursive=1"):
            head = path.removeprefix("/git/trees/").removesuffix("?recursive=1")
            shas = self.package_shas.get(head, {})
            return {
                "truncated": False,
                "tree": [
                    {"path": root, "type": "tree", "sha": sha}
                    for root, sha in sorted(shas.items())
                ],
            }
        return super().request(path, method=method, payload=payload)


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

    def test_review_scope_includes_every_touched_run_package(self):
        files = [
            {
                "status": "added",
                "filename": "runs/2026-09-03/new-package/manifest.yaml",
            },
            {
                "status": "modified",
                "filename": "runs/2026-08-31/existing-package/attempts/r1/result.yaml",
            },
            {
                "status": "renamed",
                "filename": "runs/2026-09-01/renamed-package/README.md",
                "previous_filename": "runs/2026-09-01/original-package/README.md",
            },
            {"status": "modified", "filename": "README.md"},
        ]
        self.assertEqual(
            scenario_package_roots(files),
            (
                "runs/2026-08-31/existing-package",
                "runs/2026-09-01/original-package",
                "runs/2026-09-01/renamed-package",
                "runs/2026-09-03/new-package",
            ),
        )

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
        value = normalized_config(config())
        legacy = Assignment(
            reviewer="keting",
            stage="second",
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
        )
        self.assertEqual(
            allowed_assignment_families(value, legacy),
            {"anthropic-claude"},
        )
        self.assertTrue(
            assignment_supported(
                value,
                legacy,
                [Capability("keting", "claude-code", "anthropic-claude")],
            )
        )
        self.assertFalse(
            assignment_supported(
                value,
                legacy,
                [Capability("keting", "workbuddy", "moonshot-kimi")],
            )
        )

    def test_assignment_capability_pin_must_match_product_and_family(self):
        value = normalized_config(config())
        candidate = [Capability("keting", "workbuddy", "moonshot-kimi")]
        exact = Assignment(
            reviewer="keting",
            stage="second",
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
            agent_product="workbuddy",
            model_family="moonshot-kimi",
        )
        wrong_product = Assignment(
            **{**exact.__dict__, "agent_product": "claude-code"}
        )
        wrong_family = Assignment(
            **{**exact.__dict__, "model_family": "anthropic-claude"}
        )
        self.assertTrue(assignment_supported(value, exact, candidate))
        self.assertFalse(assignment_supported(value, wrong_product, candidate))
        self.assertFalse(assignment_supported(value, wrong_family, candidate))

    def test_config_rejects_noncanonical_model_family(self):
        value = config()
        value["reviewer_capabilities"]["black-pwq"][0]["model_family"] = "deepseek"
        with self.assertRaisesRegex(RuntimeError, "invalid model_family"):
            normalized_config(value)

    def test_config_allows_maintainers_in_structured_reviewer_pools(self):
        value = config()
        normalized = normalized_config(value)
        self.assertIn("beautyarbutin", normalized["reviewers"])
        self.assertIn("XiaoCooder", normalized["reviewers"])
        self.assertIn("beautyarbutin", normalized["maintainers"])

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

    def test_non_scenario_pull_without_an_approval_is_refused(self):
        # The ruleset no longer requires an approving review, so review-gate is
        # what stops an unreviewed change now.
        client = FakeClient(pull(number=1))
        client.scenario = False
        self.assertIsNone(process_pull(client, client.value))
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIn("maintainer", client.statuses[-1]["description"])

    def test_non_scenario_pull_with_a_maintainer_approval_passes(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}}
        )
        self.assertIsNone(process_pull(client, client.value))
        self.assertEqual(client.statuses[-1]["state"], "success")
        process_pull(client, client.value)
        self.assertEqual(len(client.statuses), 1)

    def test_an_approval_of_an_earlier_commit_does_not_carry(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": "0" * 40, "user": {"login": "XiaoCooder"}}
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_the_author_cannot_approve_their_own_change(self):
        client = FakeClient(pull(number=1, author="XiaoCooder"))
        client.scenario = False
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}}
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_a_non_maintainer_approval_is_not_enough(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "black-pwq"}}
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")

    def test_protocol_changes_need_a_code_owner_as_author_or_approver(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        client.protocol_change = True
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}}
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIn("code owner", client.statuses[-1]["description"])

    def test_a_code_owner_authored_protocol_change_needs_only_a_maintainer(self):
        # The single code owner is usually the author of protocol changes, and
        # GitHub never lets an author approve their own pull request. Requiring
        # an owner *approval* would make those unmergeable, so authorship by an
        # owner counts, and a non-author maintainer still has to approve.
        client = FakeClient(pull(number=1, author="keting"))
        client.scenario = False
        client.protocol_change = True
        client.reviews_data.append(
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}}
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "success")

    def test_a_code_owner_approval_unlocks_a_contributor_protocol_change(self):
        client = FakeClient(pull(number=1))
        client.scenario = False
        client.protocol_change = True
        client.reviews_data.extend(
            [
                {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "keting"}},
                {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}},
            ]
        )
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "success")

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

    def test_glm_first_approval_assigns_highest_priority_codex_reviewer(self):
        client = FakeClient(pull(number=3))
        process_pull(client, client.value)
        first = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        self.assertEqual(first.reviewer.lower(), "ahmedalattar416")
        client.add_verdict("AHMEDALATTAR416", "zhipu-glm")
        self.assertIsNone(process_pull(client, client.value))
        second = latest_assignment(assignment_records(client.comments_data), "second", HEAD)
        self.assertEqual(second.reviewer, "beautyarbutin")
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

    def test_assigned_read_reviewer_is_accepted_when_actions_hides_association(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        client.comments_data[-1]["author_association"] = "NONE"

        self.assertEqual(process_pull(client, client.value), "1")
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(second.reviewer, "keting")

        client.add_verdict(
            "keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z"
        )
        process_pull(client, client.value)
        self.assertEqual(client.requested, ["beautyarbutin", "XiaoCooder"])
        maintainer_approval = {
            "id": 500,
            "state": "APPROVED",
            "submitted_at": "2026-09-03T12:00:00Z",
            "commit_id": HEAD,
            "user": {"login": "XiaoCooder"},
        }
        client.reviews_data.append(maintainer_approval)
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "success")

    def test_openai_second_reviewer_priority_does_not_rotate(self):
        client = FakeClient(pull(number=2))
        process_pull(client, client.value)
        client.add_verdict("XiaoCooder", "openai-gpt")
        self.assertEqual(process_pull(client, client.value), "2")
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertEqual(second.reviewer, "keting")

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

    def test_approved_first_review_is_carried_when_scenario_content_is_unchanged(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T10:00:00Z"

        self.assertEqual(process_pull(client, client.value), "1")

        carried = [
            item["body"]
            for item in client.comments_data
            if "scenario-review-carried:beautyarbutin" in item["body"]
        ]
        self.assertEqual(len(carried), 1)
        self.assertIn(f"reviewed-head:{HEAD} head:{new_head}", carried[0])
        self.assertIn("No reviewer action is required", carried[0])
        self.assertNotIn("@beautyarbutin", carried[0])
        self.assertFalse(
            any("Scenario re-review requested" in item["body"] for item in client.comments_data)
        )
        second = latest_assignment(
            assignment_records(client.comments_data), "second", new_head
        )
        self.assertEqual(second.reviewer, "keting")
        self.assertEqual(client.requested, ["keting"])

    def test_existing_re_review_request_is_retired_when_old_approval_still_covers_content(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.comment_time = "2026-09-03T10:00:00Z"
        process_pull(client, client.value)
        self.assertIn("Scenario re-review requested", client.comments_data[-1]["body"])

        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T11:00:00Z"
        self.assertEqual(process_pull(client, client.value), "1")

        self.assertEqual(client.requested, ["keting"])
        self.assertEqual(
            sum(
                "scenario-review-carried:beautyarbutin" in item["body"]
                for item in client.comments_data
            ),
            1,
        )

    def test_approval_requires_re_review_when_scenario_content_changes(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        client.value["head"]["sha"] = "c" * 40
        client.comment_time = "2026-09-03T10:00:00Z"

        process_pull(client, client.value)

        self.assertIn("Scenario re-review requested", client.comments_data[-1]["body"])
        self.assertEqual(client.requested, ["beautyarbutin"])
        self.assertFalse(
            any("scenario-review-carried:" in item["body"] for item in client.comments_data)
        )

    def test_two_approvals_are_carried_to_unchanged_scenario_content(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict(
            "keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z"
        )
        process_pull(client, client.value)

        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T11:00:00Z"
        process_pull(client, client.value)

        carried = [
            item for item in client.comments_data if "scenario-review-carried:" in item["body"]
        ]
        self.assertEqual(len(carried), 2)
        self.assertEqual(client.requested, ["beautyarbutin", "XiaoCooder"])
        self.assertEqual(client.statuses[-1]["state"], "pending")
        maintainer_approval = {
            "id": 500,
            "state": "APPROVED",
            "submitted_at": "2026-09-03T12:00:00Z",
            "commit_id": new_head,
            "user": {"login": "XiaoCooder"},
        }
        client.reviews_data.append(maintainer_approval)
        process_pull(client, client.value)
        self.assertEqual(client.statuses[-1]["state"], "success")
        self.assertIn("maintainer approval", client.statuses[-1]["description"])

        before = len(client.comments_data)
        process_pull(client, client.value)
        self.assertEqual(len(client.comments_data), before)

    def test_approval_is_not_carried_when_any_submitted_package_changed(self):
        client = TwoPackageFakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")

        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        # alpha is byte-for-byte unchanged; beta changed. One unchanged package
        # must never be enough to carry an approval over the whole submission.
        client.package_shas[new_head] = {
            "runs/2026-09-03/alpha": "runs/2026-09-03/alpha-v1",
            "runs/2026-09-03/beta": "runs/2026-09-03/beta-v2",
        }
        client.comment_time = "2026-09-03T10:00:00Z"

        process_pull(client, client.value)

        self.assertFalse(
            any("scenario-review-carried" in item["body"] for item in client.comments_data)
        )
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", new_head)
        )
        self.assertFalse(
            any("scenario-review-stage:second" in item["body"] for item in client.comments_data)
        )
        self.assertIn("Scenario re-review requested", client.comments_data[-1]["body"])
        self.assertEqual(client.requested, ["beautyarbutin"])
        self.assertEqual(client.statuses[-1]["state"], "pending")
        self.assertIn(
            "Waiting for first verdict from @beautyarbutin",
            client.statuses[-1]["description"],
        )

    def test_approval_is_not_carried_to_a_different_assigned_reviewer(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")

        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        # The owner reassigns the first review to somebody else at the new head.
        client.comments_data.append(
            {
                "id": 700,
                "created_at": "2026-09-03T09:45:00Z",
                "user": {"login": "keting"},
                "body": (
                    f"<!-- scenario-review-assignment:leonadoor head:{new_head} -->\n"
                    "<!-- scenario-review-stage:first -->\n"
                    "<!-- scenario-review-capability:codex model-family:openai-gpt -->"
                ),
            }
        )
        client.comment_time = "2026-09-03T10:00:00Z"

        process_pull(client, client.value)

        self.assertFalse(
            any("scenario-review-carried" in item["body"] for item in client.comments_data)
        )
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", new_head)
        )
        self.assertFalse(
            any("scenario-review-stage:second" in item["body"] for item in client.comments_data)
        )
        self.assertEqual(
            latest_assignment(
                assignment_records(client.comments_data), "first", new_head
            ).reviewer,
            "leonadoor",
        )
        self.assertEqual(client.requested, ["leonadoor"])
        self.assertEqual(client.statuses[-1]["state"], "pending")
        self.assertIn(
            "Waiting for first verdict from @leonadoor",
            client.statuses[-1]["description"],
        )

    def test_request_changes_is_never_carried_as_an_approval(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt", "REQUEST_CHANGES")
        process_pull(client, client.value)

        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T10:00:00Z"

        process_pull(client, client.value)

        self.assertFalse(
            any("scenario-review-carried" in item["body"] for item in client.comments_data)
        )
        self.assertIsNone(
            latest_assignment(assignment_records(client.comments_data), "second", new_head)
        )
        self.assertFalse(
            any("scenario-review-stage:second" in item["body"] for item in client.comments_data)
        )
        self.assertIn("Scenario re-review requested", client.comments_data[-1]["body"])
        self.assertEqual(client.requested, ["beautyarbutin"])
        self.assertNotEqual(client.statuses[-1]["state"], "success")
        self.assertEqual(client.statuses[-1]["state"], "pending")

    def test_privacy_verdict_remains_visible_after_head_changes(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict(
            "beautyarbutin", "openai-gpt", "PRIVACY-CONCERN-RAISED-PRIVATELY"
        )
        process_pull(client, client.value)
        client.value["head"]["sha"] = "c" * 40
        client.comment_time = "2026-09-03T10:00:00Z"

        process_pull(client, client.value)

        self.assertEqual(client.requested, [])
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIn("remains unresolved", client.statuses[-1]["description"])
        self.assertIsNone(
            latest_assignment(
                assignment_records(client.comments_data), "first", "c" * 40
            )
        )

    def test_legacy_assignment_privacy_verdict_remains_visible_after_head_changes(self):
        client = FakeClient(pull(number=1))
        client.comments_data.append(
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "keting"},
                "body": "<!-- scenario-review-assignment:black-pwq -->",
            }
        )
        client.next_comment = 2
        client.add_verdict(
            "black-pwq", "openai-gpt", "PRIVACY-CONCERN-RAISED-PRIVATELY"
        )
        client.value["head"]["sha"] = "c" * 40

        process_pull(client, client.value)

        self.assertEqual(client.requested, [])
        self.assertEqual(client.statuses[-1]["state"], "failure")
        self.assertIn("remains unresolved", client.statuses[-1]["description"])

    def test_legacy_assignment_approval_can_be_carried_from_declared_head(self):
        client = FakeClient(pull(number=1))
        client.comments_data.append(
            {
                "id": 1,
                "created_at": NOW,
                "user": {"login": "keting"},
                "body": "<!-- scenario-review-assignment:beautyarbutin -->",
            }
        )
        client.next_comment = 2
        client.add_verdict("beautyarbutin", "openai-gpt")
        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T10:00:00Z"

        self.assertEqual(process_pull(client, client.value), "1")

        self.assertTrue(
            any(
                f"reviewed-head:{HEAD} head:{new_head}" in item["body"]
                for item in client.comments_data
            )
        )
        self.assertEqual(client.requested, ["keting"])

    def test_tree_lookup_failure_does_not_issue_a_re_review_request(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        client.value["head"]["sha"] = "c" * 40
        client.fail_trees = True

        with self.assertRaisesRegex(RuntimeError, "tree API unavailable"):
            process_pull(client, client.value)

        self.assertEqual(client.requested, ["beautyarbutin"])
        self.assertIsNone(
            latest_assignment(
                assignment_records(client.comments_data), "first", "c" * 40
            )
        )

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
        # Both maintainers are invited, but the check waits for one of them.
        self.assertEqual(client.statuses[-1]["state"], "pending")
        self.assertIn("maintainer", client.statuses[-1]["description"])
        maintainer_approval = {
            "id": 500,
            "state": "APPROVED",
            "submitted_at": "2026-09-03T12:00:00Z",
            "commit_id": HEAD,
            "user": {"login": "XiaoCooder"},
        }
        client.reviews_data.append(maintainer_approval)
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
        # Once one of them approves, only the other one's request is retired.
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
        client.requested.remove("XiaoCooder")
        client.requested.append("manual-reviewer")
        client.teams = ["manual-team"]
        before = len(client.request_history)
        process_pull(client, client.value)
        self.assertEqual(len(client.request_history), before)
        self.assertEqual(client.requested, ["manual-reviewer"])
        self.assertEqual(client.teams, ["manual-team"])
        maintenance = assignment_records([maintainer_comment])
        self.assertEqual(maintenance, [])

    def test_config_change_does_not_invalidate_existing_maintainer_approval(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict(
            "keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z"
        )
        process_pull(client, client.value)
        client.reviews_data.append(
            {
                "state": "APPROVED",
                "submitted_at": "2026-09-03T11:00:00Z",
                "commit_id": HEAD,
                "user": {"login": "XiaoCooder"},
            }
        )
        client.requested.remove("XiaoCooder")
        before_requests = len(client.request_history)
        before_markers = sum(
            "scenario-maintainer-request" in comment["body"]
            for comment in client.comments_data
        )
        revised = config()
        revised["maintainers"] = ["beautyarbutin"]
        with patch(
            "scenario_review_flow.load_config",
            return_value=normalized_config(revised),
        ):
            process_pull(client, client.value)
        self.assertEqual(client.requested, [])
        self.assertEqual(len(client.request_history), before_requests)
        self.assertEqual(
            sum(
                "scenario-maintainer-request" in comment["body"]
                for comment in client.comments_data
            ),
            before_markers,
        )

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

    def test_earliest_eligible_maintainer_approval_wins(self):
        request = MaintainerRequest(
            reviewers=("beautyarbutin", "XiaoCooder"),
            head=HEAD,
            created_at=parse_time(NOW),
            comment_id=1,
        )
        reviews = [
            {
                "id": 2,
                "state": "APPROVED",
                "submitted_at": "2026-09-03T12:00:00Z",
                "commit_id": HEAD,
                "user": {"login": "XiaoCooder"},
            },
            {
                "id": 1,
                "state": "APPROVED",
                "submitted_at": "2026-09-03T11:00:00Z",
                "commit_id": HEAD,
                "user": {"login": "beautyarbutin"},
            },
        ]
        self.assertEqual(has_formal_approval(reviews, request, HEAD), "beautyarbutin")

    def _approved_first_review(self, number=1):
        client = FakeClient(pull(number=number))
        process_pull(client, client.value)
        first = latest_assignment(
            assignment_records(client.comments_data), "first", HEAD
        )
        client.add_verdict(first.reviewer, first.model_family)
        process_pull(client, client.value)
        return client, first

    def _reply(self, login, body, comment_id, submitted="2026-09-03T12:00:00Z"):
        return {
            "id": comment_id,
            "html_url": "https://example.test/reply",
            "author_association": "MEMBER",
            "created_at": submitted,
            "user": {"login": login},
            "body": body,
        }

    def test_inline_verdict_mention_does_not_supersede_a_published_verdict(self):
        client, first = self._approved_first_review()
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        self.assertIsNotNone(second)
        client.comments_data.append(
            self._reply(
                first.reviewer,
                "Answering the author: my `## Review verdict:` is already in the "
                "comment above, so I am not posting it twice.",
                7001,
            )
        )
        process_pull(client, client.value)
        self.assertNotIn("First verdict rejected", client.statuses[-1]["description"])
        self.assertEqual(
            latest_assignment(
                assignment_records(client.comments_data), "second", HEAD
            ).reviewer,
            second.reviewer,
        )

    def test_quoted_verdict_heading_does_not_supersede_a_published_verdict(self):
        client, first = self._approved_first_review()
        client.comments_data.append(
            self._reply(
                first.reviewer,
                "Quoting my earlier comment for the author:\n\n"
                "> ## Review verdict: APPROVE\n>\n> Reviewed at head: deadbeef\n",
                7002,
            )
        )
        process_pull(client, client.value)
        self.assertNotIn("First verdict rejected", client.statuses[-1]["description"])

    def test_new_verdict_heading_still_supersedes_a_published_verdict(self):
        client, first = self._approved_first_review()
        stale = verdict(first.reviewer, "openai-gpt")
        stale["id"] = 7003
        stale["created_at"] = "2026-09-03T12:00:00Z"
        stale["body"] = stale["body"].replace(
            f"Reviewed at head: {HEAD}", "Reviewed at head: " + "c" * 40
        )
        client.comments_data.append(stale)
        process_pull(client, client.value)
        self.assertIn("First verdict rejected", client.statuses[-1]["description"])

    def test_maintainer_removed_from_config_is_reassigned(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        client.add_verdict(
            "keting", "anthropic-claude", submitted="2026-09-03T10:00:00Z"
        )
        process_pull(client, client.value)
        first_marker = next(
            comment
            for comment in client.comments_data
            if "scenario-maintainer-request" in comment["body"]
        )
        self.assertIn("beautyarbutin,xiaocooder", first_marker["body"])
        revised = config()
        revised["maintainers"] = ["XiaoCooder"]
        with patch(
            "scenario_review_flow.load_config",
            return_value=normalized_config(revised),
        ):
            process_pull(client, client.value)
        markers = [
            comment["body"]
            for comment in client.comments_data
            if "scenario-maintainer-request" in comment["body"]
        ]
        self.assertEqual(len(markers), 2)
        self.assertIn("scenario-maintainer-request:xiaocooder ", markers[-1])
        self.assertEqual(client.requested, ["XiaoCooder"])

    def test_shipped_verdict_template_cannot_be_pasted_as_a_verdict(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("docs/review-process.md", "docs/review-process.zh-CN.md"):
            with self.subTest(document=name):
                template = verdict_template(root / name)
                self.assertIn("## Review verdict:", template)
                # Fill only the placeholders a copier would naturally replace.
                body = template.replace("<template commit>", "abcdef1").replace(
                    "<commit SHA>", HEAD
                )
                parsed, reason = parse_verdict_with_reason(
                    {
                        "id": 1,
                        "author_association": "MEMBER",
                        "created_at": NOW,
                        "user": {"login": "black-pwq"},
                        "body": body,
                    },
                    HEAD,
                )
                self.assertIsNone(parsed)
                self.assertIn("Review verdict", reason)


class ReviewFlowWorkflowTests(unittest.TestCase):
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github/workflows/scenario-review-flow.yml"
    ).read_text(encoding="utf-8")

    def test_notification_step_runs_even_after_a_partial_failure(self):
        self.assertIn(
            "if: always() && steps.flow.outputs.notify_prs != ''", self.workflow
        )

    def test_notification_step_reads_the_output_the_script_writes(self):
        script = (
            Path(__file__).resolve().parents[1] / "scripts/scenario_review_flow.py"
        ).read_text(encoding="utf-8")
        self.assertIn('write_output("notify_prs"', script)
        self.assertIn("NOTIFY_PRS: ${{ steps.flow.outputs.notify_prs }}", self.workflow)

    def test_workflow_only_checks_out_trusted_main(self):
        self.assertIn("ref: main", self.workflow)
        self.assertNotIn("github.event.pull_request.head", self.workflow)

    def test_comment_trigger_is_limited_to_verdict_shaped_comments(self):
        self.assertIn(
            "contains(github.event.comment.body, '## Review verdict:')", self.workflow
        )

    def test_workflow_uses_one_global_serialization_group(self):
        self.assertIn("group: scenario-review-flow\n", self.workflow)
        self.assertIn("cancel-in-progress: false", self.workflow)


class NotifyOutputTests(unittest.TestCase):
    def _run_main(self, client):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "github_output"
            output_path.write_text("", encoding="utf-8")
            with patch(
                "scenario_review_flow.GitHubClient", return_value=client
            ), patch.dict(
                os.environ,
                {
                    "REPOSITORY": "aicodingresearch/agent-hi-tax",
                    "GITHUB_TOKEN": "test",
                    "GITHUB_OUTPUT": str(output_path),
                },
            ):
                main(["--pull-request-number", str(client.value["number"])])
            return output_path.read_text(encoding="utf-8")

    def test_owner_second_assignment_publishes_the_notify_output(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        self.assertIn("notify_prs=1\n", self._run_main(client))

    def test_owner_reassignment_publishes_the_notify_output(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        client.comments_data.append(
            {
                "id": 7100,
                "created_at": "2026-09-03T09:30:00Z",
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"<!-- scenario-review-assignment:keting head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:second -->\n"
                    "<!-- scenario-review-capability:workbuddy model-family:moonshot-kimi -->"
                ),
            }
        )
        self.assertIn("notify_prs=1\n", self._run_main(client))

    def test_owner_still_publishes_the_notify_output_while_a_verdict_is_pending(self):
        client = FakeClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt")
        process_pull(client, client.value)
        self.assertEqual(
            latest_assignment(
                assignment_records(client.comments_data), "second", HEAD
            ).reviewer,
            "keting",
        )
        self.assertIn("notify_prs=1\n", self._run_main(client))

    def test_first_review_stage_publishes_an_empty_notify_output(self):
        client = FakeClient(pull(number=1))
        self.assertIn("notify_prs=\n", self._run_main(client))



REPO = "aicodingresearch/agent-hi-tax"


def refresh_pull(**overrides):
    """The standing results-index refresh pull request."""
    value = {
        "number": 93,
        "state": "open",
        "draft": False,
        "user": {"login": "keting"},
        "head": {
            "ref": "chore/refresh-results-index",
            "sha": HEAD,
            "repo": {"full_name": REPO},
        },
        "base": {"ref": "main", "repo": {"full_name": REPO}},
    }
    value.update(overrides)
    return value


INDEX_FILES = [
    {"filename": "RESULTS.md", "status": "modified"},
    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
]


class IndexRefreshExemptionTests(unittest.TestCase):
    """The one exemption from "a maintainer must approve", and its edges."""

    def setUp(self):
        self.config = normalized_config(config())

    def gate(self, pull_value, files, reviews=()):
        return non_scenario_gate(self.config, pull_value, files, list(reviews))

    def test_the_refresh_pull_request_needs_no_approval(self):
        self.assertTrue(index_refresh_pull(refresh_pull(), INDEX_FILES))
        eligible, reason = self.gate(refresh_pull(), INDEX_FILES)
        self.assertTrue(eligible)
        self.assertIn("results index", reason)

    def test_another_branch_carrying_the_same_files_is_not_exempt(self):
        value = refresh_pull()
        value["head"]["ref"] = "chore/refresh-results-index-2"
        self.assertFalse(index_refresh_pull(value, INDEX_FILES))
        self.assertFalse(self.gate(value, INDEX_FILES)[0])

    def test_a_fork_branch_of_the_same_name_is_not_exempt(self):
        value = refresh_pull()
        value["head"]["repo"] = {"full_name": "someone-else/agent-hi-tax"}
        self.assertFalse(index_refresh_pull(value, INDEX_FILES))

    def test_a_deleted_head_repository_is_not_exempt(self):
        value = refresh_pull()
        value["head"]["repo"] = None
        self.assertFalse(index_refresh_pull(value, INDEX_FILES))

    def test_another_base_branch_is_not_exempt(self):
        value = refresh_pull()
        value["base"] = {"ref": "release", "repo": {"full_name": REPO}}
        self.assertFalse(index_refresh_pull(value, INDEX_FILES))

    def test_one_extra_file_removes_the_exemption(self):
        files = INDEX_FILES + [{"filename": "scripts/x.py", "status": "modified"}]
        self.assertFalse(index_refresh_pull(refresh_pull(), files))
        eligible, reason = self.gate(refresh_pull(), files)
        self.assertFalse(eligible)
        self.assertIn("maintainer", reason)

    def test_an_extra_file_from_a_non_owner_needs_the_code_owner(self):
        files = INDEX_FILES + [{"filename": "scripts/x.py", "status": "modified"}]
        eligible, reason = self.gate(
            refresh_pull(user={"login": "someone-else"}), files
        )
        self.assertFalse(eligible)
        self.assertIn("code owner", reason)

    def test_a_missing_index_page_removes_the_exemption(self):
        self.assertFalse(index_refresh_pull(refresh_pull(), INDEX_FILES[:1]))

    def test_an_empty_change_set_is_not_exempt(self):
        self.assertFalse(index_refresh_pull(refresh_pull(), []))

    def test_an_added_or_removed_page_removes_the_exemption(self):
        for status in ("added", "removed", "renamed"):
            files = [
                {"filename": "RESULTS.md", "status": status},
                {"filename": "RESULTS.zh-CN.md", "status": "modified"},
            ]
            self.assertFalse(index_refresh_pull(refresh_pull(), files), status)

    def test_a_lookalike_path_removes_the_exemption(self):
        files = [
            {"filename": "docs/RESULTS.md", "status": "modified"},
            {"filename": "RESULTS.zh-CN.md", "status": "modified"},
        ]
        self.assertFalse(index_refresh_pull(refresh_pull(), files))

    def test_the_exemption_does_not_depend_on_who_opened_it(self):
        for author in ("keting", "results-index[bot]", "someone-else"):
            value = refresh_pull(user={"login": author})
            self.assertTrue(index_refresh_pull(value, INDEX_FILES), author)

    def test_a_head_that_cannot_be_read_is_refused(self):
        value = refresh_pull()
        value["head"] = {"ref": "feature", "sha": "", "repo": {"full_name": REPO}}
        eligible, reason = self.gate(value, [{"filename": "a.md", "status": "modified"}])
        self.assertFalse(eligible)
        self.assertIn("could not be read", reason)

class ProtectedPathEscapeTests(unittest.TestCase):
    """A change set must not be judged on where a file landed."""

    def setUp(self):
        self.config = normalized_config(config())
        self.approval = [
            {"state": "APPROVED", "commit_id": HEAD, "user": {"login": "XiaoCooder"}}
        ]

    def test_renaming_a_protected_file_out_of_its_directory_still_counts(self):
        files = [
            {
                "filename": "tools/merge_group_gate.py",
                "previous_filename": "scripts/merge_group_gate.py",
                "status": "renamed",
            }
        ]
        self.assertTrue(changes_protected_protocol(files))
        eligible, reason = non_scenario_gate(
            self.config, refresh_pull(user={"login": "someone-else"}), files, self.approval
        )
        self.assertFalse(eligible)
        self.assertIn("code owner", reason)

    def test_renaming_a_file_into_a_protected_directory_also_counts(self):
        files = [
            {
                "filename": "scripts/new_gate.py",
                "previous_filename": "notes/new_gate.py",
                "status": "renamed",
            }
        ]
        self.assertTrue(changes_protected_protocol(files))

    def test_an_ordinary_rename_is_still_unprotected(self):
        files = [
            {
                "filename": "docs/b.md",
                "previous_filename": "docs/a.md",
                "status": "renamed",
            }
        ]
        self.assertFalse(changes_protected_protocol(files))

    def test_a_change_set_too_large_to_list_is_refused(self):
        files = [
            {"filename": f"runs/2026-09-03/p{index}/manifest.yaml", "status": "added"}
            for index in range(3000)
        ]
        eligible, reason = non_scenario_gate(
            self.config, refresh_pull(), files, self.approval
        )
        self.assertFalse(eligible)
        self.assertIn("Too many files", reason)

    def test_a_change_set_just_under_the_cap_is_still_judged(self):
        files = [
            {"filename": f"docs/n{index}.md", "status": "modified"}
            for index in range(2999)
        ]
        eligible, _ = non_scenario_gate(
            self.config, refresh_pull(), files, self.approval
        )
        self.assertTrue(eligible)


if __name__ == "__main__":
    unittest.main()
