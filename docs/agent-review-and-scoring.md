# Agent entry point for PR review and points

**English** | [中文](agent-review-and-scoring.zh-CN.md)

> Goal: after receiving an action and one Agent Hi Tax Pull Request URL, a capable Agent can discover the repository rules, perform an independent review, or calculate and submit the post-merge points update without requiring local paths or copied instructions.

This page is the routing entry point, not a replacement for the detailed rules. [CONTRIBUTING](../CONTRIBUTING.md), the base branch's [review process](review-process.md), and the applicable version of [wanted scenarios and points](wanted-scenarios.md) remain authoritative.

## Minimal input contract

The variable input is one PR URL in this repository. Pair it with one action:

```text
Review and post a verdict for <PR URL> using the repository's Agent review entry point.
```

or, after the PR is merged:

```text
Calculate the points for <merged PR URL> and submit the ledger update using the repository's Agent points entry point.
```

If the user supplies only the URL, route by authoritative PR state:

- an open, non-draft PR enters the review action;
- a merged PR enters the points action;
- a draft PR or a closed but unmerged PR is reported as not eligible, and the Agent stops without publishing or changing the repository.

The prompt does not need to copy policy text, provide an absolute local path, or include a token, email address, or other credential. The Agent must derive the owner, repository, PR number, head SHA, base SHA, contributor, task or claim, checks, and changed files from the URL and repository state.

This contract assumes the Agent can:

- read the PR, Git repository, GitHub API, and linked claim or proposal;
- check out or otherwise inspect the exact PR head;
- open every public image at original size;
- run repository verification commands;
- for review, publish an issue-style PR comment;
- for points, create a branch, commit, push it, and open a PR.

If a required capability or permission is unavailable, the Agent reports the exact boundary and stops. It must not infer evidence it could not inspect or claim that a comment, commit, or PR was submitted when it was not.

## Action: review a PR

The Agent performs these steps in order:

1. Resolve the PR URL and record its current head SHA, base SHA, author, changed files, draft state, CI checks, and mergeability. Review the exact head, not a moving branch name.
2. Before reading any existing review or PR conversation comment, read from the PR's base branch: `CONTRIBUTING.md`, `docs/review-process.md`, `.github/CODEOWNERS`, the applicable task in `docs/wanted-scenarios.md`, and any linked claim or proposal. Read the PR body, diff, and submitted files, but keep other reviewers' findings unopened until this review is published.
3. Run `./scripts/verify-all.sh` at the PR head. Treat a green check as structural evidence only, never as a substitute for review.
4. Open every published image one by one at original size. Check redaction, then reconcile images, `RESULTS.csv`, `manifest.yaml`, attempt results, events or usage records, hashes, the package README, and the PR claims.
5. Apply the L1/L2/L3 rules and reach an independent verdict. For AI-assisted review, record the Agent product, exact model, and reasoning effort; use `not exposed` rather than guessing.
6. Include a points recommendation in `Advisory`: identify the task, candidate value, stacking or non-stacking decision, and evidence boundary. This is advice only; the maintainer decides and records the award.
7. Publish the structured verdict comment from `docs/review-process.md`. An AI reviewer posts a comment only and never uses GitHub's formal **Approve** or **Request changes** action.
8. After publishing, the Agent may read other verdict comments and report the aggregate gate: required independent verdicts, formal CODEOWNER approval, CI, resolved threads, and merge state. A review is redone if the PR head changes.

For a suspected sensitive disclosure, follow the privacy exception in `docs/review-process.md`: do not quote or locate the value publicly; raise the detail through the private channel.

### Review completion output

The Agent reports:

- reviewed head SHA and template commit;
- verdict and review-comment URL;
- verification result and evidence boundaries;
- points recommendation;
- remaining project-process and GitHub mechanical gates.

## Action: calculate and submit points

This action starts only after the target PR is merged. An approval or an open PR is not enough.

1. Resolve the merged PR URL and record its merge time, merge commit, contributor, scenario identity, task or claim, route, evidence level, and delivered files.
2. Read the points rules and ledger in `docs/wanted-scenarios.md` as they stood when the PR merged. Read the claim or proposal and the review Advisories, but recompute the award; reviewer suggestions are inputs, not decisions.
3. Match every plausible task and pricing bucket. Apply decay, pair completion, proposal pricing, adapter and probe add-ons, and the documented stacking rules. Do not silently stack two ordinary task prices. If the case is genuinely ambiguous, stop for one explicit maintainer decision and record that decision in the ledger note.
4. Confirm whether evidence that was available was omitted. Honest `self_reported`, `not_exposed`, or confounded evidence does not reduce points by itself; evidence that could have been supplied delays the award under the points rules.
5. Append one row to both `docs/wanted-scenarios.md` and `docs/wanted-scenarios.zh-CN.md`. Include date, contributor, task, merged PR, points, claim or proposal when relevant, and enough rationale to preserve normalization and non-stacking decisions. Never edit a historical ledger row; corrections use a new offsetting row.
6. Create a work branch from current `main`, run `./scripts/verify-all.sh` and `git diff --check`, commit only the ledger files, push the branch, and open a PR. Never push directly to `main` and never use an admin bypass to skip required PR, CI, or review gates.
7. Report the ledger commit and PR URL. After that PR is normally merged, verify that both ledger rows are present on `main` and that the worktree contains no uncommitted files created by the task.

### Points completion output

The Agent reports:

- awarded task and points, including stacking or decay rationale;
- merged source PR and contributor;
- exact English and Chinese ledger rows;
- verification results;
- ledger commit and PR URL;
- any maintainer decision still required.

## Boundaries

- One PR URL is enough to locate the target; it is not permission to change unrelated settings, permissions, secrets, branches, issues, or other PRs.
- Review and scoring are separate actions. A review Advisory does not update the ledger, and a merged PR does not receive points until the bilingual ledger update is merged.
- The maintainer performs the formal GitHub approval, final merge, points adjudication, and any private-evidence check. Agents provide review comments and repository changes through normal PRs.
