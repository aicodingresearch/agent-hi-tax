"""Every path through the results auto-enqueue gate, especially the refusals.

The gate's whole value is that it refuses. So each test here changes exactly one
thing about an otherwise valid refresh pull request and asserts that the change
is enough to stop the enqueue — and, for the cases that matter, that no write
was attempted at all.
"""

import contextlib
import base64
import io
import json
import os
import re
import sys
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import auto_enqueue_results_pr as gate  # noqa: E402


SOURCE = (
    Path(__file__).resolve().parents[1] / "scripts" / "auto_enqueue_results_pr.py"
).read_text(encoding="utf-8")


REPOSITORY = "aicodingresearch/agent-hi-tax"
MAIN = "1" * 40
HEAD = "a" * 40
OTHER_HEAD = "b" * 40
NODE_ID = "PR_kwDOexample"
EN_TEXT = "# Results\n\nEnglish index\n"
ZH_TEXT = "# 结果\n\n中文索引\n"
RENDERED = {"en": EN_TEXT, "zh": ZH_TEXT}


def encoded(text):
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
    }


def pull_payload(**overrides):
    payload = {
        "number": 93,
        "node_id": NODE_ID,
        "state": "open",
        "draft": False,
        "merged": False,
        "base": {"ref": "main"},
        "head": {
            "ref": gate.REFRESH_BRANCH,
            "sha": HEAD,
            "repo": {"full_name": REPOSITORY},
        },
    }
    payload.update(overrides)
    return payload


def routes(**overrides):
    """The reply table for a pull request that should be enqueued."""
    owner = REPOSITORY.partition("/")[0]
    table = {
        "/commits/main": {"sha": MAIN},
        f"/pulls?state=open&base=main&head={owner}:{gate.REFRESH_BRANCH}": [
            pull_payload()
        ],
        "/pulls/93": pull_payload(),
        "/pulls/93/files": [
            {"filename": "RESULTS.md", "status": "modified"},
            {"filename": "RESULTS.zh-CN.md", "status": "modified"},
        ],
        f"/contents/RESULTS.md?ref={HEAD}": encoded(EN_TEXT),
        f"/contents/RESULTS.zh-CN.md?ref={HEAD}": encoded(ZH_TEXT),
        f"/commits/{HEAD}/check-runs": {
            "total_count": 1,
            "check_runs": [
                {"name": "verify", "status": "completed", "conclusion": "success"}
            ],
        },
        f"/commits/{HEAD}/status": {
            "state": "success",
            "statuses": [{"context": "review-gate", "state": "success"}],
        },
    }
    table.update(overrides)
    return table


class FakeClient:
    """Answers from a table keyed by the path without pagination parameters."""

    def __init__(self, table, budget=gate.REST_REQUEST_BUDGET):
        self.table = table
        self.calls = []
        self.budget = budget
        self.spent = 0

    def request(self, path, method="GET", payload=None):
        if method != "GET":
            raise gate.EnqueueRefused(f"refusing to issue a {method} request to {path}")
        self.spent += 1
        if self.spent > self.budget:
            raise gate.EnqueueRefused(
                f"exceeded the budget of {self.budget} GitHub REST requests"
            )
        self.calls.append(path)
        base, _, query = path.partition("?")
        kept = "&".join(
            part
            for part in query.split("&")
            if part and not part.startswith(("per_page=", "page="))
        )
        key = f"{base}?{kept}" if kept else base
        page = 1
        for part in query.split("&"):
            if part.startswith("page="):
                page = int(part[len("page=") :])
        if key not in self.table:
            raise AssertionError(f"unexpected request: {path}")
        value = self.table[key]
        if page > 1:
            # Page two of a one-page answer is empty, in whichever shape the
            # endpoint uses.
            if isinstance(value, list):
                return []
            if isinstance(value, dict) and "check_runs" in value:
                return {"total_count": 0, "check_runs": []}
        return value


class GateTestCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(
            gate, "render_index", side_effect=lambda root, lang: RENDERED[lang]
        )
        self.render = patcher.start()
        self.addCleanup(patcher.stop)

    def verify(self, client):
        with contextlib.redirect_stdout(io.StringIO()):
            return gate.verify(client, REPOSITORY, Path("."), MAIN)

    def refusal(self, table):
        client = FakeClient(table)
        with self.assertRaises(gate.EnqueueRefused) as caught:
            self.verify(client)
        return str(caught.exception)


class HappyPathTests(GateTestCase):
    def test_a_valid_refresh_pull_request_verifies(self):
        client = FakeClient(routes())
        pull, head = self.verify(client)
        self.assertEqual(pull["number"], 93)
        self.assertEqual(head, HEAD)

    def test_the_pull_request_is_looked_up_by_the_fixed_branch(self):
        client = FakeClient(routes())
        self.verify(client)
        query = next(call for call in client.calls if call.startswith("/pulls?"))
        self.assertIn(f"head=aicodingresearch:{gate.REFRESH_BRANCH}", query)
        self.assertIn("base=main", query)
        self.assertIn("state=open", query)

    def test_the_head_is_read_again_before_enqueueing(self):
        client = FakeClient(routes())
        self.verify(client)
        self.assertIn("/pulls/93", client.calls)

    def test_verification_stays_well_inside_its_request_budget(self):
        client = FakeClient(routes())
        self.verify(client)
        self.assertLess(client.spent, gate.REST_REQUEST_BUDGET)


class TrustedCheckoutTests(GateTestCase):
    def test_a_main_that_moved_after_checkout_is_refused(self):
        message = self.refusal(routes(**{"/commits/main": {"sha": OTHER_HEAD}}))
        self.assertIn("moved", message)

    def test_an_unreadable_main_is_refused(self):
        message = self.refusal(routes(**{"/commits/main": []}))
        self.assertIn("could not resolve", message)

    def test_a_local_sha_that_is_not_a_sha_is_refused(self):
        client = FakeClient(routes())
        with self.assertRaises(gate.EnqueueRefused):
            with contextlib.redirect_stdout(io.StringIO()):
                gate.verify(client, REPOSITORY, Path("."), "not-a-sha")


class PullRequestShapeTests(GateTestCase):
    def query_key(self):
        owner = REPOSITORY.partition("/")[0]
        return f"/pulls?state=open&base=main&head={owner}:{gate.REFRESH_BRANCH}"

    def with_pull(self, **overrides):
        pull = pull_payload(**overrides)
        return routes(**{self.query_key(): [pull], "/pulls/93": pull})

    def test_no_open_refresh_pull_request_is_refused(self):
        message = self.refusal(routes(**{self.query_key(): []}))
        self.assertIn("no open pull request", message)

    def test_two_open_refresh_pull_requests_are_refused(self):
        table = routes(
            **{self.query_key(): [pull_payload(), pull_payload(number=94)]}
        )
        message = self.refusal(table)
        self.assertIn("exactly one", message)

    def test_a_draft_is_refused(self):
        self.assertIn("draft", self.refusal(self.with_pull(draft=True)))

    def test_a_closed_pull_request_is_refused(self):
        self.assertIn("not open", self.refusal(self.with_pull(state="closed")))

    def test_an_already_merged_pull_request_is_refused(self):
        self.assertIn("already merged", self.refusal(self.with_pull(merged=True)))

    def test_another_base_branch_is_refused(self):
        message = self.refusal(self.with_pull(base={"ref": "release"}))
        self.assertIn("targets", message)

    def test_another_head_branch_is_refused(self):
        head = {"ref": "chore/other", "sha": HEAD, "repo": {"full_name": REPOSITORY}}
        self.assertIn("comes from", self.refusal(self.with_pull(head=head)))

    def test_a_fork_head_is_refused(self):
        head = {
            "ref": gate.REFRESH_BRANCH,
            "sha": HEAD,
            "repo": {"full_name": "someone-else/agent-hi-tax"},
        }
        self.assertIn("head lives in", self.refusal(self.with_pull(head=head)))

    def test_a_deleted_head_repository_is_refused(self):
        head = {"ref": gate.REFRESH_BRANCH, "sha": HEAD, "repo": None}
        self.assertIn("head lives in", self.refusal(self.with_pull(head=head)))

    def test_a_malformed_head_sha_is_refused(self):
        head = {
            "ref": gate.REFRESH_BRANCH,
            "sha": "abc",
            "repo": {"full_name": REPOSITORY},
        }
        self.assertIn("no usable head sha", self.refusal(self.with_pull(head=head)))

    def test_a_missing_node_id_is_refused(self):
        self.assertIn("no node id", self.refusal(self.with_pull(node_id="")))


class FileSetTests(GateTestCase):
    def with_files(self, files):
        return routes(**{"/pulls/93/files": files})

    def test_an_extra_file_is_refused(self):
        message = self.refusal(
            self.with_files(
                [
                    {"filename": "RESULTS.md", "status": "modified"},
                    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
                    {"filename": ".github/workflows/verify-data.yml", "status": "modified"},
                ]
            )
        )
        self.assertIn("unexpected", message)
        self.assertIn("verify-data.yml", message)

    def test_only_one_index_page_is_refused(self):
        message = self.refusal(
            self.with_files([{"filename": "RESULTS.md", "status": "modified"}])
        )
        self.assertIn("absent", message)

    def test_an_empty_change_set_is_refused(self):
        self.assertIn("expected exactly", self.refusal(self.with_files([])))

    def test_a_lookalike_path_is_refused(self):
        message = self.refusal(
            self.with_files(
                [
                    {"filename": "docs/RESULTS.md", "status": "modified"},
                    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
                ]
            )
        )
        self.assertIn("unexpected", message)

    def test_an_added_index_page_is_refused(self):
        message = self.refusal(
            self.with_files(
                [
                    {"filename": "RESULTS.md", "status": "added"},
                    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
                ]
            )
        )
        self.assertIn("'added'", message)

    def test_a_removed_index_page_is_refused(self):
        message = self.refusal(
            self.with_files(
                [
                    {"filename": "RESULTS.md", "status": "removed"},
                    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
                ]
            )
        )
        self.assertIn("'removed'", message)

    def test_a_renamed_index_page_is_refused(self):
        message = self.refusal(
            self.with_files(
                [
                    {"filename": "RESULTS.md", "status": "renamed"},
                    {"filename": "RESULTS.zh-CN.md", "status": "modified"},
                ]
            )
        )
        self.assertIn("'renamed'", message)


class DeterministicContentTests(GateTestCase):
    def test_a_single_changed_byte_is_refused(self):
        table = routes(
            **{f"/contents/RESULTS.md?ref={HEAD}": encoded(EN_TEXT + "x")}
        )
        self.assertIn("generator's output", self.refusal(table))

    def test_a_stale_chinese_page_is_refused(self):
        table = routes(
            **{f"/contents/RESULTS.zh-CN.md?ref={HEAD}": encoded("# 旧的\n")}
        )
        message = self.refusal(table)
        self.assertIn("RESULTS.zh-CN.md", message)

    def test_both_pages_are_compared(self):
        client = FakeClient(routes())
        self.verify(client)
        self.assertEqual(
            sorted(call.split("?")[0] for call in client.calls if "/contents/" in call),
            ["/contents/RESULTS.md", "/contents/RESULTS.zh-CN.md"],
        )

    def test_the_comparison_reads_the_pull_request_head_not_main(self):
        client = FakeClient(routes())
        self.verify(client)
        for call in client.calls:
            if call.startswith("/contents/"):
                self.assertIn(f"ref={HEAD}", call)

    def test_a_directory_where_a_page_should_be_is_refused(self):
        table = routes(**{f"/contents/RESULTS.md?ref={HEAD}": {"type": "dir"}})
        self.assertIn("not a file", self.refusal(table))

    def test_an_unexpected_encoding_is_refused(self):
        table = routes(
            **{
                f"/contents/RESULTS.md?ref={HEAD}": {
                    "type": "file",
                    "encoding": "none",
                    "content": "",
                }
            }
        )
        self.assertIn("cannot verify", self.refusal(table))

    def test_content_that_is_not_utf8_is_refused(self):
        table = routes(
            **{
                f"/contents/RESULTS.md?ref={HEAD}": {
                    "type": "file",
                    "encoding": "base64",
                    "content": base64.b64encode(b"\xff\xfe").decode("ascii"),
                }
            }
        )
        self.assertIn("not UTF-8", self.refusal(table))

    def test_a_generator_failure_is_refused(self):
        with mock.patch.object(gate, "render_index", side_effect=ValueError("boom")):
            client = FakeClient(routes())
            with self.assertRaises(gate.EnqueueRefused) as caught:
                with contextlib.redirect_stdout(io.StringIO()):
                    gate.verify(client, REPOSITORY, Path("."), MAIN)
        self.assertIn("could not regenerate", str(caught.exception))


class RequiredCheckTests(GateTestCase):
    def with_check_runs(self, check_runs):
        return routes(
            **{
                f"/commits/{HEAD}/check-runs": {
                    "total_count": len(check_runs),
                    "check_runs": check_runs,
                }
            }
        )

    def with_statuses(self, statuses):
        return routes(
            **{f"/commits/{HEAD}/status": {"state": "success", "statuses": statuses}}
        )

    def test_a_missing_verify_check_run_is_refused(self):
        message = self.refusal(self.with_check_runs([]))
        self.assertIn("has not reported", message)

    def test_a_verify_check_run_still_running_is_refused(self):
        message = self.refusal(
            self.with_check_runs(
                [{"name": "verify", "status": "in_progress", "conclusion": None}]
            )
        )
        self.assertIn("not completed", message)

    def test_a_skipped_verify_check_run_is_refused(self):
        message = self.refusal(
            self.with_check_runs(
                [{"name": "verify", "status": "completed", "conclusion": "skipped"}]
            )
        )
        self.assertIn("skipped", message)

    def test_a_neutral_verify_check_run_is_refused(self):
        message = self.refusal(
            self.with_check_runs(
                [{"name": "verify", "status": "completed", "conclusion": "neutral"}]
            )
        )
        self.assertIn("neutral", message)

    def test_a_failed_verify_check_run_is_refused(self):
        message = self.refusal(
            self.with_check_runs(
                [{"name": "verify", "status": "completed", "conclusion": "failure"}]
            )
        )
        self.assertIn("failure", message)

    def test_one_green_rerun_does_not_excuse_a_red_one(self):
        message = self.refusal(
            self.with_check_runs(
                [
                    {"name": "verify", "status": "completed", "conclusion": "success"},
                    {"name": "verify", "status": "completed", "conclusion": "failure"},
                ]
            )
        )
        self.assertIn("failure", message)

    def test_another_green_check_does_not_stand_in_for_verify(self):
        message = self.refusal(
            self.with_check_runs(
                [{"name": "manage", "status": "completed", "conclusion": "success"}]
            )
        )
        self.assertIn("'verify'", message)

    def test_a_missing_review_gate_status_is_refused(self):
        self.assertIn("has not reported", self.refusal(self.with_statuses([])))

    def test_a_pending_review_gate_status_is_refused(self):
        message = self.refusal(
            self.with_statuses([{"context": "review-gate", "state": "pending"}])
        )
        self.assertIn("pending", message)

    def test_a_failed_review_gate_status_is_refused(self):
        message = self.refusal(
            self.with_statuses([{"context": "review-gate", "state": "failure"}])
        )
        self.assertIn("failure", message)

    def test_a_review_gate_check_run_does_not_stand_in_for_the_status(self):
        # `review-gate` is a commit status on the pull request. A check run of
        # the same name must not be mistaken for it.
        table = self.with_statuses([])
        table[f"/commits/{HEAD}/check-runs"] = {
            "total_count": 2,
            "check_runs": [
                {"name": "verify", "status": "completed", "conclusion": "success"},
                {"name": "review-gate", "status": "completed", "conclusion": "success"},
            ],
        }
        self.assertIn("has not reported", self.refusal(table))

    def test_a_verify_status_does_not_stand_in_for_the_check_run(self):
        table = self.with_check_runs([])
        table[f"/commits/{HEAD}/status"] = {
            "state": "success",
            "statuses": [
                {"context": "review-gate", "state": "success"},
                {"context": "verify", "state": "success"},
            ],
        }
        self.assertIn("'verify'", self.refusal(table))

    def test_malformed_status_payloads_are_refused(self):
        table = routes(**{f"/commits/{HEAD}/status": {"state": "success"}})
        self.assertIn("not a list", self.refusal(table))


class WaitingTests(GateTestCase):
    """Waiting may only ever be for "no answer yet", never for a red answer."""

    def wait(self, client, wait_seconds=90, poll_seconds=30):
        slept = []
        clock = iter(range(0, 10_000, 30))
        with contextlib.redirect_stdout(io.StringIO()):
            result = gate.verify_with_wait(
                client,
                REPOSITORY,
                Path("."),
                MAIN,
                wait_seconds,
                poll_seconds,
                sleep=slept.append,
                clock=lambda: next(clock),
            )
        return result, slept

    def test_pending_is_a_kind_of_refusal(self):
        self.assertTrue(issubclass(gate.EnqueuePending, gate.EnqueueRefused))

    def test_a_check_that_arrives_late_is_waited_for(self):
        table = routes(
            **{f"/commits/{HEAD}/check-runs": {"total_count": 0, "check_runs": []}}
        )
        client = FakeClient(table)
        real_request = client.request
        state = {"polls": 0}

        def request(path, method="GET", payload=None):
            if "check-runs" in path:
                state["polls"] += 1
                if state["polls"] > 2:
                    return {
                        "total_count": 1,
                        "check_runs": [
                            {
                                "name": "verify",
                                "status": "completed",
                                "conclusion": "success",
                            }
                        ],
                    }
            return real_request(path, method, payload)

        client.request = request
        (pull, head), slept = self.wait(client)
        self.assertEqual(head, HEAD)
        self.assertEqual(slept, [30, 30])

    def test_a_check_that_never_answers_is_refused_at_the_deadline(self):
        table = routes(
            **{f"/commits/{HEAD}/check-runs": {"total_count": 0, "check_runs": []}}
        )
        with self.assertRaises(gate.EnqueueRefused) as caught:
            self.wait(FakeClient(table))
        self.assertIn("still not decided", str(caught.exception))

    def test_a_red_check_is_never_waited_out(self):
        table = routes(
            **{
                f"/commits/{HEAD}/check-runs": {
                    "total_count": 1,
                    "check_runs": [
                        {"name": "verify", "status": "completed", "conclusion": "failure"}
                    ],
                }
            }
        )
        with self.assertRaises(gate.EnqueueRefused) as caught:
            _, slept = self.wait(FakeClient(table))
        self.assertNotIsInstance(caught.exception, gate.EnqueuePending)
        self.assertIn("failure", str(caught.exception))

    def test_a_wrong_file_set_is_never_waited_out(self):
        table = routes(**{"/pulls/93/files": []})
        with self.assertRaises(gate.EnqueueRefused) as caught:
            self.wait(FakeClient(table))
        self.assertNotIsInstance(caught.exception, gate.EnqueuePending)

    def test_the_request_budget_still_bounds_a_long_wait(self):
        table = routes(
            **{f"/commits/{HEAD}/check-runs": {"total_count": 0, "check_runs": []}}
        )
        client = FakeClient(table, budget=12)
        with self.assertRaises(gate.EnqueueRefused) as caught:
            self.wait(client, wait_seconds=10_000)
        self.assertIn("budget", str(caught.exception))

    def test_a_truncated_response_is_retried_rather_than_failing_the_run(self):
        # GitHub occasionally truncates a reply; observed three times in seven
        # live runs. Nothing has been decided at that point, so retry.
        client = FakeClient(routes())
        real_request = client.request
        state = {"failures": 0}

        def request(path, method="GET", payload=None):
            if "check-runs" in path and state["failures"] < 2:
                state["failures"] += 1
                raise RuntimeError(
                    "GitHub API GET /check-runs failed: IncompleteRead(5465 bytes read)"
                )
            return real_request(path, method, payload)

        client.request = request
        (pull, head), slept = self.wait(client)
        self.assertEqual(head, HEAD)
        self.assertEqual(slept, [30, 30])

    def test_a_transport_failure_that_never_clears_stays_an_error(self):
        class Broken:
            spent = 0

            def request(self, path, method="GET", payload=None):
                raise RuntimeError("connection reset")

        with self.assertRaises(RuntimeError) as caught:
            self.wait(Broken())
        self.assertNotIsInstance(caught.exception, gate.EnqueueRefused)
        self.assertIn("still not decided", str(caught.exception))

    def test_a_refusal_is_never_retried_as_a_transport_failure(self):
        table = routes(**{"/pulls/93/files": []})
        client = FakeClient(table)
        with self.assertRaises(gate.EnqueueRefused):
            self.wait(client)
        # One pass only: a decided no must not consume the wait budget.
        self.assertEqual(len([c for c in client.calls if c.startswith("/pulls?")]), 1)

    def test_every_attempt_re_reads_the_head(self):
        table = routes(
            **{f"/commits/{HEAD}/check-runs": {"total_count": 0, "check_runs": []}}
        )
        client = FakeClient(table)
        with self.assertRaises(gate.EnqueueRefused):
            self.wait(client, wait_seconds=90)
        self.assertGreater(len([c for c in client.calls if c.startswith("/pulls?")]), 1)


class HeadRaceTests(GateTestCase):
    def test_a_head_that_moved_during_verification_is_refused(self):
        moved = pull_payload(
            head={
                "ref": gate.REFRESH_BRANCH,
                "sha": OTHER_HEAD,
                "repo": {"full_name": REPOSITORY},
            }
        )
        message = self.refusal(routes(**{"/pulls/93": moved}))
        self.assertIn("moved from", message)

    def test_a_pull_request_closed_during_verification_is_refused(self):
        message = self.refusal(routes(**{"/pulls/93": pull_payload(state="closed")}))
        self.assertIn("no longer open", message)

    def test_a_pull_request_merged_during_verification_is_refused(self):
        message = self.refusal(routes(**{"/pulls/93": pull_payload(merged=True)}))
        self.assertIn("no longer open", message)


class BudgetAndPaginationTests(GateTestCase):
    def test_running_out_of_budget_refuses_rather_than_enqueues(self):
        client = FakeClient(routes(), budget=3)
        with self.assertRaises(gate.EnqueueRefused) as caught:
            self.verify(client)
        self.assertIn("budget", str(caught.exception))

    def test_the_budget_is_derived_from_the_hourly_limit(self):
        self.assertEqual(
            gate.REST_REQUEST_BUDGET,
            int(
                gate.REST_HOURLY_LIMIT
                * gate.ENQUEUE_SHARE_OF_HOURLY_LIMIT
                / gate.MAX_REQUEST_ATTEMPTS
            ),
        )

    def test_a_list_endpoint_that_never_ends_is_refused(self):
        class Endless:
            def request(self, path, method="GET", payload=None):
                return [{"filename": "RESULTS.md"}] * gate.PAGE_SIZE

        with self.assertRaises(gate.EnqueueRefused) as caught:
            gate.paginate_list(Endless(), "/pulls/93/files")
        self.assertIn("exceeded", str(caught.exception))

    def test_an_enveloped_endpoint_that_never_ends_is_refused(self):
        class Endless:
            def request(self, path, method="GET", payload=None):
                return {"check_runs": [{"name": "verify"}] * gate.PAGE_SIZE}

        with self.assertRaises(gate.EnqueueRefused) as caught:
            gate.paginate_envelope(Endless(), "/commits/x/check-runs", "check_runs")
        self.assertIn("exceeded", str(caught.exception))

    def test_a_list_endpoint_that_answers_an_object_is_refused(self):
        class Wrong:
            def request(self, path, method="GET", payload=None):
                return {"unexpected": True}

        with self.assertRaises(gate.EnqueueRefused):
            gate.paginate_list(Wrong(), "/pulls/93/files")


class WriteGuardTests(unittest.TestCase):
    def test_the_rest_client_refuses_every_method_but_get(self):
        client = gate.BudgetedClient(REPOSITORY, "token")
        for method in ("POST", "PATCH", "PUT", "DELETE"):
            with self.assertRaises(gate.EnqueueRefused) as caught:
                client.request("/pulls/93/reviews", method=method, payload={})
            self.assertIn("only reads", str(caught.exception))

    def test_no_rest_path_in_the_source_is_a_write_endpoint(self):
        # Checks the paths the program can actually build, not its prose: every
        # string literal that looks like an API path must be a read.
        literals = re.findall(r'f?"(/[^"]*)"', SOURCE)
        self.assertTrue(literals)
        for literal in literals:
            for forbidden in (
                "/merge",
                "/reviews",
                "/comments",
                "/requested_reviewers",
                "/statuses/",
                "/rulesets",
            ):
                self.assertNotIn(
                    forbidden, literal, f"{literal} reaches a write endpoint"
                )

    def test_the_only_mutation_is_enqueue_pull_request(self):
        self.assertEqual(SOURCE.count("mutation("), 1)
        self.assertIn("enqueuePullRequest", gate.ENQUEUE_MUTATION)
        for name in (
            "addPullRequestReview",
            "mergePullRequest",
            "addComment",
            "createCommitOnBranch",
            "dequeuePullRequest",
        ):
            self.assertNotIn(name, SOURCE)

    def test_the_only_non_get_request_is_that_mutation(self):
        self.assertEqual(SOURCE.count('method="POST"'), 1)
        for method in ('method="PUT"', 'method="PATCH"', 'method="DELETE"'):
            self.assertNotIn(method, SOURCE)


class EnqueueMutationTests(unittest.TestCase):
    def call(self, reply, status=200):
        captured = {}

        class Response:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *args):
                return False

            def read(self_inner):
                return json.dumps(reply).encode("utf-8")

        def urlopen(request, timeout=None):
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data)
            captured["auth"] = request.get_header("Authorization")
            return Response()

        with mock.patch.object(gate.urllib.request, "urlopen", urlopen):
            try:
                entry = gate.enqueue("app-token", NODE_ID, HEAD)
            except gate.EnqueueRefused as error:
                return captured, error
        return captured, entry

    def test_the_mutation_carries_the_verified_head_as_expected_oid(self):
        captured, entry = self.call(
            {
                "data": {
                    "enqueuePullRequest": {
                        "mergeQueueEntry": {"id": "MQE_1", "position": 1, "state": "QUEUED"}
                    }
                }
            }
        )
        self.assertEqual(captured["body"]["variables"]["expectedHeadOid"], HEAD)
        self.assertEqual(captured["body"]["variables"]["pullRequestId"], NODE_ID)
        self.assertEqual(captured["auth"], "Bearer app-token")
        self.assertEqual(entry["id"], "MQE_1")

    def test_a_graphql_error_is_a_refusal(self):
        _, error = self.call(
            {
                "data": {"enqueuePullRequest": None},
                "errors": [{"message": "expected head oid does not match"}],
            }
        )
        self.assertIsInstance(error, gate.EnqueueRefused)
        self.assertIn("expected head oid", str(error))

    def test_an_empty_reply_is_a_refusal(self):
        _, error = self.call({"data": {"enqueuePullRequest": None}})
        self.assertIsInstance(error, gate.EnqueueRefused)
        self.assertIn("returned no entry", str(error))


class MainTests(GateTestCase):
    def run_main(self, argv, env, verify_result=None, enqueue_side_effect=None):
        calls = {"enqueue": []}

        def fake_enqueue(token, node_id, expected_head):
            calls["enqueue"].append((token, node_id, expected_head))
            if enqueue_side_effect is not None:
                raise enqueue_side_effect
            return {"id": "MQE_1", "position": 1, "state": "QUEUED"}

        table = routes()

        def fake_client(repository, token):
            return FakeClient(table)

        buffer = io.StringIO()
        fast = ["--wait-seconds", "0", "--poll-seconds", "0", *argv]
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(gate, "BudgetedClient", fake_client):
                with mock.patch.object(gate, "enqueue", fake_enqueue):
                    with contextlib.redirect_stdout(buffer):
                        code = gate.main(fast)
        return code, buffer.getvalue(), calls

    def base_env(self, **overrides):
        env = {
            "REPOSITORY": REPOSITORY,
            "GITHUB_TOKEN": "read-token",
            "ENQUEUE_TOKEN": "app-token",
            "TRUSTED_MAIN_SHA": MAIN,
            "RESULTS_AUTO_ENQUEUE_ENABLED": "true",
        }
        env.update(overrides)
        return env

    def test_the_switch_off_verifies_but_never_enqueues(self):
        code, out, calls = self.run_main([], self.base_env(RESULTS_AUTO_ENQUEUE_ENABLED="false"))
        self.assertEqual(code, 0)
        self.assertEqual(calls["enqueue"], [])
        self.assertIn('"step": "dry_run"', out)

    def test_an_absent_switch_is_off(self):
        env = self.base_env()
        del env["RESULTS_AUTO_ENQUEUE_ENABLED"]
        code, out, calls = self.run_main([], env)
        self.assertEqual(code, 0)
        self.assertEqual(calls["enqueue"], [])

    def test_a_switch_that_is_neither_true_nor_false_fails(self):
        code, _, calls = self.run_main([], self.base_env(RESULTS_AUTO_ENQUEUE_ENABLED="yes"))
        self.assertEqual(code, 1)
        self.assertEqual(calls["enqueue"], [])

    def test_dry_run_beats_the_switch(self):
        code, out, calls = self.run_main(["--dry-run"], self.base_env())
        self.assertEqual(code, 0)
        self.assertEqual(calls["enqueue"], [])
        self.assertIn("would be enqueued", out)

    def test_the_switch_on_enqueues_with_the_verified_head(self):
        code, out, calls = self.run_main([], self.base_env())
        self.assertEqual(code, 0)
        self.assertEqual(calls["enqueue"], [("app-token", NODE_ID, HEAD)])
        self.assertIn('"step": "enqueued"', out)

    def test_a_refusal_is_reported_as_a_notice_and_not_a_failure(self):
        table = routes(**{"/commits/main": {"sha": OTHER_HEAD}})
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, self.base_env(), clear=True):
            with mock.patch.object(gate, "BudgetedClient", lambda r, t: FakeClient(table)):
                with mock.patch.object(gate, "enqueue", mock.Mock()) as enqueued:
                    with contextlib.redirect_stdout(buffer):
                        code = gate.main([])
        self.assertEqual(code, 0)
        enqueued.assert_not_called()
        self.assertIn("::notice", buffer.getvalue())
        self.assertNotIn("::error", buffer.getvalue())

    def test_an_unexpected_failure_is_an_error_and_not_an_enqueue(self):
        class Broken:
            spent = 0

            def request(self, path, method="GET", payload=None):
                raise RuntimeError("network is gone")

        buffer = io.StringIO()
        with mock.patch.dict(os.environ, self.base_env(), clear=True):
            with mock.patch.object(gate, "BudgetedClient", lambda r, t: Broken()):
                with mock.patch.object(gate, "enqueue", mock.Mock()) as enqueued:
                    with contextlib.redirect_stdout(buffer):
                        code = gate.main(
                            ["--wait-seconds", "0", "--poll-seconds", "0"]
                        )
        self.assertEqual(code, 1)
        enqueued.assert_not_called()
        self.assertIn("::error", buffer.getvalue())

    def test_a_rejected_enqueue_fails_the_run(self):
        code, out, calls = self.run_main(
            [],
            self.base_env(),
            enqueue_side_effect=gate.EnqueueRefused("head oid does not match"),
        )
        self.assertEqual(code, 1)
        self.assertIn("::error", out)

    def test_the_enqueue_token_is_only_required_when_enqueueing(self):
        env = self.base_env(RESULTS_AUTO_ENQUEUE_ENABLED="false")
        del env["ENQUEUE_TOKEN"]
        code, _, calls = self.run_main([], env)
        self.assertEqual(code, 0)
        self.assertEqual(calls["enqueue"], [])

    def test_the_switch_on_without_an_app_token_says_so_and_stops(self):
        # Turning the variable on before the app exists must not end the run on
        # a traceback: the job has to say which secret is missing.
        env = self.base_env()
        del env["ENQUEUE_TOKEN"]
        code, out, calls = self.run_main([], env)
        self.assertEqual(code, 1)
        self.assertEqual(calls["enqueue"], [])
        self.assertIn("RESULTS_APP_ID", out)
        self.assertIn("::error", out)

    def test_an_empty_app_token_is_treated_as_absent(self):
        code, out, calls = self.run_main([], self.base_env(ENQUEUE_TOKEN="   "))
        self.assertEqual(code, 1)
        self.assertEqual(calls["enqueue"], [])

    def test_a_missing_read_token_is_fatal(self):
        env = self.base_env()
        del env["GITHUB_TOKEN"]
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                with contextlib.redirect_stdout(io.StringIO()):
                    gate.main([])

    def test_a_missing_trusted_main_sha_is_fatal(self):
        env = self.base_env()
        del env["TRUSTED_MAIN_SHA"]
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                with contextlib.redirect_stdout(io.StringIO()):
                    gate.main([])

    def test_every_log_line_is_machine_readable(self):
        _, out, _ = self.run_main([], self.base_env())
        events = [
            json.loads(line[len("auto-enqueue ") :])
            for line in out.splitlines()
            if line.startswith("auto-enqueue ")
        ]
        self.assertEqual(
            [event["step"] for event in events][:4],
            ["mode", "trusted_main", "pull", "files"],
        )
        self.assertEqual(events[-1]["step"], "enqueued")

    def test_no_token_is_ever_logged(self):
        _, out, _ = self.run_main([], self.base_env())
        self.assertNotIn("app-token", out)
        self.assertNotIn("read-token", out)


class ConstantsTests(unittest.TestCase):
    def test_the_branch_is_fixed_in_code_and_not_configurable(self):
        self.assertIn('REFRESH_BRANCH = "chore/refresh-results-index"', SOURCE)
        self.assertNotIn('getenv("REFRESH_BRANCH', SOURCE)
        self.assertNotIn('environ.get("REFRESH_BRANCH', SOURCE)
        # The allowlist and the required checks are constants for the same
        # reason: a workflow edit must not be able to widen them.
        for name in ("INDEX_FILES", "REQUIRED_CHECK_RUNS", "REQUIRED_COMMIT_STATUSES"):
            self.assertNotIn(f'environ.get("{name}', SOURCE)
            self.assertNotIn(f'getenv("{name}', SOURCE)

    def test_the_allowlist_is_exactly_the_two_generated_pages(self):
        self.assertEqual(gate.INDEX_FILES, ("RESULTS.md", "RESULTS.zh-CN.md"))
        self.assertEqual(set(gate.INDEX_LANGUAGES), set(gate.INDEX_FILES))

    def test_the_required_checks_are_split_by_reporting_mechanism(self):
        self.assertEqual(gate.REQUIRED_CHECK_RUNS, ("verify",))
        self.assertEqual(gate.REQUIRED_COMMIT_STATUSES, ("review-gate",))


if __name__ == "__main__":
    unittest.main()
