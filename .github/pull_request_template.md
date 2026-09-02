<!-- 中文贡献者：可以用中文填写本模板；规则见 CONTRIBUTING.zh-CN.md -->
## Related issue / 关联 Issue

Closes #

<!-- Replace the line above with the claim issue number, for example: Closes #123. GitHub will close the issue when this PR is merged. 请填写认领 Issue 编号，例如：Closes #123；本 PR 合并后 GitHub 会自动关闭该 Issue。 -->

## Scenario

- Scenario ID:
- Scenario directory: `runs/YYYY-MM-DD/<scenario-id>/`
- Agent / version:
- Model / effort:
- Subscription or billing channel:
- Route / harness profile:

## Attempts

- Planned attempts:
- Valid attempts:
- Invalid, error, or timed-out attempts, with reasons:

## Evidence

- Package-level evidence: Level A / B / C
- Visual evidence: public / private_evidence / not_provided
- Fields that are not exposed, not provided, self-reported, or conflicted:
- Did original images stay outside the Git repository at all times: yes / no

## Protocol deviations and confounders

Describe extra commands, permission or footer mode changes, MCP / plugin / hook differences, shared-quota contamination, and any difference that cannot be attributed to the model. Write "none" if there are none.

## Verification output

Paste the complete output of the following commands:

```text
./scripts/verify-run-package.sh runs/YYYY-MM-DD/<scenario-id>
./scripts/verify-packages.sh
```

## Pre-submission checklist

- [ ] This PR contains exactly one scenario and all of its attempts.
- [ ] The related claim issue is linked above with `Closes #<issue-number>`.
- [ ] There are at least 3 valid independent runs, and they are not parallel, resumed, or cherry-picked minimums.
- [ ] The prompt, Agent version, model, effort, route, permission mode, and harness are consistent across the valid attempts.
- [ ] Exactly one copy of scenario-level environment evidence is kept, with the reply and usage kept separately for each attempt.
- [ ] Native usage fields and derived formulas are both documented, and cached input is not double-counted.
- [ ] Invalid and anomalous attempts have not been silently deleted.
- [ ] Public text and images contain no credentials, email addresses, account IDs, session IDs, resume commands, usernames, hostnames, absolute home paths, or private content.
- [ ] Original visual images have not entered public Git history; redacted images have been visually inspected one by one.
- [ ] `private_evidence` is used only for originals a maintainer has actually verified.
- [ ] `SHA256SUMS` was generated after all public files were finalized.
- [ ] This PR leaves the generated `RESULTS.md` and `RESULTS.zh-CN.md` untouched; they are rebuilt on `main` after the merge.
- [ ] `./scripts/verify-packages.sh` has passed.
- [ ] I am entitled to publish this evidence: it contains no private repository, internal tool, or third-party account material.
- [ ] I agree that this contribution is published under the repository's licenses (CC BY 4.0 for data and documentation, Apache-2.0 for software).

<!-- Your PR will receive at least two independent reviews; see docs/review-process.md for the process and the verdict template. 本 PR 将收到至少两份独立评审，流程与意见模板见 docs/review-process.zh-CN.md -->

<!-- If you discover leaked credentials, emails, session IDs, or private paths in already-published evidence, do not report them here. Follow SECURITY.md and report privately. -->
<!-- 如果你在已公开的证据中发现凭据、邮箱、session ID 或私有路径泄露，不要在这里报告，请按 SECURITY.md 私下报告。 -->
