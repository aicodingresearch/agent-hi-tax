#!/bin/sh
# Apply branch protection to main.
#
# GitHub only allows branch protection on a public repository, or on a private
# repository under a paid plan. This repository is currently private under a
# free organization plan, so the rules below cannot be applied yet: the API
# answers 403 "Upgrade to GitHub Pro or make this repository public".
#
# Run this once, immediately after the repository is made public:
#
#     ./scripts/apply-repo-protection.sh
#
# Requires the gh CLI, authenticated with admin rights on the repository.
set -eu

repo=${REPO:-aicodingresearch/agent-hi-tax}
branch=${BRANCH:-main}

echo "applying branch protection: $repo@$branch"

# - one approving review, dismissed when new commits land
# - the data verification workflow must pass, on an up-to-date branch
# - conversations must be resolved (redaction questions do not get lost)
# - force pushes and deletions are blocked, including for administrators
gh api -X PUT "repos/$repo/branches/$branch/protection" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["verify"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "required_linear_history": false,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON

# Private vulnerability reporting: the intake channel named in SECURITY.md.
echo "enabling private vulnerability reporting"
gh api -X PUT "repos/$repo/private-vulnerability-reporting" || \
  echo "  (not available yet — enable it under Settings > Security after going public)" >&2

# Secret scanning with push protection: blocks a credential before it lands.
echo "enabling secret scanning and push protection"
gh api -X PATCH "repos/$repo" --input - <<'JSON' || \
  echo "  (not available yet — enable it under Settings > Security after going public)" >&2
{
  "security_and_analysis": {
    "secret_scanning": {"status": "enabled"},
    "secret_scanning_push_protection": {"status": "enabled"}
  }
}
JSON

echo "done; verify at https://github.com/$repo/settings/branches"
