import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from merge_group_gate import (  # noqa: E402
    BudgetedGitHubClient,
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


def page(nodes, has_next=False, cursor=None):
    return {
        "data": {
            "repository": {
                "mergeQueue": {
                    "entries": {
                        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                        "nodes": nodes,
                    }
                }
            }
        }
    }


def paginating_queue(entries):
    """A fake that slices by the `first`/`after` variables the caller sends.

    Ignoring them would let a page size that GitHub rejects, or one too small to
    reach the end of the queue, still pass every test.
    """

    def fake(token, query, variables):
        size = variables["page"]
        assert isinstance(size, int) and 1 <= size <= 100, f"illegal first: {size}"
        start = 0 if variables["after"] is None else int(variables["after"])
        chunk = entries[start : start + size]
        has_next = start + size < len(entries)
        return page(chunk, has_next, str(start + size) if has_next else None)

    return fake


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

    def test_octopus_commit_fails_closed(self):
        # Three parents would make `parents[1]` an arbitrary choice among the
        # merged heads, so the shape is refused rather than interpreted.
        commits = {GROUP_A: commit(GROUP_A, [MAIN_TIP, PR_A_HEAD, PR_B_HEAD])}
        with self.assertRaises(GateFailure):
            group_commits(TopologyClient(commits), GROUP_A, MAIN_TIP)

    def _chain(self, length):
        commits = {}
        previous = MAIN_TIP
        shas = [f"{index:040x}" for index in range(1, length + 1)]
        for sha in shas:
            commits[sha] = commit(sha, [previous, PR_A_HEAD])
            previous = sha
        return commits, shas

    def test_walk_limit_covers_the_largest_queue_github_allows(self):
        from merge_group_gate import MAX_GROUP_ENTRIES

        # An absolute floor, not a restatement of the constant: GitHub's merge
        # queue settings allow up to 100 entries, so the walk must accept a
        # 100-commit chain and the constant must not be quietly lowered.
        self.assertGreaterEqual(MAX_GROUP_ENTRIES, 100)
        # And an upper bound, for a different reason and with a different
        # justification than the platform's. GitHub documents that a stacked
        # merge group may exceed the configured maximum by up to 50%, so 100 is
        # not "the largest group GitHub can build". It is this repository's
        # operational ceiling: beyond it a run cannot be examined inside the
        # request budget, so the gate refuses instead of draining the quota.
        self.assertLessEqual(MAX_GROUP_ENTRIES, 100)
        commits, shas = self._chain(100)
        chain = group_commits(TopologyClient(commits), shas[-1], MAIN_TIP)
        self.assertEqual(len(chain), 100)

    def test_a_chain_at_the_walk_limit_is_accepted(self):
        from merge_group_gate import MAX_GROUP_ENTRIES

        commits, shas = self._chain(MAX_GROUP_ENTRIES)
        chain = group_commits(TopologyClient(commits), shas[-1], MAIN_TIP)
        self.assertEqual(len(chain), MAX_GROUP_ENTRIES)

    def test_a_chain_one_past_the_walk_limit_fails_closed(self):
        from merge_group_gate import MAX_GROUP_ENTRIES

        commits, shas = self._chain(MAX_GROUP_ENTRIES + 1)
        with self.assertRaises(GateFailure):
            group_commits(TopologyClient(commits), shas[-1], MAIN_TIP)


class SourcePullRequestTests(unittest.TestCase):
    def budgeted(self):
        return BudgetedGitHubClient("o/r", "token")

    def resolve(self, entries):
        with patch(
            "merge_group_gate.queue_entries_by_commit",
            return_value={item["headCommit"]["oid"].lower(): item for item in entries},
        ):
            return source_pull_requests(
                TopologyClient(), "o/r", GROUP_B, "refs/heads/main"
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

    def test_empty_merge_group_fails_closed(self):
        # The group head being the base tip means no queued pull request was
        # found. Returning an empty list here would let `main` report success
        # for a group it never examined.
        with patch("merge_group_gate.queue_entries_by_commit", return_value={}):
            with self.assertRaises(GateFailure):
                source_pull_requests(
                    TopologyClient(), "o/r", MAIN_TIP, "refs/heads/main"
                )

    def test_queue_is_read_across_every_page(self):
        pages = [
            page([entry(1, GROUP_A, 11, PR_A_HEAD)], has_next=True, cursor="c1"),
            page([entry(2, GROUP_B, 22, PR_B_HEAD)]),
        ]
        with patch("merge_group_gate.graphql", side_effect=pages) as call:
            mapping = queue_entries_by_commit(self.budgeted(), "o/r", "main")
        self.assertEqual(sorted(mapping), sorted([GROUP_A, GROUP_B]))
        self.assertEqual(call.call_count, 2)
        self.assertIsNone(call.call_args_list[0].args[2]["after"])
        self.assertEqual(call.call_args_list[1].args[2]["after"], "c1")

    def test_missing_page_info_fails_closed(self):
        response = page([entry(1, GROUP_A, 11, PR_A_HEAD)])
        del response["data"]["repository"]["mergeQueue"]["entries"]["pageInfo"]
        with patch("merge_group_gate.graphql", return_value=response):
            with self.assertRaises(GateFailure):
                queue_entries_by_commit(self.budgeted(), "o/r", "main")

    def test_non_boolean_has_next_page_fails_closed(self):
        for value in ("false", 0, None):
            with self.subTest(has_next=value):
                response = page([entry(1, GROUP_A, 11, PR_A_HEAD)])
                response["data"]["repository"]["mergeQueue"]["entries"]["pageInfo"][
                    "hasNextPage"
                ] = value
                with patch("merge_group_gate.graphql", return_value=response):
                    with self.assertRaises(GateFailure):
                        queue_entries_by_commit(self.budgeted(), "o/r", "main")

    def test_more_pages_without_a_cursor_fails_closed(self):
        response = page([entry(1, GROUP_A, 11, PR_A_HEAD)], has_next=True, cursor=None)
        with patch("merge_group_gate.graphql", return_value=response):
            with self.assertRaises(GateFailure):
                queue_entries_by_commit(self.budgeted(), "o/r", "main")

    def test_endless_pagination_fails_closed(self):
        from merge_group_gate import MAX_QUEUE_PAGES

        endless = page([entry(1, GROUP_A, 11, PR_A_HEAD)], has_next=True, cursor="c")
        with patch("merge_group_gate.graphql", return_value=endless) as call:
            with self.assertRaises(GateFailure):
                queue_entries_by_commit(self.budgeted(), "o/r", "main")
        # Exactly the declared bound: neither an off-by-one nor a doubled loop.
        self.assertEqual(call.call_count, MAX_QUEUE_PAGES)
        # And an absolute ceiling, so raising the constant cannot move the
        # assertion with it. One or two pages read the whole queue in practice.
        self.assertLessEqual(MAX_QUEUE_PAGES, 200)
        self.assertLessEqual(call.call_count, 200)

    def test_page_size_is_sent_as_a_query_variable(self):
        from merge_group_gate import QUEUE_PAGE_SIZE

        with patch(
            "merge_group_gate.graphql",
            return_value=page([entry(1, GROUP_A, 11, PR_A_HEAD)]),
        ) as call:
            queue_entries_by_commit(self.budgeted(), "o/r", "main")
        self.assertEqual(call.call_args_list[0].args[2]["page"], QUEUE_PAGE_SIZE)

    def test_page_size_stays_inside_the_graphql_contract(self):
        from merge_group_gate import QUEUE_PAGE_SIZE

        # GraphQL rejects `first` outside 1..100, so a page size beyond that
        # would fail against real GitHub while every mock happily accepted it.
        self.assertGreaterEqual(QUEUE_PAGE_SIZE, 1)
        self.assertLessEqual(QUEUE_PAGE_SIZE, 100)

    def test_pagination_can_reach_the_longest_group_the_walk_allows(self):
        from merge_group_gate import (
            MAX_GROUP_ENTRIES,
            MAX_QUEUE_PAGES,
            QUEUE_PAGE_SIZE,
        )

        # At most `QUEUE_PAGE_SIZE * MAX_QUEUE_PAGES` entries can be read before
        # the loop gives up. That has to cover every commit the walk is willing
        # to accept, otherwise a group the walk considers legal could still be
        # unmappable.
        self.assertGreaterEqual(QUEUE_PAGE_SIZE * MAX_QUEUE_PAGES, MAX_GROUP_ENTRIES)

    def test_a_full_length_queue_is_read_with_the_real_page_size(self):
        from merge_group_gate import MAX_GROUP_ENTRIES, QUEUE_PAGE_SIZE

        # One more entry than a single page holds, so the `after` branch of the
        # fake is actually exercised: a fixture that fits in one page would let
        # a fake that ignores the cursor pass.
        total = max(MAX_GROUP_ENTRIES, QUEUE_PAGE_SIZE + 1)
        entries = [
            entry(index, f"{index:040x}", index, f"{index + 900:040x}")
            for index in range(1, total + 1)
        ]
        with patch(
            "merge_group_gate.graphql", side_effect=paginating_queue(entries)
        ) as call:
            mapping = queue_entries_by_commit(self.budgeted(), "o/r", "main")
        self.assertEqual(len(mapping), total)
        self.assertGreaterEqual(call.call_count, 2)
        # The second request must resume where the first stopped.
        self.assertIsNone(call.call_args_list[0].args[2]["after"])
        self.assertEqual(
            call.call_args_list[1].args[2]["after"], str(QUEUE_PAGE_SIZE)
        )
        # Reading the longest queue must stay cheap. A page size small enough to
        # need a request per entry would satisfy every correctness assertion
        # while spending a hundred round trips on one gate run.
        self.assertLessEqual(call.call_count, 3)

    def test_unreadable_merge_queue_fails_closed(self):
        with patch(
            "merge_group_gate.graphql",
            return_value={"data": {"repository": {"mergeQueue": None}}},
        ):
            with self.assertRaises(GateFailure):
                queue_entries_by_commit(self.budgeted(), "o/r", "main")

    def test_configuration_permission_error_is_tolerated(self):
        response = page([entry(1, GROUP_A, 11, PR_A_HEAD)])
        response["errors"] = [
            {
                "path": ["repository", "mergeQueue", "configuration"],
                "message": "Resource not accessible by integration",
            }
        ]
        with patch("merge_group_gate.graphql", return_value=response):
            mapping = queue_entries_by_commit(self.budgeted(), "o/r", "main")
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
                queue_entries_by_commit(self.budgeted(), "o/r", "main")


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

    def test_evaluate_pull_calls_the_shared_maintainer_helper(self):
        # Identity of the imported name is not enough: production code could
        # keep the import for the identity assertion and call a local copy.
        # Patching the name the module actually resolves at call time pins the
        # call site itself.
        client = self.two_approvals()
        client.reviews_data.append(approved_maintainer_review())
        with patch(
            "merge_group_gate.maintainer_approved", return_value=False
        ) as shared:
            ok, reason = evaluate_pull(client, self.config, client.value)
        shared.assert_called_once()
        self.assertFalse(ok)
        self.assertIn("maintainer", reason)

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

    def test_owner_is_never_a_first_review_candidate(self):
        # `keting` is excluded from the first-review pool on the pull request
        # side; the merge-group evaluator must not quietly widen that pool.
        # The exclusion is checked against a configuration that *does* list
        # `keting` in `reviewers`, which `normalized_config` accepts: testing it
        # against a pool that happens to omit `keting` would prove nothing.
        widened = config()
        widened["reviewers"] = ["keting"] + widened["reviewers"]
        self.config = normalized_config(widened)
        self.assertIn("keting", [login.lower() for login in self.config["reviewers"]])
        from scenario_review_flow import process_pull

        client = GateClient(pull(number=1))
        process_pull(client, client.value)
        client.comments_data.append(
            {
                "id": 960,
                "created_at": "2026-09-03T09:30:00Z",
                "user": {"login": "keting"},
                "body": (
                    f"<!-- scenario-review-assignment:keting head:{HEAD} -->\n"
                    "<!-- scenario-review-stage:first -->\n"
                    "<!-- scenario-review-capability:claude-code model-family:anthropic-claude -->"
                ),
            }
        )
        client.add_verdict("keting", "anthropic-claude")
        client.reviews_data.append(approved_maintainer_review())
        ok, reason = evaluate_pull(client, self.config, client.value)
        self.assertFalse(ok)
        self.assertIn("no longer valid", reason)

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
        ), patch("merge_group_gate.BudgetedGitHubClient") as client_class, patch(
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

    def test_head_that_moves_between_queue_read_and_evaluation_fails_closed(self):
        # The queue was read first; `main` re-reads each pull request and must
        # notice a head that changed in between rather than evaluating a
        # different tree than the one that was queued.
        pulls = [{"number": 11, "head": PR_A_HEAD}]
        with patch("merge_group_gate.source_pull_requests", return_value=pulls), patch(
            "merge_group_gate.load_config", return_value=normalized_config(config())
        ), patch("merge_group_gate.BudgetedGitHubClient") as client_class, patch(
            "merge_group_gate.evaluate_pull", return_value=(True, "ok")
        ) as evaluate, patch.dict(
            "os.environ",
            {
                "REPOSITORY": "o/r",
                "GITHUB_TOKEN": "t",
                "MERGE_GROUP_HEAD_SHA": GROUP_A,
                "MERGE_GROUP_BASE_REF": "refs/heads/main",
            },
        ):
            client_class.return_value.pull.return_value = {
                "number": 11,
                "head": {"sha": "9" * 40},
            }
            self.assertEqual(main([]), 1)
        evaluate.assert_not_called()

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


class RequestBudgetTests(unittest.TestCase):
    def client(self, budget):
        return BudgetedGitHubClient("o/r", "token", budget=budget)

    def test_reads_are_counted_across_every_helper(self):
        # `paginate`, `pull`, `comments` and `reviews` all funnel through
        # `request`, so counting there bounds the whole run rather than one
        # call site.
        client = self.client(10)
        with patch(
            "notify_review_escalation.GitHubClient.request", return_value={"sha": "x"}
        ):
            client.request("/commits/main")
            client.pull(1)
        self.assertEqual(client.spent, 2)

    def test_running_out_of_budget_fails_closed(self):
        client = self.client(2)
        with patch(
            "notify_review_escalation.GitHubClient.request", return_value={}
        ):
            client.request("/one")
            client.request("/two")
            with self.assertRaises(GateFailure):
                client.request("/three")

    def test_budget_survives_the_retry_amplification(self):
        from merge_group_gate import (
            GATE_SHARE_OF_HOURLY_LIMIT,
            MAX_REQUEST_ATTEMPTS,
            REST_HOURLY_LIMIT,
            REST_REQUEST_BUDGET,
        )

        # `GitHubClient.request` retries a transient GET, so one counted call can
        # cost several HTTP requests against the hourly limit. Counting logical
        # calls without that factor would understate the real cost threefold.
        # Absolute anchors, not restatements of the constants: every value
        # below is checked against the documented platform fact rather than
        # against another constant in the same file, so raising one of them to
        # make the arithmetic work out cannot pass.
        self.assertEqual(REST_HOURLY_LIMIT, 1000)  # GITHUB_TOKEN, per repo, per hour
        self.assertEqual(MAX_REQUEST_ATTEMPTS, self._client_retry_attempts())
        worst_case = REST_REQUEST_BUDGET * MAX_REQUEST_ATTEMPTS
        self.assertLessEqual(
            worst_case, REST_HOURLY_LIMIT * GATE_SHARE_OF_HOURLY_LIMIT
        )
        # And the share must genuinely leave the hour to the other workflows.
        self.assertLess(GATE_SHARE_OF_HOURLY_LIMIT, 0.5)
        # Still large enough for a realistic group: a single pull request costs
        # under a dozen requests.
        self.assertGreaterEqual(REST_REQUEST_BUDGET, 50)

    def _client_retry_attempts(self):
        """Read the retry count out of the client this gate actually uses."""
        import inspect

        import notify_review_escalation

        source = inspect.getsource(notify_review_escalation.GitHubClient.request)
        for line in source.splitlines():
            if "attempts = " in line:
                return int(line.split("attempts = ")[1].split()[0])
        raise AssertionError("could not read the retry count from GitHubClient")

    def test_graphql_reads_are_budgeted_too(self):
        from merge_group_gate import GRAPHQL_REQUEST_BUDGET

        # `graphql` does not go through `request`, so it needs its own accounting
        # rather than being trusted to the page loop.
        client = BudgetedGitHubClient("o/r", "token", graphql_budget=2)
        client.charge_graphql()
        client.charge_graphql()
        with self.assertRaises(GateFailure):
            client.charge_graphql()
        # Absolute bounds. Reading the queue takes one or two pages in practice,
        # so a budget in the hundreds already has no legitimate use and a budget
        # large enough to be meaningless must not pass.
        self.assertGreaterEqual(GRAPHQL_REQUEST_BUDGET, 1)
        self.assertLessEqual(GRAPHQL_REQUEST_BUDGET, 200)

    def test_queue_paging_charges_the_graphql_budget(self):
        client = BudgetedGitHubClient("o/r", "token")
        entries = [entry(1, GROUP_A, 11, PR_A_HEAD)]
        with patch(
            "merge_group_gate.graphql", side_effect=paginating_queue(entries)
        ):
            queue_entries_by_commit(client, "o/r", "main")
        self.assertEqual(client.graphql_spent, 1)

    def test_an_endless_queue_exhausts_the_graphql_budget_not_the_loop(self):
        client = BudgetedGitHubClient("o/r", "token", graphql_budget=3)
        endless = page([entry(1, GROUP_A, 11, PR_A_HEAD)], has_next=True, cursor="c")
        with patch("merge_group_gate.graphql", return_value=endless) as call:
            with self.assertRaises(GateFailure):
                queue_entries_by_commit(client, "o/r", "main")
        self.assertEqual(call.call_count, 3)

    def test_a_paginating_read_cannot_outrun_the_budget(self):
        # The worst case the reviewer identified: a pull request whose files,
        # comments and reviews each paginate to the 100-page limit.
        client = self.client(10)
        pages = [[{"x": index} for index in range(100)] for _ in range(20)]
        with patch(
            "notify_review_escalation.GitHubClient.request", side_effect=pages
        ):
            with self.assertRaises(GateFailure):
                client.paginate("/pulls/1/files")
        self.assertEqual(client.spent, 11)


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

    def test_base_branch_fetch_is_limited_to_merge_group_runs(self):
        # Fetching the base branch on a pull request run would replace the
        # merge-commit base and change what the index gate compares.
        self.assertIn(
            "if: github.event_name == 'merge_group'\n", self.verify
        )
        self.assertIn('if [ "$EVENT_NAME" = "merge_group" ]; then', self.verify)

    def test_pull_request_side_review_gate_requires_a_maintainer_approval(self):
        # Both sides of `review-gate` must ask the same question, or a pull
        # request that passed on the pull request would be ejected from the
        # queue for a reason never shown on it.
        flow = (ROOT / "scripts/scenario_review_flow.py").read_text(encoding="utf-8")
        gate = (ROOT / "scripts/merge_group_gate.py").read_text(encoding="utf-8")
        self.assertIn("def maintainer_approved(", flow)
        self.assertIn("maintainer_approved(config, reviews", flow)
        self.assertIn("maintainer_approved", gate)
        # Identity, not text: a renamed local copy would defeat a source check
        # but cannot make these two names refer to the same function object.
        import merge_group_gate
        import scenario_review_flow

        self.assertIs(
            merge_group_gate.maintainer_approved,
            scenario_review_flow.maintainer_approved,
        )

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

    def test_merge_group_gate_has_a_wall_clock_bound(self):
        # The request budget bounds call count, not time: each call can wait out
        # a 30 second timeout, so a run needs its own ceiling or it can hold a
        # runner and the queue open for over an hour.
        self.assertIn("timeout-minutes:", self.gate)

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
