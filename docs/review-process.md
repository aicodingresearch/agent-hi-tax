# How pull requests are reviewed

**English** | [中文](review-process.zh-CN.md)

> Automated checks decide whether a package is well-formed. Review decides whether it is honest.

This page describes what happens to a data Pull Request after it is opened: who reads it, what they are asked to look at, how disagreement is resolved, and what a review comment must contain. The rules for collecting and submitting evidence stay in [CONTRIBUTING](../CONTRIBUTING.md); this page only covers the review.

For the one-PR-URL Agent workflow that routes both review and post-merge points submission, see [Agent entry point for PR review and points](agent-review-and-scoring.md).

## What review covers

Automated verification already runs on every PR. `./scripts/verify-packages.sh` checks package structure, the arithmetic of derived fields, `SHA256SUMS`, and textual privacy clues; a PR that touches the generated indexes is additionally held to `./scripts/verify-all.sh`, which requires them to match the data exactly — see [the pre-submission section of CONTRIBUTING](../CONTRIBUTING.md#submitting-a-pull-request). Reviewers do not repeat that work, and a green check is not an opinion about the submission.

Review exists for the four things a script cannot do:

1. **Redaction.** Every published image is looked at, one by one, at full size. No account email address, account ID, session or resume identifier, username, hostname, or full home path may remain visible, and masking must be opaque rather than blurred. A file name or a thumbnail is not a substitute for opening the image.
2. **Cross-evidence consistency.** The numbers and the ordering must agree across the screenshot, `RESULTS.csv`, `manifest.yaml`, and the sanitized event records. Usage buckets, timestamps, the attempt count, model, and effort should tell the same story wherever they appear.
3. **Protocol conformance.** Scenario identity holds across the valid attempts; the [field-level states](../CONTRIBUTING.md#field-level-states) — `not_exposed`, `not_provided`, `self_reported`, `conflicted`, and the rest — are used honestly rather than as a way to look complete; deviations and confounders are registered instead of quietly dropped; the directory name and `scenario.id` follow the [GitHub-handle suffix rule](../CONTRIBUTING.md#run-package-layout).
4. **Restraint of claims.** The package README and the PR text stay within what the evidence supports. A single scenario is one observation of one execution stack; it is not a statement about a model, a vendor, or a price.

## Review levels

| Level | When it applies | Configuration and decision |
| --- | --- | --- |
| **L1 — default** | Ordinary data PRs | At least 2 independent reviews (human, or human-directed with AI assistance), plus the maintainer's final read. Two APPROVE verdicts: the maintainer merges and awards points. Any REQUEST_CHANGES: the contributor revises and the reviewers look again. |
| **L2 — escalated** | The two verdicts disagree; a ★★★ first sample of a new product with no reference package to compare against; any package that carries a `private_evidence` upgrade | A third review is added, from a different model family or a different person than the first two. Two out of three carries the decision, and the maintainer executes it. |
| **L3 — maintainer only** | Changes to protocol files (`prompts/`, `templates/`, `scripts/`, and the rest of the paths called out in [CODEOWNERS](../.github/CODEOWNERS)); scoring disputes; suspected dishonesty; security incidents | No majority vote. The maintainer decides, and writes the decision back onto the relevant list under the existing meta-rule that pricing and normalization calls are recorded where they were made. |

## Decision rules

- **"Disagreement" means the Verdict lines differ.** Two REQUEST_CHANGES verdicts that raise entirely different findings are not a disagreement — they are two lists, and the contributor is expected to address both.
- **Every review names the head commit it was performed at.** After a force-push or a new commit, the affected reviews are redone against the new head; a verdict written against an older tree does not carry forward.
- **A draft PR is not reviewed.** Review starts when the contributor marks the PR Ready for review, and an explicit request to review a draft does not change that — a verdict on a moving head is scheduled to be redone, and [CONTRIBUTING](../CONTRIBUTING.md#submitting-a-pull-request) puts the automated verification and the screenshot re-check before that transition, not after it. Looking at a draft and leaving ordinary comments is welcome; it is a pre-review consultation, not a verdict, and it counts toward no gate.
- **Re-review appends; it does not rewrite verdict history.** After a contributor responds to a verdict by pushing commits or updating the PR description, leave the earlier verdict comment unchanged and post a new structured verdict after the contributor's update, even when the head SHA did not change. The follow-up links the earlier comment in `Supersedes`, states what was re-reviewed, and discloses that the preceding discussion was read. It replaces that reviewer's earlier verdict for the current gate, but it is still the same review and does not count as another independent L1 review. Editing an earlier verdict is limited to typo, link, or formatting corrections that do not change its decision or findings; an explicit maintainer-directed historical correction must retain an edit note.
- **Target response time is about 3 working days**, the same as the acknowledgement window in [SECURITY.md](../SECURITY.md).

## Reviewer independence

The reviews are dispatched sequentially. The first reviewer publishes a current-head verdict before the second reviewer is selected. A first `REQUEST_CHANGES` stays with that reviewer until re-review; a privacy verdict stops the flow. Only a first `APPROVE` causes one reviewer from a different model family to be invited for the second review.

Sequential dispatch does not relax independence. The second reviewer must work from the diff and files without reading the first reviewer's findings. A review written after seeing another reviewer's findings must disclose that, and it does not count toward the two-independent-review minimum. An explicitly requested same-reviewer re-review may read that reviewer's earlier verdict and the contributor's subsequent response because it is validating a revision, not creating another independent review; the follow-up must disclose this boundary.

Reviews performed with AI assistance must come from **different model families**. Two reviews from the same family count as one, and the second one does not satisfy the L1 minimum.

## The verdict comment

Reviews are posted as a structured comment on the PR, in this shape:

```text
Reviewed under: docs/review-process.md @ <template commit>

## Review verdict: APPROVE | REQUEST_CHANGES | PRIVACY-CONCERN-RAISED-PRIVATELY

Reviewed at head: <commit SHA>
Reviewer: <human name, or agent product + model + reasoning effort>
Independence key: human:<github-login> | agent:<model-family>
Date: <YYYY-MM-DD>
Supersedes (re-review only): <prior verdict comment URL>

| Dimension | Result |
| --- | --- |
| Redaction (published images eyeballed one by one) | pass / issues |
| Cross-evidence consistency (image ↔ CSV ↔ manifest ↔ events) | pass / issues |
| Protocol conformance (identity, field states, deviations) | pass / issues |
| Restraint of claims | pass / issues |

Blocking findings: <one per line, as file:line; write "none" if there are none>
Non-blocking suggestions: <may be empty>
Could not verify: <required; see below>
Advisory (optional): <task and point-value suggestions, for the maintainer's reference only>
```

`<template commit>` is the short hash of the last commit that touched this page, read on the PR's base branch:

```sh
git log -1 --format=%h -- docs/review-process.md
```

Six requirements are not optional:

- **The first line of a review comment must declare the template version it was written under**, identified by that commit. Later revisions of this page are not retroactive: each review is judged against the version it declared, unless the maintainer explicitly asks for a re-review under the current one.
- **Do not read any review already posted on the PR before publishing your own; reach your conclusion independently.** Review from the diff and the files themselves, without opening the PR conversation page. If you did see another reviewer's findings, disclose it in your comment: that review no longer counts toward the two-independent-review minimum and stands as reference only.
- **A re-review posts a new comment and names the verdict it supersedes.** Do not edit an earlier verdict into a different decision after the contributor has acted on it. Keep the old comment as the visible reason for the contributor's response, and use the new comment as that reviewer's current verdict.
- **A review performed with AI assistance must name the agent product, the exact model, and the reasoning effort.** When the product does not expose the model or the effort, write `not exposed` — do not guess. This is the same honesty rule the repository applies to evidence fields: an unavailable value is recorded as unavailable, never inferred.
- **The independence key is stable across re-reviews and deliberately coarser than the exact Reviewer line.** A human-only review uses `human:<github-login>`. An AI-assisted review uses a model-family key such as `agent:openai-gpt`, `agent:anthropic-claude`, `agent:zhipu-glm`, or `agent:google-gemini`; model versions and effort levels in the same family keep the same key. If the model family is not exposed, use `agent:not-exposed`. Two APPROVE verdicts count separately only when both the GitHub reviewers and their keys differ.
- **"Could not verify" is a required line.** State the boundary of what your review could actually establish. At minimum it includes the class of claim that only the contributor can check — for example, that the published images correspond to the private originals they were masked from, or that no additional attempts were discarded before submission. A review that silently omits its own limits overstates itself, which is the same failure this project asks contributors to avoid.

## The privacy exception

If you suspect that a **published** file leaks a credential, an email address, a session or resume identifier, a private path, or private content, do not describe the detail in the PR. Do not quote the value, do not point at the pixel, and do not open a public issue.

Post a single line instead:

```text
Privacy concern raised through the private channel.
```

Use `PRIVACY-CONCERN-RAISED-PRIVATELY` as the verdict, and send the detail through the private reporting process in [SECURITY.md](../SECURITY.md). The rest of your review can be published normally. A public description of where a leak sits is itself a disclosure, and this holds whether the mistake is a contributor's, another reviewer's, or the maintainer's.

## What reviewers do not decide

Reviews are input, not adjudication. The maintainer performs the merge, awards and records points, normalizes decay buckets, updates the ledger, and checks any `private_evidence` originals against their registered hashes. A reviewer may put a point-value opinion in the Advisory line; it carries no weight of its own.

AI-assisted reviews are posted as structured comments only. They do not use GitHub's formal **Approve** or **Request changes** buttons — those record a named person taking responsibility for a judgement, and an agent is not one.
