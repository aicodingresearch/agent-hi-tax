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

### A draft PR is never reviewed

Review eligibility is a property of the PR, not of how the review was requested. **A draft PR is not eligible under any invocation** — URL-only routing, the recommended review input below, or an explicit human instruction naming the PR. The Agent reports the draft state, names the one thing that would unblock it (the contributor marking the PR Ready for review), and stops without publishing a comment or changing the repository. Publishing a verdict on a draft and disclaiming the draft state inside the comment is not an accepted substitute; that path still puts a verdict on the record that the gate then has to discount by hand.

Two existing rules make this a consequence rather than a new restriction. [Every review names the head commit it was performed at](review-process.md#decision-rules) and is redone after a new commit, so a verdict written against a still-moving draft is scheduled to be discarded before it is written. And [CONTRIBUTING](../CONTRIBUTING.md#submitting-a-pull-request) asks the contributor to mark a PR Ready for review only after automated verification passes and every screenshot has been visually re-checked — reviewing earlier spends review effort on checks the contributor still owes.

A maintainer may of course look at a draft and comment on it. That is a pre-review consultation: ordinary comments, never a structured verdict comment, and it counts toward no review gate.

There are two different URL roles. A **target PR URL** identifies work and is sufficient for automatic routing. This **runbook URL** identifies instructions, not a target; if it is the only URL and the surrounding context does not identify exactly one PR, the Agent asks for the target PR URL rather than guessing.

### Recommended review input

URL-only invocation remains valid, but the recommended review prompt also records the reviewer runtime explicitly:

```text
Action: independently review and post a verdict comment
Target PR: https://github.com/aicodingresearch/agent-hi-tax/pull/<number>
Reviewer Agent: <product, for example Claude Code or Codex>
Reviewer model: <exact model, for example claude-opus-5 or gpt-5.6-sol>
Reasoning effort: <exact effort, for example xhigh>

Follow the Agent review and scoring entry point in this repository. Review the
exact current head. Do not read existing review comments or reviewer findings
before publishing this independent verdict. Post a comment only; do not use
GitHub's formal Approve or Request changes action.
```

The Agent product, model, and effort must describe the actual runtime. Writing them in a prompt does not switch or configure the runtime. If the supplied identity conflicts with what the product exposes, the Agent reports the mismatch and uses the observed value; if unavailable, it writes `not exposed` rather than copying or guessing.

For post-merge points, the recommended input is:

```text
Action: calculate points and submit the bilingual ledger update
Target PR: https://github.com/aicodingresearch/agent-hi-tax/pull/<merged-number>

Follow the Agent review and scoring entry point in this repository. Recompute
eligibility and points, check for an existing row or pending ledger PR first,
and do not modify the repository for any non-RECORDED outcome.
```

The prompt does not need to copy policy text, provide an absolute local path, or include a token, email address, or other credential. The Agent must derive the owner, repository, PR number, head SHA, base SHA, contributor, task or claim, checks, and changed files from the URL and repository state.

This contract assumes the Agent can:

- read the PR, Git repository, GitHub API, and linked claim or proposal;
- check out or otherwise inspect the exact PR head;
- open every public image at original size;
- run repository verification commands;
- for review, publish an issue-style PR comment;
- for points, create a branch, commit, push it, and open a PR.

If a required capability or permission is unavailable, the Agent reports the exact boundary and stops. It must not infer evidence it could not inspect or claim that a comment, commit, or PR was submitted when it was not.

## PR type triage

Before applying either action, classify the target by delivered behavior, not by author identity:

- **Scenario-data PR**: adds or changes a scenario package under `runs/` and its generated indexes. Use the data-review dimensions and L1/L2 process; it may be eligible for points after merge.
- **Protocol, governance, software, or documentation PR**: changes rules, prompts, templates, scripts, workflows, security policy, process documentation, or ordinary documentation without delivering a scenario. Use L3 when the authoritative review process says it applies; otherwise use a maintainer-directed code/documentation review. It is normally not eligible for scenario points.
- **Points-ledger PR**: primarily adds or corrects entries in the points ledger for an already merged source PR. Review the ledger operation itself under maintainer control. The ledger PR never earns points for recording points.
- **Mixed PR**: delivers more than one of the above. Apply every relevant review dimension and the highest-risk decision path; do not silently assume it is an ordinary L1 data PR.

For scenario-data PRs, L1 requires two independent structured reviews and L2 adds the documented escalation. L3 and maintainer-directed non-data reviews do not acquire an automatic two-review majority requirement merely because they are open PRs. GitHub's formal approval, CI, and thread-resolution gates remain separate in every case.

## Action: review a PR

The Agent performs these steps in order:

1. Resolve the PR URL and record its current head SHA, base SHA, author, changed files, draft state, CI checks, and mergeability. Review the exact head, not a moving branch name.
2. For an initial independent review, before reading any existing review or PR conversation comment, read from the PR's base branch: `CONTRIBUTING.md`, `docs/review-process.md`, `.github/CODEOWNERS`, the applicable task in `docs/wanted-scenarios.md`, and any linked claim or proposal. Read the PR body, diff, and submitted files, but keep other reviewers' findings unopened until this review is published. For an explicitly requested same-reviewer re-review, first resolve the current PR state, then read that reviewer's prior verdict and the contributor responses needed to verify the revision; disclose this and do not claim another independent review.
3. Classify the PR using [PR type triage](#pr-type-triage), then select review dimensions:
   - scenario data: redaction, cross-evidence consistency, protocol conformance, and restraint of claims;
   - protocol/software/documentation: behavioral correctness, conflicts with authoritative rules, bilingual and link consistency, and executable/security boundaries;
   - points ledger: source PR eligibility, recomputed points and non-stacking rationale, bilingual append-only consistency and duplicate prevention, and verification;
   - mixed: combine all applicable dimensions and state the decision level explicitly.
4. Run `./scripts/verify-packages.sh` at the PR head — or `./scripts/verify-all.sh` when the PR touches the generated indexes — plus any focused checks required by the changed files. Treat a green check as structural evidence only, never as a substitute for review.
5. For scenario-data or mixed PRs that publish evidence, open every published image one by one at original size. Reconcile images, `RESULTS.csv`, `manifest.yaml`, attempt results, events or usage records, hashes, the package README, and the PR claims. Do not impose this data-package checklist on a PR that publishes no scenario evidence.
6. Reach an independent verdict under the applicable level. For AI-assisted review, record the Agent product, exact model, and reasoning effort; use `not exposed` rather than guessing.
7. For an eligible scenario-data delivery, include a points recommendation in `Advisory`: identify the task, candidate value, stacking or non-stacking decision, and evidence boundary. For protocol, documentation, software, or ledger-only PRs, write `points: not_applicable` unless an explicit priced task says otherwise.
8. Publish the applicable structured verdict comment. Scenario-data reviews use the template in `docs/review-process.md`. A non-data review retains the version, verdict, head, reviewer, date, findings, verification, `Could not verify`, and Advisory fields, but uses the dimensions above instead of manufacturing `n/a` rows in the data-evidence table. An AI reviewer posts a comment only and never uses GitHub's formal **Approve** or **Request changes** action.
9. On re-review after a contributor update, preserve the earlier verdict comment and publish a new structured follow-up after the update. Never edit the earlier comment to change its verdict or findings. The follow-up links the earlier verdict in `Supersedes`, identifies the state re-reviewed (including a PR-description-only update when the head is unchanged), and discloses that the preceding discussion was read. Count it as the same reviewer, not as another independent L1 review.
10. After publishing, the Agent may read other verdict comments and report the aggregate gate for this PR type: required independent verdicts, formal CODEOWNER approval, CI, resolved threads, and merge state. A review is redone if the PR head changes. For each reviewer, use the latest valid superseding verdict for the reviewed state while retaining earlier comments as history.

For a suspected sensitive disclosure, follow the privacy exception in `docs/review-process.md`: do not quote or locate the value publicly; raise the detail through the private channel.

### Review completion output

The Agent reports:

- reviewed head SHA and template commit;
- verdict and review-comment URL;
- verification result and evidence boundaries;
- points recommendation or `not_applicable`;
- remaining project-process and GitHub mechanical gates.

## Action: calculate and submit points

This action starts only after the target PR is merged. An approval or an open PR is not enough.

1. Resolve the merged PR URL and record its merge time, merge commit, contributor, delivered files, and PR type.
2. Perform the idempotency check before calculating or writing anything:
   - search both current ledgers for the exact source PR;
   - search open ledger-update PRs for a pending row for that source PR;
   - if matching rows already exist in both ledgers, return `ALREADY_RECORDED` and stop;
   - if a matching ledger PR is open, return `ALREADY_PENDING` with its URL and stop;
   - if the English and Chinese ledgers disagree, return `LEDGER_INCONSISTENT` and request maintainer direction rather than adding another ordinary row.
3. Apply eligibility exits. A points-ledger PR returns `NOT_APPLICABLE` so the workflow cannot score itself. A protocol, governance, software, or documentation PR without an explicitly priced scenario delivery also returns `NOT_APPLICABLE`. Explicitly excluded pre-system reference samples remain ineligible. Author identity alone is not an exclusion.
4. For an eligible scenario or mixed delivery, record scenario identity, task or claim, route, evidence level, and delivered files. Read the points rules and ledger in `docs/wanted-scenarios.md` as they stood when the source PR merged. Read the claim or proposal and review Advisories, but recompute the award; reviewer suggestions are inputs, not decisions.
5. Match every plausible task and pricing bucket. Apply decay, pair completion, proposal pricing, adapter and probe add-ons, and the documented stacking rules. Do not silently stack two ordinary task prices. If the case is genuinely ambiguous, return `NEEDS_MAINTAINER_DECISION`, ask one concrete question, and do not create a ledger change until answered.
6. Confirm whether evidence that was available was omitted. Honest `self_reported`, `not_exposed`, or confounded evidence does not reduce points by itself. If evidence that could have been supplied is missing, return `AWARD_DEFERRED` and state what must be supplied; do not append a row yet.
7. Only after the preceding checks produce an eligible, unrecorded award, append one row to both `docs/wanted-scenarios.md` and `docs/wanted-scenarios.zh-CN.md`. Include date, contributor, task, merged PR, points, claim or proposal when relevant, and enough rationale to preserve normalization and non-stacking decisions. Never edit a historical ledger row; corrections use a new offsetting row.
8. Create a work branch from current `main`, run `./scripts/verify-packages.sh` and `git diff --check`, commit only the ledger files, push the branch, and open a PR. Never push directly to `main` and never use an admin bypass to skip required PR, CI, or review gates.
9. Report the ledger commit and PR URL. After that PR is normally merged, verify that both ledger rows are present on `main` and that the worktree contains no uncommitted files created by the task.

### Points completion output

The Agent reports:

- outcome: `RECORDED`, `ALREADY_RECORDED`, `ALREADY_PENDING`, `NOT_APPLICABLE`, `AWARD_DEFERRED`, `NEEDS_MAINTAINER_DECISION`, or `LEDGER_INCONSISTENT`;
- awarded task and points, including stacking or decay rationale;
- merged source PR and contributor;
- exact English and Chinese ledger rows;
- verification results;
- ledger commit and PR URL;
- any maintainer decision still required.

For outcomes other than `RECORDED`, fields that do not apply are omitted and no commit or PR is created.

## Contract acceptance tests

After this runbook is merged, validate the minimal contract without repeating its instructions in the prompt:

1. Give an open scenario-data PR URL only. The Agent must classify it as data, preserve reviewer independence, use the data dimensions, and publish one correctly versioned verdict.
2. Give an open protocol/documentation or ledger PR URL only. The Agent must use the non-data dimensions, avoid the data evidence table, avoid claiming an automatic L1 two-review requirement, and mark points `not_applicable`.
3. Give a PR with a published REQUEST_CHANGES verdict, then have the contributor push a new head or update only the PR description. The same reviewer must leave the old verdict unchanged and post a new superseding verdict after the contributor's update; the gate must count that reviewer once.
4. Give a draft PR URL, first alone and then with an explicit instruction to review it and post a verdict. Both times the Agent must report the draft state and stop, with no comment published; the explicit instruction must not unlock a disclaimered verdict.
5. Give an eligible merged scenario PR URL that has no ledger row or pending ledger PR. The Agent must calculate once and create exactly one bilingual ledger-update PR.
6. Give the same merged scenario PR URL again while its ledger PR is open and after it is merged. The outcomes must be `ALREADY_PENDING` and `ALREADY_RECORDED`, with no duplicate row or PR.
7. Give a merged points-ledger or non-priced documentation PR URL. The outcome must be `NOT_APPLICABLE`, with no repository change.

The bootstrap prompt used to introduce this page is not evidence that the URL-only contract passes; only these post-merge tests are.

## Boundaries

- One PR URL is enough to locate the target; it is not permission to change unrelated settings, permissions, secrets, branches, issues, or other PRs.
- Review and scoring are separate actions. A review Advisory does not update the ledger, and a merged PR does not receive points until the bilingual ledger update is merged.
- A ledger PR records another PR's award and is never itself a new scoring target. Idempotency is checked before every write.
- The maintainer performs the formal GitHub approval, final merge, points adjudication, and any private-evidence check. Agents provide review comments and repository changes through normal PRs.
