import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from merge_group_gate import (  # noqa: E402
    GateFailure,
    base_branch_name,
    evaluate_pull,
    group_commits,
    main,
    maintainer_approved,
    queue_entries_by_commit,
    source_pull_requests,
)
from scenario_review_flow import normalized_config  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_scenario_review_flow import (  # noqa: E402
    FakeClient,
    config,
    pull,
    verdict,
    HEAD,
)


MAIN_TIP = "1" * 40
GROUP_A = "a" * 40
GROUP_B = "b" * 40
PR_A_HEAD = "4" * 40
PR_B_HEAD = "5" * 40


def commit(sha, parents):
    return {"sha": sha, "parents": [{"sha": item} for item in parents]}


def entry(position, group_sha, number, head, state="AWAITING_CHECKS"):
    return {
        "position": position,
        "state": state,
        "headCommit": {"oid": group_sha},
        "baseCommit": {"oid": MAIN_TIP},
        "pullRequest": {"number": number, "headRefOid": head},
    }


class TopologyClient:
    """Serves the commit topology a real merge group produces."""

    def __init__(self, commits=None, tip=MAIN_TIP):
        self.tip = tip
        self.commits = commits if commits is not None else {
            GROUP_A: commit(GROUP_A, [MAIN_TIP, PR_A_HEAD]),
            GROUP_B: commit(GROUP_B, [GROUP_A, PR_B_HEAD]),
        }

    def request(self, path, method="GET", payload=None):
        if path == "/commits/main":
            return {"sha": self.tip}
        if path.startswith("/commits/"):
            sha = path.removeprefix("/commits/")
            if sha not in self.commits:
                raise RuntimeError(f"unknown commit {sha}")
            return self.commits[sha]
        raise AssertionError(path)


class MergeGroupTopologyTests(unittest.TestCase):
    def test_base_ref_is_reduced_to_a_branch_name(self):
        self.assertEqual(base_branch_name("refs/heads/main"), "main")
        self.assertEqual(base_branch_name("main"), "main")

    def test_first_parent_walk_finds_every_queued_pull_request(self):
        chain = group_commits(TopologyClient(), GROUP_B, MAIN_TIP)
        self.assertEqual(chain, [(GROUP_A, PR_A_HEAD), (GROUP_B, PR_B_HEAD)])

    def test_single_entry_group_yields_one_pull_request(self):
        chain = group_commits(TopologyClient(), GROUP_A, MAIN_TIP)
        self.assertEqual(chain, [(GROUP_A, PR_A_HEAD)])

    def test_chain_that_never_reaches_the_base_tip_fails_closed(self):
        commits = {GROUP_A: commit(GROUP_A, [GROUP_A, PR_A_HEAD])}
        with self.assertRaises(GateFailure):
            group_commits(TopologyClient(commits), GROUP_A, MAIN_TIP)

    def test_commit_without_two_parents_fails_closed(self):
        commits = {GROUP_A: commit(GROUP_A, [MAIN_TIP])}
        with self.assertRaises(GateFailure):
            group_commits(TopologyClient(commits), GROUP_A, MAIN_TIP)


class SourcePullRequestTests(unittest.TestCase):
    def resolve(self, entries):
        with patch(
            "merge_group_gate.queue_entries_by_commit",
            return_value={item["headCommit"]["oid"].lower(): item for item in entries},
        ):
            return source_pull_requests(
                TopologyClient(), "token", "o/r", GROUP_B, "refs/heads/main"
            )

    def test_every_commit_is_mapped_to_its_pull_request(self):
        resolved = self.resolve(
            [entry(1, GROUP_A, 11, PR_A_HEAD), entry(2, GROUP_B, 22, PR_B_HEAD)]
        )
        self.assertEqual(
            resolved,
            [{"number": 11, "head": PR_A_HEAD}, {"number": 22, "head": PR_B_HEAD}],
        )

    def test_missing_queue_entry_fails_closed(self):
        with self.assertRaises(GateFailure):
            self.resolve([entry(2, GROUP_B, 22, PR_B_HEAD)])

    def test_entry_without_a_pull_request_fails_closed(self):
        broken = entry(1, GROUP_A, 11, PR_A_HEAD)
        broken["pullRequest"] = None
        with self.assertRaises(GateFailure):
            self.resolve([broken, entry(2, GROUP_B, 22, PR_B_HEAD)])

    def test_head_changed_after_enqueue_fails_closed(self):
        with self.assertRaises(GateFailure):
            self.resolve(
                [
                    entry(1, GROUP_A, 11, "9" * 40),
                    entry(2, GROUP_B, 22, PR_B_HEAD),
                ]
            )

    def test_unreadable_merge_queue_fails_closed(self):
        with patch(
            "merge_group_gate.graphql",
            return_value={"data": {"repository": {"mergeQueue": None}}},
        ):
            with self.assertRaises(GateFailure):
                queue_entries_by_commit("token", "o/r", "main")

    def test_configuration_permission_error_is_tolerated(self):
        response = {
            "data": {
                "repository": {
                    "mergeQueue": {
                        "entries": {"nodes": [entry(1, GROUP_A, 11, PR_A_HEAD)]}
                    }
                }
            },
            "errors": [
                {
                    "path": ["repository", "mergeQueue", "configuration"],
                    "message": "Resource not accessible by integration",
                }
            ],
        }
        with patch("merge_group_gate.graphql", return_value=response):
            mapping = queue_entries_by_commit("token", "o/r", "main")
        self.assertEqual(list(mapping), [GROUP_A])

    def test_permission_error_on_entries_fails_closed(self):
        response = {
            "data": {"repository": {"mergeQueue": {"entries": None}}},
            "errors": [
                {
                    "path": ["repository", "mergeQueue", "entries"],
                    "message": "Resource not accessible by integration",
                }
            ],
        }
        with patch("merge_group_gate.graphql", return_value=response):
            with self.assertRaises(GateFailure):
                queue_entries_by_commit("token", "o/r", "main")


class GateClient(FakeClient):
    """A pull request client that also answers `client.pull(number)`."""

    def pull(self, number):
        return self.value


def approved_maintainer_review(head=HEAD, login="XiaoCooder"):
    return {
        "id": 1,
        "state": "APPROVED",
        "submitted_at": "2026-09-03T12:00:00Z",
        "commit_id": head,
        "user": {"login": login},
    }


class EvaluatePullTests(unittest.TestCase):
    def setUp(self):
        self.config = normalized_config(config())

    def two_approvals(self, number=1, author="contributor"):
        from scenario_review_flow import (
            assignment_records,
            latest_assignment,
            process_pull,
        )

        client = GateClient(pull(number=number, author=author))
        process_pull(client, client.value)
        first = latest_assignment(assignment_records(client.comments_data), "first", HEAD)
        client.add_verdict(first.reviewer, first.model_family)
        process_pull(client, client.value)
        second = latest_assignment(
            assignment_records(client.comments_data), "second", HEAD
        )
        client.add_verdict(
            second.reviewer, second.model_family, submitted="2026-09-03T10:00:00Z"
        )
        process_pull(client, client.value)
        client.statuses.clear()
        return client

    def test_two_approvals_plus_maintainer_approval_pass(self):
        client = self.two_approvals()
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertTrue(ok, reason)
        self.assertEqual(client.statuses, [])

    def test_missing_maintainer_approval_fails(self):
        client = self.two_approvals()
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("maintainer", reason)

    def test_author_maintainer_approval_does_not_count(self):
        client = self.two_approvals(author="XiaoCooder")
        client.reviews_data.append(approved_maintainer_review(login="XiaoCooder"))
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("maintainer", reason)

    def test_maintainer_approval_of_an_older_head_does_not_count(self):
        client = self.two_approvals()
        client.reviews_data.append(approved_maintainer_review(head="9" * 40))
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)

    def test_carried_approval_over_unchanged_packages_passes(self):
        from scenario_review_flow import (
            assignment_records,
            latest_assignment,
            process_pull,
        )

        client = GateClient(pull(number=1))
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
        client.reviews_data.append(approved_maintainer_review(head=new_head))
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertTrue(ok, reason)
        self.assertIsNotNone(
            latest_assignment(
                assignment_records(client.comments_data), "second", new_head
            )
        )

    def test_changed_package_content_fails(self):
        client = self.two_approvals()
        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.comment_time = "2026-09-03T11:00:00Z"
        client.reviews_data.append(approved_maintainer_review(head=new_head))
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)

    def test_request_changes_fails(self):
        from scenario_review_flow import process_pull

        client = GateClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict("beautyarbutin", "openai-gpt", "REQUEST_CHANGES")
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("REQUEST_CHANGES", reason)

    def test_privacy_verdict_fails(self):
        from scenario_review_flow import process_pull

        client = GateClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict(
            "beautyarbutin", "openai-gpt", "PRIVACY-CONCERN-RAISED-PRIVATELY"
        )
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("privacy", reason)

    def test_privacy_verdict_from_an_older_head_still_fails(self):
        from scenario_review_flow import process_pull

        client = GateClient(pull(number=1))
        process_pull(client, client.value)
        client.add_verdict(
            "beautyarbutin", "openai-gpt", "PRIVACY-CONCERN-RAISED-PRIVATELY"
        )
        new_head = "c" * 40
        client.value["head"]["sha"] = new_head
        client.tree_shas[new_head] = client.tree_shas[HEAD]
        client.comment_time = "2026-09-03T11:00:00Z"
        client.reviews_data.append(approved_maintainer_review(head=new_head))
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("privacy", reason)

    def test_non_scenario_pull_request_is_not_applicable(self):
        client = GateClient(pull(number=1))
        client.scenario = False
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertTrue(ok)
        self.assertIn("does not apply", reason)

    def test_mixed_scenario_and_protocol_pull_request_fails(self):
        client = self.two_approvals()
        client.protocol_change = True
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("split", reason)

    def test_assigned_reviewer_is_trusted_when_actions_hides_association(self):
        client = self.two_approvals()
        for item in client.comments_data:
            if "## Review verdict:" in item.get("body", ""):
                item["author_association"] = "NONE"
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertTrue(ok, reason)

    def test_external_author_verdict_does_not_satisfy_the_gate(self):
        from scenario_review_flow import process_pull

        client = GateClient(pull(number=1))
        process_pull(client, client.value)
        forged = verdict("outsider", "openai-gpt")
        forged["author_association"] = "NONE"
        forged["id"] = 950
        client.comments_data.append(forged)
        client.comments_data.append(
            {
                "id": 951,
                "created_at": "2026-09-03T09:30:00Z",
                "user": {"login": "outsider"},
                "body": (
                    f"<!-- scenario-review-assignment:outsider head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:first -->"
                ),
            }
        )
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)


class MergeGroupMainTests(unittest.TestCase):
    def run_main(self, pulls, evaluations):
        clients = {}

        def fake_pull(number):
            return clients[number]

        with patch("merge_group_gate.source_pull_requests", return_value=pulls), patch(
            "merge_group_gate.load_config", return_value=normalized_config(config())
        ), patch("merge_group_gate.GitHubClient") as client_class, patch(
            "merge_group_gate.evaluate_pull", side_effect=evaluations
        ), patch.dict(
            "os.environ",
            {
                "REPOSITORY": "o/r",
                "GITHUB_TOKEN": "t",
                "MERGE_GROUP_HEAD_SHA": GROUP_B,
                "MERGE_GROUP_BASE_REF": "refs/heads/main",
            },
        ):
            instance = client_class.return_value
            instance.pull.side_effect = lambda number: {
                "number": number,
                "head": {"sha": next(
                    item["head"] for item in pulls if item["number"] == number
                )},
            }
            return main([])

    def test_every_source_pull_request_must_pass(self):
        pulls = [
            {"number": 11, "head": PR_A_HEAD},
            {"number": 22, "head": PR_B_HEAD},
        ]
        self.assertEqual(
            self.run_main(pulls, [(True, "ok"), (True, "ok")]), 0
        )
        self.assertEqual(
            self.run_main(pulls, [(True, "ok"), (False, "second is bad")]), 1
        )
        self.assertEqual(
            self.run_main(pulls, [(False, "first is bad"), (True, "ok")]), 1
        )

    def test_unidentifiable_source_pull_requests_fail_closed(self):
        with patch(
            "merge_group_gate.source_pull_requests",
            side_effect=GateFailure("no queue entry"),
        ), patch.dict(
            "os.environ",
            {
                "REPOSITORY": "o/r",
                "GITHUB_TOKEN": "t",
                "MERGE_GROUP_HEAD_SHA": GROUP_B,
                "MERGE_GROUP_BASE_REF": "refs/heads/main",
            },
        ):
            self.assertEqual(main([]), 1)


class MergeQueueWorkflowTests(unittest.TestCase):
    verify = (ROOT / ".github/workflows/verify-data.yml").read_text(encoding="utf-8")
    gate = (ROOT / ".github/workflows/merge-queue-review-gate.yml").read_text(
        encoding="utf-8"
    )
    flow = (ROOT / ".github/workflows/scenario-review-flow.yml").read_text(
        encoding="utf-8"
    )

    def test_verify_answers_pull_request_push_and_merge_group(self):
        self.assertIn("  pull_request:", self.verify)
        self.assertIn("  push:", self.verify)
        self.assertIn("  merge_group:\n    types:\n      - checks_requested", self.verify)

    def test_verify_check_name_is_stable(self):
        self.assertIn("\n  verify:\n", self.verify)

    def test_verify_has_no_path_filter(self):
        self.assertNotIn("paths:", self.verify)
        self.assertNotIn("paths-ignore:", self.verify)

    def test_verify_uses_the_base_branch_for_merge_groups(self):
        self.assertIn("refs/merge-group-base", self.verify)
        self.assertIn("github.event.merge_group.base_ref", self.verify)
        self.assertIn('base=\'HEAD^1\'', self.verify)
        # base_sha is the previous queue entry, not the base branch tip, so it
        # must never be interpolated as the diff base.
        self.assertNotIn("github.event.merge_group.base_sha", self.verify)

    def test_merge_group_gate_answers_only_merge_group(self):
        self.assertIn("on:\n  merge_group:\n    types:\n      - checks_requested", self.gate)
        self.assertNotIn("pull_request", self.gate.split("jobs:")[0])

    def test_merge_group_gate_check_name_is_review_gate(self):
        self.assertIn("\n  review-gate:\n    name: review-gate\n", self.gate)

    def test_no_other_workflow_declares_a_review_gate_job(self):
        for text in (self.verify, self.flow):
            self.assertNotIn("name: review-gate", text)

    def test_merge_group_gate_checks_out_trusted_main_only(self):
        self.assertIn("ref: main", self.gate)
        self.assertNotIn("merge_group.head_sha }}\n          ref", self.gate)
        self.assertNotIn("github.event.pull_request.head", self.gate)

    def test_merge_group_gate_permissions_are_read_only(self):
        header = self.gate.split("jobs:")[0]
        self.assertIn("permissions:\n  contents: read\n  pull-requests: read\n", header)
        for scope in ("issues: write", "pull-requests: write", "statuses: write", "contents: write"):
            self.assertNotIn(scope, self.gate)

    def test_merge_group_gate_never_writes(self):
        source = (ROOT / "scripts/merge_group_gate.py").read_text(encoding="utf-8")
        for forbidden in ("add_comment", "post_status", "sync_review_request", "send_email", "requested_reviewers"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
