#!/usr/bin/env python3
"""Add the standing results-index refresh pull request to the merge queue.

`RESULTS.md` and `RESULTS.zh-CN.md` are generated from the scenario packages on
`main`. The refresh pull request that carries them contains no judgement: it is
either byte-for-byte what `build-results-index.py` produces from `main`, or it
is not. This program is what decides that, and it enqueues the pull request only
when every one of the following holds:

  * exactly one open pull request exists for the fixed refresh branch, it is not
    a draft, its base is `main`, and its head branch lives in this repository
    rather than a fork;
  * its complete file list — read through to the last page — is exactly the two
    generated index pages;
  * the content of both pages at the pull request head equals what the generator
    produces from the trusted `main` checkout this program is running in, and
    that checkout is still the tip of `main`;
  * the `verify` check run on the head has concluded `success`, and the
    `review-gate` commit status on the head is `success`. Anything else,
    including `skipped` and `neutral`, is not success;
  * the head has not moved between the first read and the enqueue, which is
    enforced twice: by re-reading it, and by passing it as `expectedHeadOid`.

Anything unproven fails closed. This program never approves, never merges,
never comments, and never touches a pull request other than the one on the fixed
branch.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parent))

from notify_review_escalation import GitHubClient, required_env  # noqa: E402


def _load_render_index():
    """Import the generator, whose file name is not a Python identifier.

    The comparison has to run the same code the `verify` check runs, so this
    loads `build-results-index.py` itself rather than reimplementing it.
    """
    path = Path(__file__).resolve().parent / "build-results-index.py"
    spec = importlib.util.spec_from_file_location("build_results_index", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load the results index generator from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_index


render_index = _load_render_index()


GRAPHQL_URL = "https://api.github.com/graphql"

# The one branch this program will ever act on. Deliberately a constant and not
# an environment variable: "the App only handles the refresh branch" is a
# property of the code, not of whoever configures the workflow.
REFRESH_BRANCH = "chore/refresh-results-index"
BASE_BRANCH = "main"

# The generated pages, and nothing else. A pull request that changes any other
# path — or that changes only one of these — is not the deterministic refresh
# and is left for a maintainer.
INDEX_FILES = ("RESULTS.md", "RESULTS.zh-CN.md")
# `render_index` takes the language, not the file name; this maps one to the
# other so the comparison cannot drift from the generator.
INDEX_LANGUAGES = {"RESULTS.md": "en", "RESULTS.zh-CN.md": "zh"}

# The required checks, split by the mechanism that reports them: `verify` is a
# check run produced by Actions, `review-gate` is a commit status posted by
# `scenario_review_flow.py`. Reading the wrong one would silently find nothing.
REQUIRED_CHECK_RUNS = ("verify",)
REQUIRED_COMMIT_STATUSES = ("review-gate",)

SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")

# Derived the same way as the merge-group gate's budget, so the two cannot drift
# apart: what the Actions token is allowed per repository per hour, divided by
# what one logical GET can actually cost once `GitHubClient.request` retries,
# times the share one run of this program may claim. A real run spends about a
# dozen requests; the budget exists so that a pathological one fails closed
# instead of eating the repository's hourly allowance.
REST_HOURLY_LIMIT = 1000
MAX_REQUEST_ATTEMPTS = 3
ENQUEUE_SHARE_OF_HOURLY_LIMIT = 0.45
REST_REQUEST_BUDGET = int(
    REST_HOURLY_LIMIT * ENQUEUE_SHARE_OF_HOURLY_LIMIT / MAX_REQUEST_ATTEMPTS
)
# The refresh job force-pushes the branch immediately before this runs, so
# `verify` and `review-gate` are normally still in flight. Waiting is bounded on
# both axes — wall clock and request budget — and running out of either is a
# refusal, not an enqueue. The daily scheduled run is the fallback for a refresh
# whose checks outlast the wait.
DEFAULT_WAIT_SECONDS = 480
DEFAULT_POLL_SECONDS = 30
# Pagination ceilings. These bound loops; they are not statements about how much
# data a legitimate refresh pull request has, which is two files.
MAX_PAGES = 20
PAGE_SIZE = 100

ENQUEUE_MUTATION = """
mutation($pullRequestId:ID!,$expectedHeadOid:GitObjectID!){
  enqueuePullRequest(input:{
    pullRequestId:$pullRequestId,
    expectedHeadOid:$expectedHeadOid
  }){
    mergeQueueEntry { id position state enqueuer { login } }
  }
}
"""


class EnqueueRefused(RuntimeError):
    """The pull request was not shown to be the deterministic refresh."""


class EnqueuePending(EnqueueRefused):
    """A required check has not answered yet; the same run may look again.

    Only "no verdict yet" is pending. A check that has answered anything other
    than success is a refusal, so waiting can never turn a red check green.
    """


class BudgetedClient(GitHubClient):
    """A client that refuses to spend more than one run's share of the quota.

    Running out is a refusal, never an enqueue: a pull request that could not be
    fully examined has not been shown to be safe.
    """

    def __init__(
        self, repository: str, token: str, budget: int = REST_REQUEST_BUDGET
    ) -> None:
        super().__init__(repository, token)
        self.budget = budget
        self.spent = 0

    def request(
        self, path: str, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> Any:
        if method != "GET":
            raise EnqueueRefused(
                f"refusing to issue a {method} request to {path}: this program "
                "only reads over REST"
            )
        self.spent += 1
        if self.spent > self.budget:
            raise EnqueueRefused(
                f"exceeded the budget of {self.budget} GitHub REST requests "
                "before the refresh pull request could be verified"
            )
        return super().request(path, method=method, payload=payload)


def log_event(step: str, **fields: Any) -> None:
    """One structured line per decision, so a run can be replayed from the log."""
    payload = {"step": step}
    payload.update(fields)
    print(f"auto-enqueue {json.dumps(payload, sort_keys=True, ensure_ascii=False)}")


def paginate_envelope(client: GitHubClient, path: str, key: str) -> list[dict[str, Any]]:
    """Page through an endpoint that wraps its list in an object.

    `/commits/{sha}/check-runs` answers `{"total_count": n, "check_runs": [...]}`
    rather than a bare list, so `GitHubClient.paginate` cannot read it.
    """
    separator = "&" if "?" in path else "?"
    collected: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        value = client.request(f"{path}{separator}per_page={PAGE_SIZE}&page={page}")
        if not isinstance(value, dict):
            raise EnqueueRefused(f"expected an object from {path}")
        items = value.get(key)
        if not isinstance(items, list):
            raise EnqueueRefused(f"expected {key} to be a list in the reply from {path}")
        collected.extend(item for item in items if isinstance(item, dict))
        if len(items) < PAGE_SIZE:
            return collected
    raise EnqueueRefused(f"pagination exceeded {MAX_PAGES} pages for {path}")


def paginate_list(client: GitHubClient, path: str) -> list[dict[str, Any]]:
    """Page through a list endpoint, bounded, refusing on anything unexpected."""
    separator = "&" if "?" in path else "?"
    collected: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        value = client.request(f"{path}{separator}per_page={PAGE_SIZE}&page={page}")
        if not isinstance(value, list):
            raise EnqueueRefused(f"expected a list from {path}")
        collected.extend(item for item in value if isinstance(item, dict))
        if len(value) < PAGE_SIZE:
            return collected
    raise EnqueueRefused(f"pagination exceeded {MAX_PAGES} pages for {path}")


def trusted_main_is_current(client: GitHubClient, local_sha: str) -> str:
    """The checkout this program renders from must still be the tip of `main`.

    The generated pages are compared against what this checkout produces, so a
    checkout that is behind `main` would compare the pull request against a
    stale generator input. A later push re-runs this workflow, so refusing here
    costs nothing.
    """
    if not SHA_RE.fullmatch(local_sha.lower()):
        raise EnqueueRefused(f"the local {BASE_BRANCH} commit {local_sha!r} is not a sha")
    commit = client.request(f"/commits/{BASE_BRANCH}")
    if not isinstance(commit, dict) or not isinstance(commit.get("sha"), str):
        raise EnqueueRefused(f"could not resolve the tip of {BASE_BRANCH}")
    remote_sha = str(commit["sha"]).lower()
    if remote_sha != local_sha.lower():
        raise EnqueueRefused(
            f"{BASE_BRANCH} moved to {remote_sha[:12]} after this run checked out "
            f"{local_sha[:12]}"
        )
    return remote_sha


def open_refresh_pull(client: GitHubClient, repository: str) -> dict[str, Any]:
    """The single open pull request for the refresh branch, or a refusal."""
    owner = repository.partition("/")[0]
    if not owner:
        raise EnqueueRefused(f"repository {repository!r} is not owner/name")
    pulls = paginate_list(
        client,
        f"/pulls?state=open&base={BASE_BRANCH}&head={owner}:{REFRESH_BRANCH}",
    )
    if not pulls:
        raise EnqueueRefused(
            f"no open pull request for {REFRESH_BRANCH}; nothing to enqueue"
        )
    if len(pulls) > 1:
        numbers = ", ".join(f"#{item.get('number')}" for item in pulls)
        raise EnqueueRefused(
            f"expected exactly one open pull request for {REFRESH_BRANCH}, found {numbers}"
        )
    return pulls[0]


def pull_head_sha(pull: dict[str, Any], repository: str) -> str:
    """Check the shape of the pull request itself and return its head sha."""
    number = pull.get("number")
    if not isinstance(number, int):
        raise EnqueueRefused("the pull request has no number")
    if pull.get("state") != "open":
        raise EnqueueRefused(f"PR #{number} is {pull.get('state')!r}, not open")
    if pull.get("draft"):
        raise EnqueueRefused(f"PR #{number} is a draft")
    if pull.get("merged"):
        raise EnqueueRefused(f"PR #{number} is already merged")
    base = pull.get("base") or {}
    if base.get("ref") != BASE_BRANCH:
        raise EnqueueRefused(f"PR #{number} targets {base.get('ref')!r}, not {BASE_BRANCH}")
    head = pull.get("head") or {}
    if head.get("ref") != REFRESH_BRANCH:
        raise EnqueueRefused(
            f"PR #{number} comes from {head.get('ref')!r}, not {REFRESH_BRANCH}"
        )
    head_repo = (head.get("repo") or {}).get("full_name")
    if head_repo != repository:
        raise EnqueueRefused(
            f"PR #{number} head lives in {head_repo!r}, not in {repository}"
        )
    head_sha = str(head.get("sha") or "").lower()
    if not SHA_RE.fullmatch(head_sha):
        raise EnqueueRefused(f"PR #{number} has no usable head sha")
    node_id = pull.get("node_id")
    if not isinstance(node_id, str) or not node_id:
        raise EnqueueRefused(f"PR #{number} has no node id to enqueue with")
    return head_sha


def check_file_set(client: GitHubClient, number: int) -> None:
    """The change set must be exactly the two generated pages, modified."""
    files = paginate_list(client, f"/pulls/{number}/files")
    names = [str(item.get("filename") or "") for item in files]
    if sorted(names) != sorted(INDEX_FILES):
        extra = sorted(set(names) - set(INDEX_FILES))
        missing = sorted(set(INDEX_FILES) - set(names))
        raise EnqueueRefused(
            f"PR #{number} changes {len(names)} file(s); expected exactly "
            f"{list(INDEX_FILES)}"
            + (f"; unexpected: {extra}" if extra else "")
            + (f"; absent: {missing}" if missing else "")
        )
    for item in files:
        status = item.get("status")
        if status != "modified":
            raise EnqueueRefused(
                f"PR #{number} lists {item.get('filename')!r} as {status!r}, "
                "expected 'modified'"
            )
    log_event("files", pull=number, files=sorted(names))


def head_file_text(client: GitHubClient, path: str, ref: str) -> str:
    """Read one file's bytes at a ref, refusing anything that is not a file."""
    value = client.request(f"/contents/{path}?ref={ref}")
    if not isinstance(value, dict):
        raise EnqueueRefused(f"{path} at {ref[:12]} is not a file")
    if value.get("type") != "file":
        raise EnqueueRefused(f"{path} at {ref[:12]} is a {value.get('type')!r}, not a file")
    if value.get("encoding") != "base64":
        raise EnqueueRefused(
            f"{path} at {ref[:12]} came back as {value.get('encoding')!r}, "
            "which this program cannot verify"
        )
    content = value.get("content")
    if not isinstance(content, str):
        raise EnqueueRefused(f"{path} at {ref[:12]} came back without content")
    try:
        raw = base64.b64decode(content, validate=False)
    except (binascii.Error, ValueError) as error:
        raise EnqueueRefused(f"{path} at {ref[:12]} is not decodable: {error}") from error
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EnqueueRefused(f"{path} at {ref[:12]} is not UTF-8: {error}") from error


def check_deterministic_content(
    client: GitHubClient, repo_root: Path, head_sha: str, number: int
) -> None:
    """Both pages at the head must equal what the generator produces here."""
    for filename in INDEX_FILES:
        language = INDEX_LANGUAGES[filename]
        try:
            expected = render_index(repo_root, language)
        except (OSError, ValueError) as error:
            raise EnqueueRefused(
                f"could not regenerate {filename} from the trusted checkout: {error}"
            ) from error
        actual = head_file_text(client, filename, head_sha)
        if actual != expected:
            raise EnqueueRefused(
                f"PR #{number} does not carry the generator's output for {filename}: "
                f"{len(actual)} bytes at the head against {len(expected)} regenerated"
            )
        log_event("content", pull=number, file=filename, bytes=len(expected), matches=True)


def check_required_check_runs(client: GitHubClient, head_sha: str) -> None:
    """Every required check run must exist and have concluded `success`."""
    runs = paginate_envelope(client, f"/commits/{head_sha}/check-runs", "check_runs")
    for name in REQUIRED_CHECK_RUNS:
        matching = [run for run in runs if run.get("name") == name]
        if not matching:
            raise EnqueuePending(
                f"the required check run {name!r} has not reported on {head_sha[:12]}"
            )
        for run in matching:
            if run.get("status") != "completed":
                raise EnqueuePending(
                    f"the required check run {name!r} on {head_sha[:12]} is "
                    f"{run.get('status')!r}, not completed"
                )
            if run.get("conclusion") != "success":
                raise EnqueueRefused(
                    f"the required check run {name!r} on {head_sha[:12]} concluded "
                    f"{run.get('conclusion')!r}; only 'success' counts"
                )
        log_event("check_run", name=name, head=head_sha, runs=len(matching), conclusion="success")


def check_required_commit_statuses(client: GitHubClient, head_sha: str) -> None:
    """Every required commit status must be present and `success`."""
    combined = client.request(f"/commits/{head_sha}/status")
    if not isinstance(combined, dict):
        raise EnqueueRefused(f"could not read commit statuses for {head_sha[:12]}")
    statuses = combined.get("statuses")
    if not isinstance(statuses, list):
        raise EnqueueRefused(f"commit statuses for {head_sha[:12]} are not a list")
    by_context = {
        str(item.get("context")): item for item in statuses if isinstance(item, dict)
    }
    for context in REQUIRED_COMMIT_STATUSES:
        status = by_context.get(context)
        if status is None:
            raise EnqueuePending(
                f"the required status {context!r} has not reported on {head_sha[:12]}"
            )
        if status.get("state") == "pending":
            raise EnqueuePending(
                f"the required status {context!r} on {head_sha[:12]} is still pending"
            )
        if status.get("state") != "success":
            raise EnqueueRefused(
                f"the required status {context!r} on {head_sha[:12]} is "
                f"{status.get('state')!r}; only 'success' counts"
            )
        log_event("commit_status", context=context, head=head_sha, state="success")


def reread_head(client: GitHubClient, number: int, expected_head: str) -> None:
    """The head must not have moved while the pull request was being verified."""
    pull = client.request(f"/pulls/{number}")
    if not isinstance(pull, dict):
        raise EnqueueRefused(f"could not re-read PR #{number} before enqueueing")
    current = str((pull.get("head") or {}).get("sha") or "").lower()
    if current != expected_head:
        raise EnqueueRefused(
            f"PR #{number} moved from {expected_head[:12]} to {current[:12] or '?'} "
            "while it was being verified"
        )
    if pull.get("state") != "open" or pull.get("merged"):
        raise EnqueueRefused(f"PR #{number} is no longer open")


def enqueue(token: str, node_id: str, expected_head: str) -> dict[str, Any]:
    """Call `enqueuePullRequest`. The only write this program ever performs."""
    payload = json.dumps(
        {
            "query": ENQUEUE_MUTATION,
            "variables": {"pullRequestId": node_id, "expectedHeadOid": expected_head},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "agent-hi-tax-auto-enqueue",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise EnqueueRefused(f"enqueue request failed: {error.code} {detail}") from error
    except Exception as error:  # noqa: BLE001 - any transport failure fails closed
        raise EnqueueRefused(f"enqueue request failed: {error}") from error

    for item in body.get("errors") or []:
        raise EnqueueRefused(f"enqueue refused by GitHub: {item.get('message')}")
    entry = ((body.get("data") or {}).get("enqueuePullRequest") or {}).get(
        "mergeQueueEntry"
    )
    if not isinstance(entry, dict) or not entry.get("id"):
        raise EnqueueRefused("GitHub accepted the enqueue request but returned no entry")
    return entry


def verify(
    client: GitHubClient, repository: str, repo_root: Path, trusted_main: str
) -> tuple[dict[str, Any], str]:
    """Run every check. Returns the pull request and its verified head sha."""
    trusted_main_is_current(client, trusted_main)
    log_event("trusted_main", sha=trusted_main, current=True)

    pull = open_refresh_pull(client, repository)
    head_sha = pull_head_sha(pull, repository)
    number = int(pull["number"])
    log_event(
        "pull",
        pull=number,
        head=head_sha,
        base=BASE_BRANCH,
        branch=REFRESH_BRANCH,
        fork=False,
    )

    check_file_set(client, number)
    check_deterministic_content(client, repo_root, head_sha, number)
    check_required_check_runs(client, head_sha)
    check_required_commit_statuses(client, head_sha)
    reread_head(client, number, head_sha)
    log_event("verified", pull=number, head=head_sha)
    return pull, head_sha


def verify_with_wait(
    client: GitHubClient,
    repository: str,
    repo_root: Path,
    trusted_main: str,
    wait_seconds: float,
    poll_seconds: float,
    sleep=time.sleep,
    clock=time.monotonic,
) -> tuple[dict[str, Any], str]:
    """Verify, waiting only for checks that have not answered yet.

    Every pass re-reads everything, so a head that moves mid-wait is caught by
    the same checks as a head that moved before the wait started.
    """
    deadline = clock() + wait_seconds
    attempt = 0
    while True:
        attempt += 1
        try:
            return verify(client, repository, repo_root, trusted_main)
        except EnqueuePending as pending:
            remaining = deadline - clock()
            if remaining < poll_seconds:
                raise EnqueueRefused(
                    f"{pending} — still not decided after waiting "
                    f"{wait_seconds:.0f}s over {attempt} attempt(s)"
                ) from pending
            log_event(
                "waiting",
                attempt=attempt,
                reason=str(pending),
                seconds_left=int(remaining),
                requests=getattr(client, "spent", None),
            )
            sleep(poll_seconds)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify and report, but never call enqueuePullRequest",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="the trusted main checkout the generated pages are compared against",
    )
    parser.add_argument(
        "--wait-seconds",
        type=float,
        default=DEFAULT_WAIT_SECONDS,
        help="how long to wait for required checks that have not answered yet",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=DEFAULT_POLL_SECONDS,
        help="how long to sleep between attempts while waiting",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repository = required_env("REPOSITORY")
    token = required_env("GITHUB_TOKEN")
    trusted_main = required_env("TRUSTED_MAIN_SHA")

    enabled = os.environ.get("RESULTS_AUTO_ENQUEUE_ENABLED", "").strip().lower()
    live = enabled == "true" and not args.dry_run
    if enabled not in {"true", "false", ""}:
        print(
            "::error title=Results auto-enqueue::"
            f"RESULTS_AUTO_ENQUEUE_ENABLED is {enabled!r}; expected 'true' or 'false'"
        )
        return 1
    log_event("mode", enabled=enabled or "false", dry_run=not live, repository=repository)

    client = BudgetedClient(repository, token)
    try:
        pull, head_sha = verify_with_wait(
            client,
            repository,
            args.repo_root.resolve(),
            trusted_main,
            args.wait_seconds,
            args.poll_seconds,
        )
    except EnqueueRefused as error:
        # Not an error: refusing is the normal outcome whenever the standing
        # pull request is absent, still building, or not the deterministic
        # refresh. It is reported as a notice so a red run always means a bug.
        log_event("refused", reason=str(error), requests=client.spent)
        print(f"::notice title=Results auto-enqueue::{error}")
        return 0
    except Exception as error:  # noqa: BLE001 - unknown state never enqueues
        log_event("failed", reason=str(error), requests=client.spent)
        print(f"::error title=Results auto-enqueue::could not verify: {error}")
        return 1

    number = int(pull["number"])
    if not live:
        log_event(
            "dry_run",
            pull=number,
            head=head_sha,
            would_enqueue=True,
            requests=client.spent,
        )
        print(
            f"::notice title=Results auto-enqueue::dry run: PR #{number} at "
            f"{head_sha[:12]} satisfies every check and would be enqueued"
        )
        return 0

    enqueue_token = required_env("ENQUEUE_TOKEN")
    try:
        entry = enqueue(enqueue_token, str(pull["node_id"]), head_sha)
    except EnqueueRefused as error:
        log_event("enqueue_refused", pull=number, head=head_sha, reason=str(error))
        print(f"::error title=Results auto-enqueue::{error}")
        return 1

    log_event(
        "enqueued",
        pull=number,
        head=head_sha,
        entry=entry.get("id"),
        position=entry.get("position"),
        state=entry.get("state"),
        enqueuer=(entry.get("enqueuer") or {}).get("login"),
        requests=client.spent,
    )
    print(
        f"::notice title=Results auto-enqueue::PR #{number} at {head_sha[:12]} "
        f"entered the merge queue in position {entry.get('position')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
