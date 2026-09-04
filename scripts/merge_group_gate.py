#!/usr/bin/env python3
"""Report `review-gate` for a merge group, evaluated from trusted `main`.

A merge group is a temporary branch GitHub builds from the base branch plus one
commit per queued pull request. The event payload names only the last pull
request, so the source pull requests are recovered structurally instead:

  * the first-parent chain from the merge group head down to the base branch
    tip yields one merge commit per queued pull request, and each of those
    commits has the source pull request head as its *second* parent;
  * GraphQL `repository.mergeQueue.entries` maps each of those merge commits
    (`headCommit.oid`) back to its pull request number and enqueued head.

Both views must agree, and every commit in the chain must be accounted for.
Anything unexplained fails the gate rather than passing it. This program never
writes to GitHub: no comments, no review requests, no statuses, no email.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parent))

from notify_review_escalation import GitHubClient, required_env  # noqa: E402
from review_gate import ParsedVerdict, evaluate_review_gate  # noqa: E402
from scenario_review_flow import (  # noqa: E402
    allowed_assignment_families,
    assigned_verdict,
    assignment_records,
    assignment_supported,
    capabilities_for,
    changes_protected_protocol,
    choose_candidates,
    is_scenario_pull,
    latest_assignment,
    load_config,
    maintainer_approved,
    matching_capability,
    previous_stage_verdict,
    pull_files,
    scenario_content_unchanged,
)


GRAPHQL_URL = "https://api.github.com/graphql"
# The queue is read page by page until GitHub says there is no next page, so the
# page size is a request-shaping detail and carries no correctness meaning: it
# is deliberately not tied to the walk limit below.
QUEUE_PAGE_SIZE = 100
# Bound the pagination loop so a server that never clears `hasNextPage` cannot
# spin forever. At 100 entries per page this covers 10,000 queue entries.
MAX_QUEUE_PAGES = 100
# A guard on the first-parent walk, not a claim about how long a merge group may
# be. GitHub's documented "maximum entries to build" cap describes concurrent
# builds, not the length of this chain, so this is set well above any queue this
# repository will run and only exists to stop a malformed chain from looping.
MAX_GROUP_ENTRIES = 1000

QUEUE_QUERY = """
query($owner:String!,$name:String!,$branch:String!,$page:Int!,$after:String){
  repository(owner:$owner,name:$name){
    mergeQueue(branch:$branch){
      entries(first:$page, after:$after){
        pageInfo { hasNextPage endCursor }
        nodes {
          position
          state
          headCommit { oid }
          baseCommit { oid }
          pullRequest { number headRefOid }
        }
      }
    }
  }
}
"""


class GateFailure(RuntimeError):
    """The gate could not be satisfied, or could not be proven satisfied."""


def base_branch_name(base_ref: str) -> str:
    return base_ref.split("refs/heads/", 1)[-1]


def graphql(token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "agent-hi-tax-merge-group-gate",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise GateFailure(f"GraphQL request failed: {error.code} {detail}") from error
    except Exception as error:  # noqa: BLE001 - any transport failure fails closed
        raise GateFailure(f"GraphQL request failed: {error}") from error


def group_commits(
    client: GitHubClient, head_sha: str, base_tip: str
) -> list[tuple[str, str]]:
    """Walk first parents from the group head to the base tip.

    Returns ``[(group_commit_sha, source_pull_request_head_sha), ...]`` in queue
    order. Every commit on the chain must be a two-parent merge commit; a chain
    that does not reach the base tip is a fail, never a pass.
    """
    chain: list[tuple[str, str]] = []
    sha = head_sha
    for _ in range(MAX_GROUP_ENTRIES + 1):
        if sha.lower() == base_tip.lower():
            return list(reversed(chain))
        commit = client.request(f"/commits/{sha}")
        if not isinstance(commit, dict):
            raise GateFailure(f"Could not read merge group commit {sha[:12]}")
        parents = [str(item.get("sha") or "") for item in commit.get("parents", [])]
        if len(parents) != 2 or not all(parents):
            raise GateFailure(
                f"Merge group commit {sha[:12]} does not have exactly two parents"
            )
        chain.append((sha, parents[1]))
        sha = parents[0]
    raise GateFailure(
        f"Merge group chain did not reach {base_tip[:12]} within {MAX_GROUP_ENTRIES} commits"
    )


def queue_entries_by_commit(
    token: str, repository: str, branch: str
) -> dict[str, dict[str, Any]]:
    owner, _, name = repository.partition("/")
    mapping: dict[str, dict[str, Any]] = {}
    cursor: str | None = None
    for _ in range(MAX_QUEUE_PAGES):
        response = graphql(
            token,
            QUEUE_QUERY,
            {
                "owner": owner,
                "name": name,
                "branch": branch,
                "page": QUEUE_PAGE_SIZE,
                "after": cursor,
            },
        )
        # Partial data plus errors is normal: `mergeQueue.configuration` is not
        # readable by the Actions token. Only errors on the paths this gate
        # reads may fail it.
        for error in response.get("errors") or []:
            path = [str(item) for item in (error.get("path") or [])]
            if "configuration" in path:
                continue
            raise GateFailure(
                f"GraphQL error on {'.'.join(path)}: {error.get('message')}"
            )
        queue = (
            ((response.get("data") or {}).get("repository") or {}).get("mergeQueue")
            or {}
        )
        container = queue.get("entries") or {}
        entries = container.get("nodes")
        if not isinstance(entries, list):
            raise GateFailure(f"Merge queue for {branch} is not readable")
        for node in entries:
            commit = (node.get("headCommit") or {}).get("oid")
            if commit:
                mapping[str(commit).lower()] = node
        # The queue is only fully read when GitHub says so. A missing or
        # malformed `pageInfo` means the map may be incomplete, and an
        # incomplete map would make a real group commit look unexplained, so
        # refuse rather than guess.
        page_info = container.get("pageInfo")
        if not isinstance(page_info, dict) or not isinstance(
            page_info.get("hasNextPage"), bool
        ):
            raise GateFailure(
                f"Merge queue for {branch} did not report whether more entries exist"
            )
        if not page_info["hasNextPage"]:
            return mapping
        cursor = page_info.get("endCursor")
        if not isinstance(cursor, str) or not cursor:
            raise GateFailure(
                f"Merge queue for {branch} reported more entries without a cursor"
            )
    raise GateFailure(
        f"Merge queue for {branch} did not finish within {MAX_QUEUE_PAGES} pages"
    )


def source_pull_requests(
    client: GitHubClient, token: str, repository: str, head_sha: str, base_ref: str
) -> list[dict[str, Any]]:
    """Identify every pull request in the merge group, or fail closed."""
    branch = base_branch_name(base_ref)
    tip = client.request(f"/commits/{branch}")
    if not isinstance(tip, dict) or not tip.get("sha"):
        raise GateFailure(f"Could not resolve the tip of {branch}")
    chain = group_commits(client, head_sha, str(tip["sha"]))
    if not chain:
        raise GateFailure("Merge group contains no pull request commits")
    entries = queue_entries_by_commit(token, repository, branch)

    resolved: list[dict[str, Any]] = []
    for group_sha, pull_head in chain:
        entry = entries.get(group_sha.lower())
        if entry is None:
            raise GateFailure(
                f"Merge group commit {group_sha[:12]} has no merge queue entry"
            )
        pull_request = entry.get("pullRequest")
        if not pull_request or not pull_request.get("number"):
            raise GateFailure(
                f"Merge queue entry for {group_sha[:12]} names no pull request"
            )
        enqueued_head = str(pull_request.get("headRefOid") or "").lower()
        if not enqueued_head or enqueued_head != pull_head.lower():
            raise GateFailure(
                f"PR #{pull_request['number']} head changed after it was queued"
            )
        resolved.append(
            {"number": int(pull_request["number"]), "head": enqueued_head}
        )
    return resolved


def evaluate_pull(
    client: GitHubClient, config: dict[str, Any], pull: dict[str, Any]
) -> tuple[bool, str]:
    """Read-only mirror of the pull-request review gate. Never writes."""
    number = int(pull["number"])
    author = str(pull["user"]["login"]).lower()
    head = str(pull["head"]["sha"])

    files = pull_files(client, number)
    if not is_scenario_pull(files):
        return True, "not a new scenario PR; review-gate does not apply"
    if changes_protected_protocol(files):
        return False, "scenario data and protected protocol changes must be split"

    comments = client.comments(number)
    reviews = client.reviews(number)
    records = comments + reviews
    assignments = assignment_records(comments)
    cache: dict[str, dict[str, str]] = {}
    carried: list[ParsedVerdict] = []

    stages: dict[str, Any] = {}
    for stage in ("first", "second"):
        if stage == "first":
            candidates = [
                capabilities_for(config, login)[0]
                for login in config["reviewers"]
                if login.lower() not in {author, "keting"}
            ]
        else:
            candidates = choose_candidates(config, stages["first"][1], author)
        assignment = latest_assignment(assignments, stage, head)
        if assignment and not assignment_supported(config, assignment, candidates):
            return False, f"{stage} review assignment is no longer valid"
        verdict = reason = None
        if assignment:
            verdict, reason = assigned_verdict(records, assignment, head)
        if verdict is None and (reason is None or (assignment and assignment.head is None)):
            prior_assignment, prior = previous_stage_verdict(
                records, assignments, stage, head
            )
            if prior and prior.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
                return False, f"unresolved privacy verdict on the {stage} review"
            if prior_assignment and prior and prior.verdict == "APPROVE":
                target = assignment or prior_assignment
                capability = matching_capability(config, target, candidates)
                same = (
                    assignment is None
                    or assignment.reviewer.lower() == prior_assignment.reviewer.lower()
                )
                allowed = allowed_assignment_families(config, target) | {"human"}
                if (
                    same
                    and capability
                    and prior.model_family in allowed
                    and scenario_content_unchanged(
                        client, files, prior.reviewed_head, head, cache
                    )
                ):
                    assignment = prior_assignment
                    verdict = prior
                    carried.append(prior)
        if assignment is None:
            return False, f"no {stage} reviewer is assigned"
        if verdict is None:
            return False, f"{stage} verdict is missing or rejected: {reason or 'absent'}"
        if verdict.verdict == "PRIVACY-CONCERN-RAISED-PRIVATELY":
            return False, f"unresolved privacy verdict on the {stage} review"
        if verdict.verdict != "APPROVE":
            return False, f"{stage} verdict is {verdict.verdict}"
        expected = allowed_assignment_families(config, assignment) | {"human"}
        if verdict.model_family not in expected:
            return False, f"{stage} verdict did not use its assigned model family"
        stages[stage] = (assignment, verdict)

    gate = evaluate_review_gate(
        records,
        head,
        expected_reviewers=(
            stages["first"][0].reviewer,
            stages["second"][0].reviewer,
        ),
        carried_verdicts=carried,
    )
    if not gate["eligible"]:
        return False, "two different reviewers and model families are required"
    if not maintainer_approved(config, reviews, author, head):
        return False, "no non-author maintainer has formally approved this head"
    return True, "two independent APPROVE verdicts and a maintainer approval"


def main(argv: list[str] | None = None) -> int:
    repository = required_env("REPOSITORY")
    token = required_env("GITHUB_TOKEN")
    head_sha = required_env("MERGE_GROUP_HEAD_SHA")
    base_ref = required_env("MERGE_GROUP_BASE_REF")
    client = GitHubClient(repository, token)

    try:
        pulls = source_pull_requests(client, token, repository, head_sha, base_ref)
    except GateFailure as error:
        print(f"::error title=Merge group review-gate::{error}")
        return 1

    print(f"merge group {head_sha[:12]} contains {len(pulls)} pull request(s)")
    failures: list[str] = []
    config = load_config()
    for item in pulls:
        number = item["number"]
        try:
            pull = client.pull(number)
            if str(pull["head"]["sha"]).lower() != item["head"]:
                raise GateFailure("head changed after it was queued")
            ok, reason = evaluate_pull(client, config, pull)
        except GateFailure as error:
            ok, reason = False, str(error)
        except Exception as error:  # noqa: BLE001 - unknown state never passes
            ok, reason = False, f"could not evaluate: {error}"
        print(f"  PR #{number}: {'pass' if ok else 'FAIL'} - {reason}")
        if not ok:
            failures.append(f"PR #{number}: {reason}")

    if failures:
        for failure in failures:
            print(f"::error title=Merge group review-gate::{failure}")
        return 1
    print("merge group review-gate: every source pull request satisfies the gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
